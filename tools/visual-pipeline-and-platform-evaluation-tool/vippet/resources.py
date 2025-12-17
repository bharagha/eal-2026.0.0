import os
from pathlib import Path
from typing import Protocol

# Default directories for resources
DEFAULT_LABELS_DIR = "/home/dlstreamer/dlstreamer/samples/labels"
DEFAULT_MODULES_DIR = "/modules"

# Read resource paths from environment variables if set
LABELS_PATH = os.path.normpath(
    os.environ.get("LABELS_PATH", DEFAULT_LABELS_DIR)
)
MODULES_PATH = os.path.normpath(
    os.environ.get("MODULES_PATH", DEFAULT_MODULES_DIR)
)

class ResourceManager(Protocol):
    """Protocol for managing file-based resources."""
    
    def get_filename(self, path: str) -> str | None:
        """Convert absolute path to filename if exists in managed directory."""
        ...
    
    def get_path(self, filename: str) -> str | None:
        """Convert filename to absolute path if exists in managed directory."""
        ...
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists in managed directory."""
        ...


class DirectoryResourceManager:
    """Manages resources in a specific directory."""
    
    def __init__(self, directory: Path | str):
        self.directory = Path(directory)
    
    def get_filename(self, path: str) -> str | None:
        """Extract filename from path."""
        filename = Path(path).name
        return filename
    
    def get_path(self, filename: str) -> str | None:
        """Get full path if file exists in directory."""
        if self.file_exists(filename):
            return str(self.directory / filename)
        return None
    
    def file_exists(self, filename: str) -> bool:
        """Check if file exists in managed directory."""
        return (self.directory / filename).is_file()


# Singletons for different resource types
def get_labels_manager() -> ResourceManager:
    return DirectoryResourceManager(LABELS_PATH)

def get_modules_manager() -> ResourceManager:
    return DirectoryResourceManager(MODULES_PATH)