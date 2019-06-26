import os
import io
import shutil
import re
import subprocess

from datetime import datetime

from dmscripts.helpers.html_helpers import render_html
from dmscripts.helpers.logging_helpers import get_logger
from dmscripts.helpers.framework_helpers import (
    find_suppliers_with_details_and_draft_service_counts
)
from dmscripts.export_framework_applicant_details import get_csv_rows

logger = get_logger()


def find_suppliers(client, framework, supplier_ids=None, map_impl=map, dry_run=False):
    """Return supplier details for suppliers with framework interest

    :param client: data api client
    :type client: dmapiclient.DataAPIClient
    :param dict framework: framework
    :param supplier_ids: list of supplier IDs to limit return to
    :type supplier_ids: Optional[List[Union[str, int]]]
    """
    # get supplier details (returns a lazy generator)
    logger.debug(f"fetching records for {len(supplier_ids) if supplier_ids else 'all'} suppliers")
    records = find_suppliers_with_details_and_draft_service_counts(
        client,
        framework["slug"],
        supplier_ids,
        map_impl=map_impl,
    )
    # we reuse code from another script to filter and flatten our supplier details
    _, rows = get_csv_rows(
        records,
        framework["slug"],
        framework_lot_slugs=tuple([lot["slug"] for lot in framework["lots"]]),
        count_statuses=("submitted",),
        dry_run=dry_run,
        include_central_supplier_details=True
    )
    return rows


def save_page(html, supplier_id, output_dir, descriptive_filename_part):
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    page_path = os.path.join(output_dir, '{}-{}.html'.format(supplier_id, descriptive_filename_part))
    with io.open(page_path, 'w+', encoding='UTF-8') as htmlfile:
        htmlfile.write(html)


def render_html_for_successful_suppliers(rows, framework, template_dir, output_dir, dry_run=False):
    template_path = os.path.join(template_dir, 'framework-agreement-signature-page.html')
    template_css_path = os.path.join(template_dir, 'framework-agreement-signature-page.css')

    for data in rows:
        if data['pass_fail'] in ('fail', 'discretionary'):
            logger.info(f"skipping supplier {data['supplier_id']} due to pass_fail=='{data['pass_fail']}'")
            continue

        logger.info(f"generating framework agreement page for successful supplier {data['supplier_id']}")

        data['framework'] = framework
        data['awardedLots'] = [lot for lot in framework['frameworkAgreementDetails']['lotOrder'] if int(data[lot]) > 0]
        data['includeCountersignature'] = False

        if dry_run:
            continue

        html = render_html(template_path, data)
        save_page(html, data['supplier_id'], output_dir, "signature-page")

    shutil.copyfile(template_css_path, os.path.join(output_dir, 'framework-agreement-signature-page.css'))


def render_html_for_suppliers_awaiting_countersignature(rows, framework, template_dir, output_dir):
    template_path = os.path.join(template_dir, 'framework-agreement-signature-page.html')
    template_css_path = os.path.join(template_dir, 'framework-agreement-signature-page.css')
    template_countersignature_path = os.path.join(template_dir, 'framework-agreement-countersignature.png')
    for data in rows:
        if data['pass_fail'] == 'fail' or data['countersigned_path'] or not data['countersigned_at']:
            logger.info("SKIPPING {}: pass_fail={} countersigned_at={} countersigned_path={}".format(
                data['supplier_id'],
                data['pass_fail'],
                data['countersigned_at'],
                data['countersigned_path'])
            )
            continue
        data['framework'] = framework
        data['awardedLots'] = [lot for lot in framework['frameworkAgreementDetails']['lotOrder'] if int(data[lot]) > 0]
        data['countersigned_at'] = datetime.strptime(
            data['countersigned_at'], '%Y-%m-%dT%H:%M:%S.%fZ'
        ).strftime('%d %B %Y')
        data['includeCountersignature'] = True
        html = render_html(template_path, data)
        save_page(html, data['supplier_id'], output_dir, "agreement-countersignature")
    shutil.copyfile(template_css_path, os.path.join(output_dir, 'framework-agreement-signature-page.css'))
    shutil.copyfile(
        template_countersignature_path,
        os.path.join(output_dir, 'framework-agreement-countersignature.png')
    )


def render_pdf_for_each_html_page(html_pages, html_dir, pdf_dir):
    html_dir = os.path.abspath(html_dir)
    pdf_dir = os.path.abspath(pdf_dir)
    ok = True
    if not os.path.exists(pdf_dir):
        os.mkdir(pdf_dir)
    for index, html_page in enumerate(html_pages):
        html_path = os.path.join(html_dir, html_page)
        pdf_path = '{}'.format(re.sub(r'\.html$', '.pdf', html_path))
        pdf_path = '{}'.format(re.sub(html_dir, pdf_dir, pdf_path))
        exit_code = subprocess.call(['wkhtmltopdf', 'file://{}'.format(html_path), pdf_path])
        if exit_code > 0:
            logger.error("ERROR {} on {}".format(exit_code, html_page))
            ok = False
    return ok
