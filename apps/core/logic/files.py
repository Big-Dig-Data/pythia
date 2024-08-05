import gzip


def open_file(fname, *args):
    if fname.endswith('.gz'):
        return gzip.open(fname, *args)
    return open(fname, *args)
