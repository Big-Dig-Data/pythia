import json
import os
import sys
from collections import Counter
from pathlib import Path

import pysftp


def load_config(filename="ftp_config.json"):
    with open(filename, 'r') as infile:
        data = json.load(infile)
    for key, value in (('hostname', None), ('paths', None), ('user', None), ('password', None)):
        if key not in data:
            if value is None:
                raise ValueError("Missing config value: {}".format(key))
            else:
                data[key] = value
    return data


if __name__ == "__main__":
    from ftplib import FTP

    config = load_config()
    protocol = config.get('protocol', 'ftp')
    sync_dir = Path(sys.argv[1])
    stats = Counter()
    bytes_transferred = 0
    if protocol == 'sftp':
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        connection_factory = lambda: pysftp.Connection(
            config['hostname'], username=config['user'], password=config['password'], cnopts=cnopts
        )
    else:
        connection_factory = lambda: FTP(
            host=config['hostname'], user=config['user'], passwd=config['password']
        )

    with connection_factory() as ftp:
        for path_rec in config['paths']:
            ftp.cwd(path_rec['remote'])
            ldir = sync_dir / path_rec['local']
            if not ldir.exists():
                os.mkdir(ldir)
            files = ftp.listdir() if protocol == 'sftp' else ftp.nlst()
            for ffname in files:
                lfname = ldir / ffname
                if not (ffname.endswith('.gz') or ffname.endswith('.csv')):
                    # skip the file
                    stats['uninteresting'] += 1
                elif lfname.exists():
                    # skip the file
                    stats['skipped'] += 1
                else:
                    print("Retrieving {}".format(ffname))
                    if protocol == 'sftp':
                        ftp.get(ffname, lfname)
                    else:
                        with open(str(lfname), 'wb') as loutfile:
                            ftp.retrbinary('RETR {}'.format(ffname), loutfile.write)
                            bytes_transferred += loutfile.tell()
                    stats['retreived'] += 1
    print("Stats: {}, bytes transferred: {}".format(stats, bytes_transferred))
