import mock
from freezegun import freeze_time

from datetime import datetime

from dmscripts.send_questions_and_answers_email import (
    get_live_briefs_with_new_questions_and_answers_between_two_dates
)


def test_get_live_briefs_with_new_questions_and_answers_between_two_dates():
    data_api_client = mock.Mock()
    brief_iter_values = [
        # a brief with no questions
        {"clarificationQuestions": []},

        # a brief with a question outside of the date range
        {"clarificationQuestions": [{"publishedAt": "2017-03-22T06:00:00.669156Z"}]},

        # a brief with two questions outside of the date range
        {"clarificationQuestions": [
            {"publishedAt": "2017-03-21T06:00:00.669156Z"},
            {"publishedAt": "2017-03-22T06:00:00.669156Z"}
        ]},

        # a brief with a question inside of the date range
        {"clarificationQuestions": [{"publishedAt": "2017-03-23T06:00:00.669156Z"}]},

        # a brief with two questions inside of the date range
        {"clarificationQuestions": [
            {"publishedAt": "2017-03-22T18:00:00.669156Z"},
            {"publishedAt": "2017-03-23T06:00:00.669156Z"}
        ]},

        # a brief with two questions, one of them outside the range and one inside the range
        {"clarificationQuestions": [
            {"publishedAt": "2017-03-22T06:00:00.669156Z"},
            {"publishedAt": "2017-03-23T06:00:00.669156Z"}
        ]},

        # a brief with questions over the weekend
        {"clarificationQuestions": [
            {"publishedAt": "2017-03-17T18:00:00.669156Z"},
            {"publishedAt": "2017-03-18T06:00:00.669156Z"},
            {"publishedAt": "2017-03-19T06:00:00.669156Z"},  # Sunday
            {"publishedAt": "2017-03-20T06:00:00.669156Z"},
        ]}
    ]

    data_api_client.find_briefs_iter.return_value = iter(brief_iter_values)
    briefs = get_live_briefs_with_new_questions_and_answers_between_two_dates(
        data_api_client, datetime(2017, 3, 22, hour=8), datetime(2017, 3, 23, hour=8)
    )
    data_api_client.find_briefs_iter.assert_called_once_with(status="live", human=True)
    assert briefs == [
        {"clarificationQuestions": [{"publishedAt": "2017-03-23T06:00:00.669156Z"}]},
        {"clarificationQuestions": [
            {"publishedAt": "2017-03-22T18:00:00.669156Z"},
            {"publishedAt": "2017-03-23T06:00:00.669156Z"}
        ]},
        {"clarificationQuestions": [
            {"publishedAt": "2017-03-22T06:00:00.669156Z"},
            {"publishedAt": "2017-03-23T06:00:00.669156Z"}
        ]},
    ]
