from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, List, Optional
import os
import tempfile

# Third-party parser dependency is isolated to this adapter module.
import tmdlparser

from src.powerbi.entities.model import Model
from src.powerbi.entities.table import Table, Column, Measure, CalculatedColumn
from src.powerbi.entities.identity import Identity


from src.powerbi.entities.common import Provenance, Range, Position


class DiagnosticLevel(Enum):
    INFO = auto()
    WARNING = auto()
    ERROR = auto()


@dataclass
class Diagnostic:
    level: DiagnosticLevel
    message: str
    file: Optional[str] = None
    range: Optional[Any] = None
    construct: Optional[str] = None
    context: Optional[str] = None


class TMDLParsingError(Exception):
    """Fatal TMDL parsing error."""

    def __init__(
        self,
        message: str,
        file: Optional[str] = None,
        line: Optional[int] = None,
        col: Optional[int] = None,
    ):
        super().__init__(message)
        self.file = file
        self.line = line
        self.col = col


@dataclass
class ParsedFragment:
    """Adapter-internal intermediate representation."""

    data: Any
    diagnostics: List[Diagnostic] = field(default_factory=list)


class TMDLParserAdapter:
    """Isolates the third-party TMDL parser from the canonical model."""

    def __init__(self):
        self._parser = tmdlparser.TMLDParser()

    def parse_semantic_model(
        self, model_directory: str
    ) -> tuple[Model, List[Diagnostic]]:
        """Parse a SemanticModel definition directory and return the
        canonical Model plus all non-fatal diagnostics."""
        
        exclude_dirs = {".platform", ".git", "__pycache__", ".venv"}
        
        tmdl_files = []
        for root, dirs, files in os.walk(model_directory):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith(".tmdl"):
                    tmdl_files.append(os.path.join(root, file))
        
        # Sort files to ensure deterministic order as per contract
        tmdl_files.sort()
        
        model = Model(id="model:semantic_model", name="SemanticModel")
        diagnostics = []
        
        for file in tmdl_files:
            try:
                parsed_data = self._parser.parse_file(file)
                self._map_to_canonical(parsed_data, model, file)
            except Exception as exc:
                # Handle non-fatal parsing failures, for now just collect diagnostic
                diagnostics.append(Diagnostic(level=DiagnosticLevel.ERROR, message=str(exc), file=file))
        
        return model, diagnostics

    def _map_to_canonical(self, parsed_data: List[Any], model: Model, source_file: str):
        for item in parsed_data:
            if hasattr(item, 'element'):
                element = item.element
                if element.startswith('table '):
                    self._map_table(item, model, source_file)

    def _map_table(self, item: Any, model: Model, source_file: str):
        parts = item.element.split(maxsplit=1)
        if len(parts) < 2:
            return
        
        raw_name = parts[1]
        table_name = self._decode_identifier(raw_name)
        table_id = Identity.table_id(table_name)
        
        # Range is not available from current parser, so we omit it per contract
        provenance = Provenance(source_type='TMDL', file=source_file, range=None)
        
        table = Table(id=table_id, name=table_name, provenance=provenance)
        
        for prop in item.properties:
            if not hasattr(prop, 'element'):
                continue
                
            element = prop.element
            if element.startswith('column '):
                self._map_column(prop, table, source_file)
            elif element.startswith('measure '):
                self._map_measure(prop, table, source_file)
            elif element.startswith('lineageTag: '):
                table.lineage_tag = element.split(': ', 1)[1].strip()
        
        model.tables.append(table)

    def _map_column(self, prop: Any, table: Table, source_file: str):
        # column Name [= Expression]
        element = prop.element[len('column '):].strip()
        
        provenance = Provenance(source_type='TMDL', file=source_file, range=None)
        
        if ' = ' in element:
            name_part, expression = element.split(' = ', 1)
            name = self._decode_identifier(name_part)
            column = CalculatedColumn(
                id=Identity.column_id(table.id, name),
                name=name,
                expression=expression,
                data_type='unknown', # Will be updated from properties
                is_hidden=False,
                provenance=provenance
            )
        else:
            name = self._decode_identifier(element)
            column = Column(
                id=Identity.column_id(table.id, name),
                name=name,
                data_type='unknown',
                is_hidden=False,
                provenance=provenance
            )
            
        for sub_prop in prop.properties:
            if isinstance(sub_prop, str):
                line = sub_prop.strip()
                if line.startswith('dataType: '):
                    column.data_type = line.split(': ', 1)[1].strip()
                elif line == 'isHidden':
                    column.is_hidden = True
                elif line.startswith('formatString: '):
                    column.format_string = line.split(': ', 1)[1].strip()
                elif line.startswith('summarizeBy: '):
                    column.summarize_by = line.split(': ', 1)[1].strip()
                elif line.startswith('sourceColumn: '):
                    column.source_column = self._decode_identifier(line.split(': ', 1)[1].strip())
                elif line.startswith('lineageTag: '):
                    column.lineage_tag = line.split(': ', 1)[1].strip()
        
        table.columns.append(column)

    def _map_measure(self, prop: Any, table: Table, source_file: str):
        # measure Name = Expression
        element = prop.element[len('measure '):].strip()
        
        if ' = ' in element:
            name_part, expression = element.split(' = ', 1)
        else:
            # Fallback if no '=' found, though measures usually have it
            name_part = element
            expression = ''
            
        name = self._decode_identifier(name_part)
        
        provenance = Provenance(source_type='TMDL', file=source_file, range=None)
        
        measure = Measure(
            id=Identity.measure_id(table.id, name),
            name=name,
            expression=expression,
            doc_comment=prop.description if hasattr(prop, 'description') and prop.description else None,
            provenance=provenance
        )
        
        for sub_prop in prop.properties:
            if isinstance(sub_prop, str):
                line = sub_prop.strip()
                if line.startswith('formatString: '):
                    measure.format_string = line.split(': ', 1)[1].strip()
                elif line.startswith('displayFolder: '):
                    measure.display_folder = line.split(': ', 1)[1].strip()
                elif line.startswith('lineageTag: '):
                    measure.lineage_tag = line.split(': ', 1)[1].strip()
        
        table.measures.append(measure)

    def _decode_identifier(self, identifier: str) -> str:
        """Decodes TMDL identifier (removes single quotes if present)."""
        identifier = identifier.strip()
        if identifier.startswith("'") and identifier.endswith("'"):
            return identifier[1:-1].replace("''", "'")
        return identifier

    def parse_tmdl_fragment(
        self,
        fragment: str,
        source_file: str | None = None,
    ) -> ParsedFragment:
        """Parse a TMDL fragment through the isolated third-party parser."""

        tmp_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".tmdl",
                delete=False,
                encoding="utf-8",
            ) as tmp:
                tmp.write(fragment)
                tmp_path = tmp.name

            parsed_data = self._parser.parse_file(tmp_path)

            return ParsedFragment(
                data=parsed_data,
                diagnostics=[],
            )

        except Exception as exc:
            raise TMDLParsingError(
                str(exc),
                file=source_file,
            ) from exc

        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
