"""Contract for the Unit of Work pattern."""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class UnitOfWork(ABC):
    """Coordinates a single transactional boundary.

    Concrete implementations live in `platform/infrastructure` (e.g. the
    SQLAlchemy-backed implementation used from this phase onward).
    """

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...
