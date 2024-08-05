from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, AnyStr

from .utils import open_by_ext


class DataFormat(Enum):
    XML = 'XML'
    JSON = 'JSON'


class ImportBase:
    def __init__(self, filename_or_stream, close_file=None):
        """
        A base class for a file/stream importer class.

        By default, closes files given as filenames, and leaves streams open.

        It should implement iterator inteface for iteration over the underlying records
        """
        if isinstance(filename_or_stream, (str, Path)):
            self.file = open_by_ext(filename_or_stream)
            self.file_name = str(filename_or_stream)
            self.close_file = close_file if close_file is not None else True
        else:
            if not hasattr(filename_or_stream, "read"):
                raise TypeError("Filename or file-like required")
            self.file = filename_or_stream
            self.file_name = repr(filename_or_stream)
            self.close_file = close_file if close_file is not None else False

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.file_name!r}>"

    def __iter__(self):
        raise NotImplemented

    def __next__(self) -> 'ImporterRecord':
        raise NotImplemented

    def close(self):
        """Close the underlying file if it should be closed (and was not already)."""
        if self.close_file:
            self.file.close()
            self.file = None  # drop the ref
            self.close_file = False

    def __del__(self):
        self.close()


class ImporterRecord:
    def __init__(
        self,
        ssid: str,
        raw_data: Optional[AnyStr] = None,
        raw_data_format: DataFormat = DataFormat.XML,
        isbn: Optional[str] = None,
        doi: Optional[str] = None,
        identifiers: Optional[dict] = None,
        title: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.ssid = ssid
        self.isbn = isbn
        self.doi = doi
        self.title = title
        self.identifiers = identifiers
        self.raw_data = raw_data
        self.raw_data_format = raw_data_format
        self.timestamp = timestamp or datetime.now()


class DataImportError(ValueError):

    pass
