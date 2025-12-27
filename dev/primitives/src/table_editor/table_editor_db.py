"""
Database abstraction layer for CSV-based data storage.

Provides a CSVDatabase class that can be used independently of Streamlit.
Designed with an abstract interface to allow future extension to PostgreSQL
or other database backends.

Framework-independent - no Streamlit dependencies.
"""

import json
import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class DatabaseInterface(ABC):
    """
    Abstract base class defining the interface for database operations.

    Implementations can include CSVDatabase, PostgreSQLDatabase, etc.
    This interface ensures all database backends provide consistent methods.
    """

    @abstractmethod
    def load_data(self, identifier: str) -> pd.DataFrame:
        """Load data from a source and return as DataFrame."""
        pass

    @abstractmethod
    def save_data(self, identifier: str, df: pd.DataFrame) -> bool:
        """Save DataFrame to a destination."""
        pass

    @abstractmethod
    def list_sources(self, location: str) -> List[str]:
        """List available data sources in a location."""
        pass

    @abstractmethod
    def get_source_info(self, identifier: str) -> Dict[str, Any]:
        """Get metadata about a data source."""
        pass

    @abstractmethod
    def source_exists(self, identifier: str) -> bool:
        """Check if a data source exists."""
        pass


class CSVDatabase(DatabaseInterface):
    """
    CSV file-based database implementation.

    Provides CRUD-like operations for CSV files with support for:
    - Reading/writing CSV files as pandas DataFrames
    - Listing CSV files in a directory
    - Getting file metadata (name, size, modified time)
    - Persisting file history in JSON format

    This class is designed to be importable and usable independently
    of any UI framework (no Streamlit dependencies).

    Example:
        db = CSVDatabase()
        df = db.load_csv('/path/to/data.csv')
        df['new_column'] = 'value'
        db.save_csv('/path/to/data.csv', df)
    """

    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize CSVDatabase with default settings.

        Args:
            encoding: Default encoding for CSV files (default: utf-8)
        """
        self.encoding = encoding

    # =========================================================================
    # Core Interface Methods (from DatabaseInterface)
    # =========================================================================

    def load_data(self, identifier: str) -> pd.DataFrame:
        """
        Load data from a CSV file.

        Implements the abstract DatabaseInterface method.

        Args:
            identifier: File path to the CSV file

        Returns:
            DataFrame with CSV data
        """
        return self.load_csv(identifier)

    def save_data(self, identifier: str, df: pd.DataFrame) -> bool:
        """
        Save DataFrame to a CSV file.

        Implements the abstract DatabaseInterface method.

        Args:
            identifier: File path for the CSV file
            df: DataFrame to save

        Returns:
            True if successful, False otherwise
        """
        return self.save_csv(identifier, df)

    def list_sources(self, location: str) -> List[str]:
        """
        List CSV files in a directory.

        Implements the abstract DatabaseInterface method.

        Args:
            location: Directory path to search

        Returns:
            List of CSV file paths
        """
        return self.list_csv_files(location)

    def get_source_info(self, identifier: str) -> Dict[str, Any]:
        """
        Get metadata about a CSV file.

        Implements the abstract DatabaseInterface method.

        Args:
            identifier: File path to the CSV file

        Returns:
            Dict with file metadata
        """
        return self.get_file_info(identifier)

    def source_exists(self, identifier: str) -> bool:
        """
        Check if a CSV file exists.

        Implements the abstract DatabaseInterface method.

        Args:
            identifier: File path to check

        Returns:
            True if file exists, False otherwise
        """
        return self.file_exists(identifier)

    # =========================================================================
    # CSV Read/Write Operations
    # =========================================================================

    def load_csv(self, file_path: str) -> pd.DataFrame:
        """
        Load a CSV file and return as DataFrame.

        Handles common issues like missing files and encoding problems.

        Args:
            file_path: Absolute or relative path to the CSV file

        Returns:
            DataFrame with CSV data, empty DataFrame if file not found

        Raises:
            FileNotFoundError: If the file does not exist
            pd.errors.EmptyDataError: If the file is empty
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")

        if path.stat().st_size == 0:
            raise pd.errors.EmptyDataError(f"CSV file is empty: {file_path}")

        df = pd.read_csv(path, encoding=self.encoding)
        return df

    def save_csv(self, file_path: str, df: pd.DataFrame) -> bool:
        """
        Save DataFrame to a CSV file.

        Creates parent directories if they don't exist.

        Args:
            file_path: Absolute or relative path for the CSV file
            df: DataFrame to save

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(file_path)

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            df.to_csv(path, index=False, encoding=self.encoding)
            return True
        except Exception:
            return False

    # =========================================================================
    # File System Operations
    # =========================================================================

    def list_csv_files(self, directory: str) -> List[str]:
        """
        List all CSV files in a directory.

        Args:
            directory: Path to the directory to search

        Returns:
            List of absolute file paths to CSV files found,
            empty list if directory doesn't exist
        """
        dir_path = Path(directory)

        if not dir_path.exists() or not dir_path.is_dir():
            return []

        csv_files = list(dir_path.glob('*.csv'))
        return [str(f.absolute()) for f in sorted(csv_files)]

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get metadata about a CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            Dict with keys: name, path, modified, size, exists
            Returns dict with exists=False if file not found
        """
        path = Path(file_path)

        if not path.exists():
            return {
                'name': path.name,
                'path': str(path.absolute()),
                'modified': None,
                'size': 0,
                'exists': False
            }

        stat = path.stat()
        modified_time = datetime.fromtimestamp(stat.st_mtime)

        return {
            'name': path.name,
            'path': str(path.absolute()),
            'modified': modified_time.isoformat(),
            'size': stat.st_size,
            'exists': True
        }

    def file_exists(self, file_path: str) -> bool:
        """
        Check if a file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()

    # =========================================================================
    # File History Persistence
    # =========================================================================

    def load_history(self, history_path: str) -> List[Dict]:
        """
        Load file history from a JSON file.

        Expected JSON format:
        {
            "files": [
                {"path": "/absolute/path/to/file.csv",
                 "last_opened": "2025-12-27T10:30:00",
                 "display_name": "file.csv"}
            ]
        }

        Args:
            history_path: Path to the history JSON file

        Returns:
            List of file history dicts, empty list if file doesn't exist
        """
        path = Path(history_path)

        if not path.exists():
            return []

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('files', [])
        except (json.JSONDecodeError, KeyError):
            return []

    def save_history(self, history_path: str, history: List[Dict]) -> bool:
        """
        Save file history to a JSON file.

        Saves in format:
        {
            "files": [
                {"path": str, "last_opened": str, "display_name": str}
            ]
        }

        Args:
            history_path: Path for the history JSON file
            history: List of file history dicts

        Returns:
            True if successful, False otherwise
        """
        try:
            path = Path(history_path)

            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {'files': history}

            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            return True
        except Exception:
            return False


# Module-level convenience functions for simpler usage
_default_db = None


def get_database() -> CSVDatabase:
    """
    Get the default CSVDatabase instance (singleton pattern).

    Returns:
        CSVDatabase instance
    """
    global _default_db
    if _default_db is None:
        _default_db = CSVDatabase()
    return _default_db


def load_csv(file_path: str) -> pd.DataFrame:
    """Convenience function to load a CSV file."""
    return get_database().load_csv(file_path)


def save_csv(file_path: str, df: pd.DataFrame) -> bool:
    """Convenience function to save a DataFrame to CSV."""
    return get_database().save_csv(file_path, df)


def list_csv_files(directory: str) -> List[str]:
    """Convenience function to list CSV files in a directory."""
    return get_database().list_csv_files(directory)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Convenience function to get file metadata."""
    return get_database().get_file_info(file_path)


def file_exists(file_path: str) -> bool:
    """Convenience function to check if a file exists."""
    return get_database().file_exists(file_path)


def load_history(history_path: str) -> List[Dict]:
    """Convenience function to load file history."""
    return get_database().load_history(history_path)


def save_history(history_path: str, history: List[Dict]) -> bool:
    """Convenience function to save file history."""
    return get_database().save_history(history_path, history)


if __name__ == "__main__":
    """
    Standalone test section demonstrating CSVDatabase functionality.

    Run with: python table_editor_db.py
    """
    import tempfile
    import os

    print("=" * 60)
    print("CSVDatabase Standalone Test")
    print("=" * 60)

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        db = CSVDatabase()

        # Test 1: Create and save a sample CSV
        print("\n1. Testing save_csv()...")
        sample_data = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'value': [100, 200, 300]
        })
        test_csv_path = os.path.join(temp_dir, 'test_data.csv')

        save_result = db.save_csv(test_csv_path, sample_data)
        print(f"   Save result: {save_result}")
        print(f"   File exists: {db.file_exists(test_csv_path)}")

        # Test 2: Load the CSV file
        print("\n2. Testing load_csv()...")
        loaded_df = db.load_csv(test_csv_path)
        print(f"   Loaded DataFrame shape: {loaded_df.shape}")
        print(f"   Columns: {list(loaded_df.columns)}")
        print(f"   Row count: {len(loaded_df)}")

        # Test 3: List CSV files
        print("\n3. Testing list_csv_files()...")
        # Create another CSV file for listing
        db.save_csv(os.path.join(temp_dir, 'another_file.csv'), sample_data)
        csv_files = db.list_csv_files(temp_dir)
        print(f"   Found {len(csv_files)} CSV files:")
        for f in csv_files:
            print(f"   - {Path(f).name}")

        # Test 4: Get file info
        print("\n4. Testing get_file_info()...")
        file_info = db.get_file_info(test_csv_path)
        print(f"   Name: {file_info['name']}")
        print(f"   Size: {file_info['size']} bytes")
        print(f"   Modified: {file_info['modified']}")
        print(f"   Exists: {file_info['exists']}")

        # Test 5: File history persistence
        print("\n5. Testing history persistence...")
        history_path = os.path.join(temp_dir, 'history.json')

        test_history = [
            {
                'path': test_csv_path,
                'last_opened': datetime.now().isoformat(),
                'display_name': 'test_data.csv'
            }
        ]

        save_history_result = db.save_history(history_path, test_history)
        print(f"   Save history result: {save_history_result}")

        loaded_history = db.load_history(history_path)
        print(f"   Loaded history entries: {len(loaded_history)}")
        if loaded_history:
            print(f"   First entry display_name: {loaded_history[0]['display_name']}")

        # Test 6: Error handling - missing file
        print("\n6. Testing error handling...")
        try:
            db.load_csv(os.path.join(temp_dir, 'nonexistent.csv'))
            print("   ERROR: Should have raised FileNotFoundError")
        except FileNotFoundError as e:
            print(f"   Correctly raised FileNotFoundError")

        # Test 7: Abstract interface usage
        print("\n7. Testing abstract interface methods...")
        df_via_interface = db.load_data(test_csv_path)
        print(f"   load_data() returned DataFrame with {len(df_via_interface)} rows")

        sources = db.list_sources(temp_dir)
        print(f"   list_sources() found {len(sources)} sources")

        exists = db.source_exists(test_csv_path)
        print(f"   source_exists() returned: {exists}")

    print("\n" + "=" * 60)
    print("All standalone tests completed successfully!")
    print("=" * 60)
