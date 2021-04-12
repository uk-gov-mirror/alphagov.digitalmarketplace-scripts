from typing import (
    Callable,
    Generator,
    List,
)
from pathlib import Path
import argparse
import logging

from notifications_python_client.notifications import NotificationsAPIClient

from .cli import argument_parser_factory
from .typing import EmailNotification, NotificationResponse
from .logger import AUDIT
from .queue import run


def email_engine(
    notifications_generator: Callable[
        [argparse.Namespace], Generator[EmailNotification, None, None]
    ],
    *,
    argv: List[str] = None,
    reference: str = None,
    logfile: Path = None,
):
    # get the configuration from the command line arguments
    args = argument_parser_factory(reference=reference, logfile=logfile).parse_args(
        argv
    )

    # configure logging
    #
    # We add the logfile handler to the root logger so all useful information
    # will be captured to the file.
    root_logger = logging.getLogger()
    log_handler = logging.FileHandler(args.logfile)
    root_logger.addHandler(log_handler)
    root_logger.setLevel(AUDIT)

    # prepare the state
    notifications_g = notifications_generator(args)

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
            send_email_notification, notifications=notifications_g, logfile=args.logfile
        )
    except KeyboardInterrupt:
        logging.warn("email engine interrupted by user")

    logging.info(f"sent {len(done)} email notifications with reference {reference}")
