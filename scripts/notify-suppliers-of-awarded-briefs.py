#!/usr/bin/env python3
"""
If a brief has been awarded suppliers need to be notified. This
script notifies suppliers of all awarded briefs in the previous day by default.
Alternatively, when supplied with a list of BriefResponse IDs, it will notify just the suppliers for those responses.

Usage:
    notify-suppliers-of-awarded-briefs.py <stage> <govuk_notify_api_key> <govuk_notify_template_id>
        [options]

Options:
    -h, --help                                      Display this screen
    -v, --verbose                                   Verbosity level
    --dry-run                                       Log without sending emails
    --brief_response_ids=<brief_response_ids>       (for resending failures)

Examples:
    ./scripts/notify-suppliers-of-awarded-briefs.py preview myToken notifyToken t3mp1at3id --awarded_at=2017-10-27
    ./scripts/notify-suppliers-of-awarded-briefs.py preview myToken notifyToken t3mp1at3id --dry-run --verbose

"""

import logging
import sys
from docopt import docopt

from dmapiclient import DataAPIClient

sys.path.insert(0, '.')

from dmscripts.helpers.email_helpers import scripts_notify_client
from dmscripts.helpers.auth_helpers import get_auth_token
from dmscripts.helpers import logging_helpers
from dmscripts.notify_suppliers_of_awarded_briefs import main
from dmscripts.email_engine import email_engine, argument_parser_factory
from dmutils.env_helpers import get_api_endpoint_from_stage


if __name__ == "__main__":
    arg_parser = argument_parser_factory()

    # Get arguments
    arg_parser.add_argument("--awarded-at",
        help="Notify applicants to briefs awarded on this date, defaults to yesterday (date format: YYYY-MM-DD)"
    )
    arg_parser.add_argument("--brief-response-ids", help="List of brief response IDs to send to")

    args = arg_parser.parse_args()

    data_api_client = DataAPIClient(base_url=get_api_endpoint_from_stage(args.stage),
                                    auth_token=get_auth_token('api', args.stage))

    list_of_brief_response_ids = list(map(int, args.brief_response_ids.split(','))) if args.brief_response_ids else None

    # Do send
    email_engine(
        main(
            data_api_client=data_api_client,
            template_id=args.notify_template_id,
            stage=args.stage,
            logger=logger,
            awarded_at=args.awarded_at,
            brief_response_ids=list_of_brief_response_ids,
        ),
        args
    )
