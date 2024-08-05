import bz2
import gzip
import logging
import lzma
import pathlib

import zstandard

log = logging.getLogger(__name__)


def open_by_ext(fname, mode="rb", level=6):
    """
    Open a given filename, transparently de/compressing it based on extension.

    Detected extensions are: `.bz2`, `.gz`, `.xz`, `.zstd`.
    Compression `level` is 0-9 and only relevant when writing.
    Only supports binary mode.
    """
    if "t" in mode:
        raise ValueError("'t'ext mode not supported")
    if "b" not in mode:
        mode += "b"
    writing = ("a" in mode) or ("w" in mode)
    fname = pathlib.Path(fname)
    if fname.suffix == ".bz2":
        return bz2.BZ2File(fname, mode, compresslevel=level)
    elif fname.suffix == ".gz":
        return gzip.GzipFile(fname, mode, compresslevel=level if writing else None)
    elif fname.suffix == ".xz":
        return lzma.LZMAFile(fname, mode, preset=level if writing else None)
    elif fname.suffix in (".zstd", ".zst"):
        if "a" in mode:
            raise ValueError("'a'ppend mode not supported for zstd")
        f = open(fname, mode)
        if writing:
            c = zstandard.ZstdCompressor(level=level)
            return c.stream_writer(f)
        else:
            d = zstandard.ZstdDecompressor()
            return d.stream_reader(f)
    else:
        return open(fname, mode)
