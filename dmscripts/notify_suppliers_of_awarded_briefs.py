from datetime import datetime, timedelta, date

from dmutils.email.exceptions import EmailError, EmailTemplateError
from dmutils.email.helpers import get_email_addresses, hash_string, validate_email_address
from dmutils.formats import DATE_FORMAT
from dmutils.env_helpers import get_web_url_from_stage


def _create_context_for_brief(stage, brief):
    return {
        'brief_title': brief['title'],
        'brief_link': '{}/{}/opportunities/{}'.format(
            get_web_url_from_stage(stage),
            brief['framework']['family'],
            brief['id']
        ),
        'utm_date': date.today().strftime("%Y%m%d")
    }


def _get_brief_responses_to_be_notified(data_api_client, brief_response_ids, awarded_at):

    if brief_response_ids:
        # Used for re-running failed email sending
        for brief_response_id in brief_response_ids:
            yield data_api_client.get_brief_response(brief_response_id)['briefResponses']
    else:
        awarded_at_date = awarded_at or (datetime.utcnow() - timedelta(days=1)).strftime(DATE_FORMAT)
        awarded_brief_responses = data_api_client.find_brief_responses_iter(awarded_at=awarded_at_date)

        for abr in awarded_brief_responses:
            # Add the awarded BriefResponse
            yield abr
            # Get the other non-awarded BriefResponses for the same Brief
            yield from data_api_client.find_brief_responses_iter(brief_id=abr['briefId'], status='submitted')

        # Get BriefResponses for any Briefs cancelled or unsuccessful on the same date
        for brief in data_api_client.find_briefs_iter(cancelled_on=awarded_at_date):
            yield from data_api_client.find_brief_responses_iter(brief_id=brief['id'])

        for brief in data_api_client.find_briefs_iter(unsuccessful_on=awarded_at_date):
            yield from data_api_client.find_brief_responses_iter(brief_id=brief['id'])


def _build_emails(brief_responses, stage, template_id, logger):

    # Now email everyone whose Brief got awarded
    for brief_response in brief_responses:
        email_addresses = get_email_addresses(brief_response["respondToEmailAddress"])

        # Users can enter multiple email addresses, but our input validation is very basic. So it's OK if some of the
        # addresses are invalid, as long as there is at least one valid address.
        invalid_email_addresses = [a for a in email_addresses if not validate_email_address(a)]
        if invalid_email_addresses:
            logger.warning(
                "Invalid email address(es) for BriefResponse {brief_response_id} (Brief ID {brief_id})",
                extra={
                    "brief_id": brief_response['brief']['id'],
                    "brief_response_id": brief_response['id'],
                }
            )

        for invalid_email_address in invalid_email_addresses:
            email_addresses.remove(invalid_email_address)

        if not email_addresses:
            logger.error(
                "No valid email address(es) for BriefResponse {brief_response_id} (Brief ID {brief_id})",
                extra={
                    "brief_id": brief_response['brief']['id'],
                    "brief_response_id": brief_response['id'],
                }
            )
            continue

        brief_email_context = _create_context_for_brief(stage, brief_response['brief'])
        for email_address in email_addresses:
            yield {
                "email_address": email_address,
                "template_id": template_id,
                "personalisation": brief_email_context
            }


def main(
    data_api_client, template_id, stage, logger, brief_response_ids=None, awarded_at=None
):
    brief_responses = _get_brief_responses_to_be_notified(data_api_client, brief_response_ids, awarded_at)
    notifications = _build_emails(brief_responses, stage, template_id, logger)
    yield from notifications
