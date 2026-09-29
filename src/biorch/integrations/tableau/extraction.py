from typing import Any, List
from lxml import etree
from .entities import SourceEvidence, EvidenceType, DerivationStatus
from .loader import LoaderResult

def _get_element_attributes(element: etree._Element) -> dict:
    """Recursively extract attributes and nested text from an XML element."""
    attrs = dict(element.attrib)
    for child in element:
        child_data = _get_element_attributes(child)
        # If the child has no attributes and no children, just take its text
        if not child_data:
            val = child.text if child.text is not None else ""
        else:
            # Merge text if present
            if child.text and child.text.strip():
                child_data["#text"] = child.text
            val = child_data
        
        if child.tag in attrs:
            if not isinstance(attrs[child.tag], list):
                attrs[child.tag] = [attrs[child.tag]]
            attrs[child.tag].append(val)
        else:
            attrs[child.tag] = val
    return attrs

def extract_evidence(file_path: str, loader_result: LoaderResult) -> List[SourceEvidence]:
    """
    Extracts source evidence from a Tableau workbook across six authorized categories.
    
    Categories:
    1. datasources
    2. relations
    3. metadata-records
    4. fields (represented as 'column' in source_structure)
    5. column-instances
    6. worksheets
    """
    evidence_list: List[SourceEvidence] = []
    tree = loader_result.xml_tree
    root = tree.getroot()
    
    # A. DATASOURCES
    # Extract datasource observations directly from the authoritative XML structure.
    for ds_node in root.xpath("/workbook/datasources/datasource"):
        evidence_list.append(SourceEvidence(
            source_file=file_path,
            representation="xml",
            source_structure="datasource",
            source_locator=tree.getpath(ds_node),
            source_attributes=_get_element_attributes(ds_node),
            evidence_type=EvidenceType.DATASOURCE,
            derivation_status=DerivationStatus.DIRECT
        ))
        
    # B. RELATIONS
    # Extract raw <relation> observations from the TWB/XML.
    # We search globally for relation tags to ensure we miss nothing.
    for rel in root.xpath("//relation"):
        evidence_list.append(SourceEvidence(
            source_file=file_path,
            representation="xml",
            source_structure="relation",
            source_locator=tree.getpath(rel),
            source_attributes=_get_element_attributes(rel),
            evidence_type=EvidenceType.RELATION,
            derivation_status=DerivationStatus.DIRECT
        ))
        
    # C. METADATA-RECORDS
    # Extract raw metadata-record observations from the authoritative XML.
    for mr in root.xpath("//metadata-record"):
        evidence_list.append(SourceEvidence(
            source_file=file_path,
            representation="xml",
            source_structure="metadata-record",
            source_locator=tree.getpath(mr),
            source_attributes=_get_element_attributes(mr),
            evidence_type=EvidenceType.METADATA_RECORD,
            derivation_status=DerivationStatus.DIRECT
        ))
        
    # D. FIELDS (XML <column> nodes under <datasource>)
    # Use direct XML extraction for fields to ensure evidence-first provenance.
    for ds_node in root.xpath("/workbook/datasources/datasource"):
        for col in ds_node.xpath("./column"):
            col_id = col.get("name")
            if not col_id:
                continue
            evidence_list.append(SourceEvidence(
                source_file=file_path,
                representation="xml",
                source_structure="column",
                source_locator=tree.getpath(col),
                source_attributes=_get_element_attributes(col),
                evidence_type=EvidenceType.UNKNOWN, # FIELD missing in Step 3.1 EvidenceType
                derivation_status=DerivationStatus.DIRECT
            ))
        
    # E. COLUMN-INSTANCES
    # Discover all column-instances across all possible locations (Datasources, Worksheets, Dashboards, etc.)
    # We use tree.xpath("//column-instance") to be exhaustive as requested.
    for ci in root.xpath("//column-instance"):
        attributes = _get_element_attributes(ci)
        dependency = ci.getparent()
        if dependency is not None and dependency.tag == "datasource-dependencies":
            datasource_name = dependency.get("datasource")
            if datasource_name:
                # This is direct XML context, retained with the occurrence so a
                # worksheet CI can be scoped to its canonical datasource.
                attributes["datasource"] = datasource_name
        evidence_list.append(SourceEvidence(
            source_file=file_path,
            representation="xml",
            source_structure="column-instance",
            source_locator=tree.getpath(ci),
            source_attributes=attributes,
            evidence_type=EvidenceType.COLUMN_INSTANCE,
            derivation_status=DerivationStatus.DIRECT
        ))
        
    # F. WORKSHEETS
    # Extract worksheet observations from the authoritative XML representation.
    for ws in root.xpath("/workbook/worksheets/worksheet"):
        evidence_list.append(SourceEvidence(
            source_file=file_path,
            representation="xml",
            source_structure="worksheet",
            source_locator=tree.getpath(ws),
            source_attributes=_get_element_attributes(ws),
            evidence_type=EvidenceType.WORKSHEET,
            derivation_status=DerivationStatus.DIRECT
        ))
        
    return evidence_list
