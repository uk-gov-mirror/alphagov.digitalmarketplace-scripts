#!/usr/bin/env python

"""
Usage: scripts/upload-db-dump-to-s3.py <stage> <file_path>
"""

from docopt import docopt
from dmutils.s3 import S3


def upload_dump(stage, file_path):
    bucket = S3('digitalmarketplace-database-backup-{}'.format(stage))

    try:
        with open(file_path) as dump_file:
            bucket.save('/', dump_file, acl='private')
    except (OSError, IOError) as e:
        print("Error reading file '{}': {}".format(file_path, e.message))
        raise
    except S3ResponseError as e:
        print("Error uploading '{}' to bucket: {}".format(file_path, e.message))
        raise

if __name__ == '__main__':
    arguments = docopt(__doc__)
    stage = arguments['<stage>']
    file_path = arguments['<file_path>']

    upload_dump(stage, file_path)
