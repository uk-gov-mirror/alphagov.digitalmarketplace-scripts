import dmapiclient

from datetime import datetime, date, timedelta

from dmscripts.helpers import logging_helpers
from dmscripts.helpers.logging_helpers import logging
from dmutils.formats import DATETIME_FORMAT


logger = logging_helpers.configure_logger({'dmapiclient': logging.INFO})


def get_live_briefs_with_new_questions_and_answers_between_two_dates(data_api_client, start_date, end_date):
    briefs = data_api_client.find_briefs_iter(status='live', human=True)

    # return a list of briefs that contain clarification questions published between the start data and the end date
    return [brief for brief in briefs if len(brief['clarificationQuestions']) and any(
        datetime.strptime(question['publishedAt'], DATETIME_FORMAT) >= start_date
        and datetime.strptime(question['publishedAt'], DATETIME_FORMAT) <= end_date
        for question in brief['clarificationQuestions']
    )]


def get_ids_of_suppliers_who_started_applying(data_api_client, brief):
    responses = data_api_client.find_brief_responses(brief_id=brief["id"])
    return [response["supplierId"] for response in responses["briefResponses"]]


def get_ids_of_suppliers_who_asked_a_clarification_question(data_api_client, brief):
    audit_events = data_api_client.find_audit_events(
        audit_type=dmapiclient.audit.AuditTypes.send_clarification_question,
        object_type='briefs',
        object_id=brief['id']
    )
    return [audit_event['data']['supplierId'] for audit_event in audit_events['auditEvents']]


def get_ids_of_interested_suppliers_for_briefs(data_api_client, briefs):
    interested_suppliers = {}
    for brief in briefs:
        suppliers_who_applied = get_ids_of_suppliers_who_started_applying(data_api_client, brief)
        suppliers_who_asked_a_question = get_ids_of_suppliers_who_asked_a_clarification_question(data_api_client, brief)
        interested_suppliers[brief['id']] = list(set(suppliers_who_applied + suppliers_who_asked_a_question))

    return interested_suppliers


def invert_brief_ids_and_supplier_ids(dic):
    """
    This function takes a dictionary where its keys are brief ids and its values are lists of supplier ids
    and returns a dictionary where its keys are supplier ids and its values are lists of brief ids

    In:
    {
        1: [11111, 11112],
        2: [11112, 11113],
        3: []
    }

    Out:
    {
        11111: [1],
        11112: [1, 2],
        11113: [2]
    }
    """

    inverted_dic = {}
    for brief_id, list_of_supplier_ids in dic.items():
        assert isinstance(list_of_supplier_ids, list)
        for supplier_id in list_of_supplier_ids:
            # set empty list as default if key hasn't been assigned and then append a value
            # if the key has been assigned, the new value will be appended to the existing list
            inverted_dic.setdefault(supplier_id, []).append(brief_id)

    return inverted_dic

def main(data_api_client, number_of_days):
    logger.info("Begin to send brief update notification emails")

    # get today at 8 in the morning
    end_date = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    # get yesterday at 8 in the morning
    start_date = end_date - timedelta(days=number_of_days)

    # we need to find the briefs
    briefs = get_live_briefs_with_new_questions_and_answers_between_two_dates(data_api_client, start_date, end_date)

    # get all of the interested suppliers for each brief
    brief_ids_and_interested_supplier_ids = get_ids_of_interested_suppliers_for_briefs(data_api_client, briefs)

    # invert the data so that we have a dict of supplier ids pointing to a list of briefs they are interested in
    supplier_ids_and_interested_brief_ids = invert_brief_ids_and_supplier_ids(brief_ids_and_interested_supplier_ids)

    # for each supplier, write the email text
    for supplier_id, brief_ids in supplier_ids_and_interested_brief_ids.items():


    # for each supplier, get all users

    # for each user, blast the email



