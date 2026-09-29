from pathlib import Path
from typing import NamedTuple, Union
from lxml import etree

class LoaderError(Exception):
    """Base class for loader exceptions."""
    pass

class FileMissingError(LoaderError):
    """Raised when the file does not exist."""
    pass

class NotAFileError(LoaderError):
    """Raised when the path is not a file."""
    pass

class InvalidExtensionError(LoaderError):
    """Raised when the file is not a .twb."""
    pass

class MalformedXMLError(LoaderError):
    """Raised when XML parsing fails due to syntax errors."""
    pass

class XMLReadError(LoaderError):
    """Raised when XML loading fails due to I/O or filesystem errors."""
    pass

class LoaderResult(NamedTuple):
    """Container for loaded workbook representations."""
    xml_tree: etree._ElementTree

def load_workbook(file_path: Union[str, Path]) -> LoaderResult:
    """
    Loads a Tableau workbook (.twb) using direct XML parsing.
    
    Args:
        file_path: Path to the .twb file.
        
    Returns:
        LoaderResult containing the XML tree.
        
    Raises:
        FileMissingError: If file doesn't exist.
        NotAFileError: If path exists but isn't a file.
        InvalidExtensionError: If extension isn't .twb.
        XMLReadError: If XML reading fails (I/O).
        MalformedXMLError: If XML parsing fails (syntax).
    """
    path = Path(file_path)
    
    # 1. Path validation
    if not path.exists():
        raise FileMissingError(f"File not found: {path}")
    if not path.is_file():
        raise NotAFileError(f"Path is not a file: {path}")
    if path.suffix.lower() != ".twb":
        raise InvalidExtensionError(f"Invalid extension: {path.suffix} (expected .twb)")
        
    # 2. Direct XML Loading
    try:
        # We use lxml to parse the authoritative XML
        xml_tree = etree.parse(str(path))
    except (IOError, OSError) as e:
        raise XMLReadError(f"Failed to read XML file: {e}")
    except etree.XMLSyntaxError as e:
        raise MalformedXMLError(f"Failed to parse XML syntax: {e}")
        
    return LoaderResult(xml_tree=xml_tree)
