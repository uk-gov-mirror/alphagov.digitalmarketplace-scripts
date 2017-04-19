import pytest
from dmscripts.models.process_rules import (
    format_datetime_string_as_date,
    remove_username_from_email_address,
    replace_newlines_with_spaces
)


def test_format_datetime_string_as_date():
    initial_date = "2016-10-08T12:00:00.00000Z"
    formatted_date = "2016-10-08"
    assert format_datetime_string_as_date(initial_date) == formatted_date


def test_format_datetime_string_as_date_raises_error_if_initial_date_format_incorrect():
    initial_dates = (
        "2016-10-08T12:00:00.00000",
        "2016-10-08T12:00:00",
        "2016-10-08"
    )
    formatted_date = "2016-10-08"

    for date in initial_dates:
        with pytest.raises(ValueError) as excinfo:
            format_datetime_string_as_date(date)

        assert "time data '{}' does not match format".format(date) in str(excinfo.value)


def test_remove_username_from_email_address():
    initial_email_address = "user.name@domain.com"
    formatted_email_address = "domain.com"
    assert remove_username_from_email_address(initial_email_address) == formatted_email_address


test_data = [
    ("Che Guevara\n", "Che Guevara"),
    ("Che Guevara\n\r", "Che Guevara"),
    ("Che Guevara\n\n\n\n\r\r\r\r", "Che Guevara"),
    ("Che\n\rGuevara", "Che Guevara"),
    ("Che. \n\rGuevara. \n\r", "Che.  Guevara."),
    ("\n\rChe Guevara", "Che Guevara"),
    ("\n\n\r\rChe \n\r \n\r Guevara\n\r", "Che     Guevara"),
    (
        """
The Call-Off contract will be £28m per annum.
Each Statement of Work shall detail the allocated spend to that particular project.
        """,
        "The Call-Off contract will be £28m per annum. "
        "Each Statement of Work shall detail the allocated spend to that particular project."
    )
]


@pytest.mark.parametrize("before,after", test_data)
def test_replace_newlines_with_spaces(before, after):
    assert replace_newlines_with_spaces(before) == after
