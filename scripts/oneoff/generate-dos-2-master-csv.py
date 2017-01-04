#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Generate a CSV (to stdout) with per-lot draft statistics for each supplier

Usage:
    scripts/oneoff/generate-dos-2-master-csv.py <stage> <auth_token>

Example:
    scripts/oneoff/generate-dos-2-master-csv.py preview myToken
"""
from docopt import docopt

from dmapiclient import DataAPIClient

# add cwd to pythonpath
import sys
sys.path.insert(0, '.')

from dmscripts.generate_framework_master_csv import GenerateMasterCSV
from dmscripts.env import get_api_endpoint_from_stage

if __name__ == "__main__":
    arguments = docopt(__doc__)

    client = DataAPIClient(
        base_url=get_api_endpoint_from_stage(arguments['<stage>']),
        auth_token=arguments['<auth_token>'],
    )
    csv_builder = GenerateMasterCSV(
        client=client,
        target_framework_slug='digital-outcomes-and-specialists-2'
    )
    csv_builder.populate_output()
    csv_builder.write_csv()