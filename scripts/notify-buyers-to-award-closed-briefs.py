#!/usr/bin/env python
"""Send email notifications to buyer users to remind them to award their closed requirements.

Usage:
    notify-buyers-to-award-closed-briefs.py <stage> <api_token>
        <govuk_notify_api_key> <govuk_notify_template_id> [options]

Example:
    notify-buyers-to-award-closed-briefs.py local myToken myNotifyToken myNotifyTemplateId --dry-run=True

Options:
    -h, --help  Show this screen
    --date-closed=<date> Notify users of requirements closed on that date (date format: YYYY-MM-DD)
    --dry-run List notifications that would be sent without sending actual emails

"""

import sys

sys.path.insert(0, '.')
from docopt import docopt

from dmscripts.helpers.env_helpers import get_api_endpoint_from_stage
from dmscripts.notify_buyers_to_award_closed_briefs import main


if __name__ == '__main__':
    arguments = docopt(__doc__)

    ok = main(
        data_api_url=get_api_endpoint_from_stage(arguments['<stage>'], 'api'),
        data_api_access_token=arguments['<api_token>'],
        notify_api_key=arguments['<govuk_notify_api_key>'],
        notify_template_id=arguments['<govuk_notify_template_id>'],
        date_closed=arguments['--date-closed'],
        dry_run=arguments['--dry-run']
    )

    if not ok:
        sys.exit(1)
