#!/usr/bin/env python
"""
Inform suppliers involved in the G12 recovery that the process is now closed.

Usage:
    scripts/oneoff/close_g12_recovery_for_suppliers.py <stage> <notify_api_key> [--dry-run]

Parameters:
    <stage>                     Environment to run script against.

Options:
    -h, --help                  Show this screen.

Before running this script, ensure that the list of suppliers and draft IDs in the credentials is correct.
"""

import sys
from typing import Dict, List

from dmapiclient import DataAPIClient
from dmutils.email.helpers import hash_string
from dmutils.env_helpers import get_api_endpoint_from_stage
from docopt import docopt

sys.path.insert(0, ".")

from dmscripts.helpers import logging_helpers
from dmscripts.helpers.auth_helpers import (
    get_g12_suppliers,
    get_auth_token,
    get_g12_recovery_drafts,
)
from dmscripts.helpers.email_helpers import scripts_notify_client
from dmscripts.helpers.supplier_data_helpers import get_email_addresses_for_supplier

NOTIFY_TEMPLATE_ID = "123"  # TODO: update with real ID


def get_drafts_for_suppliers(
    api_client, supplier_ids, draft_ids
) -> Dict[int, List[dict]]:
    drafts_for_suppliers = {supplier_id: [] for supplier_id in supplier_ids}
    for draft_id in draft_ids:
        draft = api_client.get_draft_service(draft_id)["services"]
        drafts_for_suppliers[draft["supplierId"]].append(draft)
    return drafts_for_suppliers


if __name__ == "__main__":
    arguments = docopt(__doc__)

    stage = arguments["<stage>"]
    dry_run = arguments["--dry-run"]
    notify_api_key = arguments["<notify_api_key>"]

    logger = logging_helpers.configure_logger()
    mail_client = scripts_notify_client(notify_api_key, logger=logger)
    api_client = DataAPIClient(
        base_url=get_api_endpoint_from_stage(stage),
        auth_token=get_auth_token("api", stage),
    )

    draft_ids = get_g12_recovery_drafts(stage)
    supplier_ids = get_g12_suppliers(stage)
    drafts_for_suppliers = get_drafts_for_suppliers(api_client, supplier_ids, draft_ids)

    prefix = "[Dry Run] " if dry_run else ""
    for supplier_id in supplier_ids:
        submitted_draft_count = len(
            [
                draft
                for draft in drafts_for_suppliers[supplier_id]
                if draft["status"] == "submitted"
            ]
        )
        logger.info(
            f"Supplier {supplier_id} has {submitted_draft_count} submitted services"
        )
        if not submitted_draft_count:
            # Only send email to suppliers with some submitted services.
            continue

        for email in get_email_addresses_for_supplier(api_client, supplier_id):
            logger.info(f"{prefix}Sending email to supplier user: {hash_string(email)}")
            if not dry_run:
                mail_client.send_email(
                    to_email_address=email,
                    template_name_or_id=NOTIFY_TEMPLATE_ID,
                    personalisation={
                        "framework_name": "G-Cloud 12",
                        "number": submitted_draft_count,
                    },
                )
