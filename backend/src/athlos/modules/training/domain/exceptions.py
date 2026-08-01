"""Domain-rule violations for the training bounded context."""


class InvalidDurationError(Exception):
    """Raised when a candidate duration is not strictly positive."""

    def __init__(self, seconds: int) -> None:
        super().__init__(f"Duration must be a positive number of seconds, got {seconds!r}.")
        self.seconds = seconds


class InvalidDistanceError(Exception):
    """Raised when a candidate distance is not strictly positive."""

    def __init__(self, meters: float) -> None:
        super().__init__(f"Distance must be a positive number of meters, got {meters!r}.")
        self.meters = meters


class ActivityNotFoundError(Exception):
    """Raised when an activity does not exist, or does not belong to the
    authenticated user.

    Deliberately generic in both cases - same anti-enumeration criterion
    already applied to `identity`'s `DeviceNotFoundError` (see
    docs/DECISIONS.md).
    """

    def __init__(self) -> None:
        super().__init__("Activity not found.")
