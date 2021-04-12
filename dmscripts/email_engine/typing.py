from ast import literal_eval
from typing import Dict


class EmailNotification(dict):
    """A typed, hashable, frozen dict subclass for tracking args to NotificationsAPIClient.send_email_notification"""

    def __init__(
        self,
        *,
        email_address: str,
        template_id: str,
        personalisation: Dict[str, str] = None
    ):
        super().__init__(
            email_address=email_address,
            template_id=template_id,
            personalisation=personalisation,
        )

    def __setitem__(self, key: str, value: str) -> None:
        raise RuntimeError("EmailNotification instances are frozen")

    def __hash__(self) -> int:  # type: ignore[override]  # noqa: F821
        # dicts are usually unhashable, but we want to use EmailNotifications
        # as the key to another dict, so we cheat and find the hash of the
        # string representation. The order of keys is going to be important for
        # this, so we make it explicit
        return (
            dict(
                email_address=self["email_address"],
                template_id=self["template_id"],
                personalisation=self["personalisation"],
            )
            .__repr__()
            .__hash__()
        )

    @classmethod
    def from_str(cls, s: str) -> "EmailNotification":
        """parse a dict literal representation of a notification"""
        return cls(**literal_eval(s))


class NotificationResponse(dict):
    @classmethod
    def from_str(cls, s: str) -> "NotificationResponse":
        """parse a dict literal representation of a NotificationResponse"""
        return cls(**literal_eval(s))
