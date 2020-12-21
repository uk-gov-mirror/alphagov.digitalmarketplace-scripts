import csv
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, List, Mapping

from dmutils.formats import DATE_FORMAT, DATETIME_FORMAT
from dmutils.s3 import S3

from dmscripts.helpers.s3_helpers import get_bucket_name

# This URL is framework agnostic
PUBLIC_BRIEF_URL = "https://www.digitalmarketplace.service.gov.uk/digital-outcomes-and-specialists/opportunities/{}"

DOS_OPPORTUNITY_HEADERS = [
    "ID", "Opportunity", "Link", "Framework", "Category", "Specialist",
    "Organisation Name", "Buyer Domain", "Location Of The Work",
    "Published At", "Open For", "Expected Contract Length", "Applications from SMEs",
    "Applications from Large Organisations", "Total Organisations", "Status", "Winning supplier",
    "Size of supplier", "Contract amount", "Contract start date", "Clarification questions"
]

DOWNLOAD_FILE_NAME = "opportunity-data.csv"


def format_datetime_string_as_date(dt):
    return datetime.strptime(dt, DATETIME_FORMAT).strftime(DATE_FORMAT) if dt else None


def remove_username_from_email_address(ea):
    return '{}'.format(ea.split('@').pop()) if ea else None


def _build_row(brief: dict, brief_responses: List[dict]) -> OrderedDict:
    winner = None
    applications_from_sme_suppliers = 0
    applications_from_large_suppliers = 0

    for brief_response in brief_responses:
        if brief_response['supplierOrganisationSize'] == 'large':
            applications_from_large_suppliers += 1
        else:
            applications_from_sme_suppliers += 1

        if brief_response['status'] == 'awarded':
            winner = brief_response

    return OrderedDict(zip(DOS_OPPORTUNITY_HEADERS, [
        brief['id'],
        brief['title'],
        PUBLIC_BRIEF_URL.format(brief['id']),
        brief['frameworkSlug'],
        brief['lotSlug'],
        brief.get('specialistRole', ""),
        brief['organisation'],
        remove_username_from_email_address(brief['users'][0]['emailAddress']),
        brief['location'],
        format_datetime_string_as_date(brief['publishedAt']),
        brief.get('requirementsLength', '2 weeks'),  # only briefs on the specialists lot include 'requirementsLength'
        brief.get('contractLength', ''),
        applications_from_sme_suppliers,
        applications_from_large_suppliers,
        applications_from_sme_suppliers + applications_from_large_suppliers,
        brief['status'],
        winner['supplierName'] if winner else '',
        winner['supplierOrganisationSize'] if winner else '',
        winner['awardDetails']['awardedContractValue'] if winner else '',
        winner['awardDetails']['awardedContractStartDate'] if winner else '',
        len(brief['clarificationQuestions'])
    ]))


def get_latest_dos_framework(client) -> str:
    frameworks = client.find_frameworks()['frameworks']
    for framework in frameworks:
        # Should be maximum of 1 live DOS framework
        if framework['family'] == 'digital-outcomes-and-specialists' and framework['status'] == 'live':
            return framework['slug']
    return 'digital-outcomes-and-specialists'


def get_brief_data(client, logger) -> list:
    logger.info("Fetching closed briefs from API")
    briefs = client.find_briefs_iter(status="closed,awarded,unsuccessful,cancelled", with_users=True,
                                     with_clarification_questions=True)
    rows = []
    for brief in briefs:
        logger.info(f"Fetching brief responses for Brief ID {brief['id']}")
        brief_responses = client.find_brief_responses_iter(brief_id=brief['id'])
        rows.append(_build_row(brief, brief_responses))
    return rows


def write_rows_to_csv(rows: List[Mapping[str, Any]], file_path: str, logger) -> None:
    logger.info(f"Writing rows to {file_path}")

    # assumes all rows have the same keys
    fieldnames = list(rows[0].keys())

    with open(file_path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames, delimiter=',', quotechar='"')
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def upload_file_to_s3(file_path, bucket, remote_key_name, download_name, dry_run, logger):
    with open(file_path, 'br') as source_file:
        logger.info("{}UPLOAD: {} to {}::{}".format(
            '[Dry-run]' if dry_run else '',
            file_path,
            bucket.bucket_name,
            download_name
        ))

        if not dry_run:
            # Save file
            bucket.save(remote_key_name, source_file, acl='public-read', download_filename=download_name)


def export_dos_opportunities(
    client,
    logger,
    stage: str,
    output_dir,
    dry_run: bool = False
):
    output_dir = Path(output_dir)
    if not output_dir.exists():
        logger.info(f"Creating {output_dir} directory")
        output_dir.mkdir(parents=True)

    latest_framework_slug = get_latest_dos_framework(client)

    file_path = output_dir / DOWNLOAD_FILE_NAME
    bucket_name = get_bucket_name(stage, "communications")
    key_name = f"{latest_framework_slug}/communications/data/{DOWNLOAD_FILE_NAME}"

    logger.info("Exporting DOS opportunity data to CSV")

    # Get the data
    rows = get_brief_data(client, logger)

    # Construct CSV
    write_rows_to_csv(rows, file_path, logger)

    # Grab bucket
    bucket = S3(bucket_name)

    # Upload to S3
    upload_file_to_s3(
        file_path,
        bucket,
        key_name,
        DOWNLOAD_FILE_NAME,
        dry_run=dry_run,
        logger=logger
    )
