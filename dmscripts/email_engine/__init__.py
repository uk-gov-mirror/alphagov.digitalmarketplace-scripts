"""Framework for sending emails from scripts via Notify

::
    from dmscripts.email_engine import EmailNotification, email_engine

    def notifications_generator(*args, **kwargs):
        # generate emails to be sent by calling the DMp API
        ...
        yield EmailNotification(...)

    if __name__ == "__main__":
        email_engine(notifications_generator)

"""
from typing import (
    Callable,
    List,
    Optional,
)
from pathlib import Path
import argparse
import logging

from notifications_python_client.notifications import NotificationsAPIClient

from .cli import argument_parser_factory
from .typing import EmailNotification, NotificationResponse, Notifications
from .logger import AUDIT
from .queue import run


def email_engine(
    notifications: Notifications,
    *,
    args: Optional[argparse.Namespace] = None,
    argv: Optional[List[str]] = None,
    reference: Optional[str] = None,
    logfile: Optional[Path] = None,
):
    """Send emails via Notify

    Send emails produced by generator function `notifications` and log progress
    to disk. If interrupted `email_engine()` has the ability to resume by
    reading its own log file.

    :param notifications:  a generator function that yields `EmailNotification`s to send
    :param argv:  list of strings to parse. The default is taken from `sys.argv`.
    """
    # if arguments aren't supplied
    # get the configuration from the command line arguments
    if args is None:
        args = argument_parser_factory(
            reference=reference, logfile=logfile
        ).parse_args(argv)

    # configure logging
    #
    # We add the logfile handler to the root logger so all useful information
    # will be captured to the file.
    root_logger = logging.getLogger()
    log_handler = logging.FileHandler(args.logfile)
    root_logger.addHandler(log_handler)
    root_logger.setLevel(AUDIT)

    # prepare the state
    if callable(notifications):
        notifications = notifications(args)

    notify_client = NotificationsAPIClient(args.notify_api_key)

    if args.dry_run:

        def send_email_notification(
            notification: EmailNotification,
        ) -> NotificationResponse:
            logging.info(f"[DRY-RUN] would send email notification {notification}")
            return NotificationResponse()

    else:

        def send_email_notification(
            notification: EmailNotification,
        ) -> NotificationResponse:
            # note that all notifications will have the same reference
            return notify_client.send_email_notification(
                **notification,
                reference=reference,
            )

    try:
        # do the thing
        done = run(
            send_email_notification, notifications=notifications, logfile=args.logfile
        )
    except KeyboardInterrupt:
        logging.warn("email engine interrupted by user")

    logging.info(f"sent {len(done)} email notifications with reference {reference}")
