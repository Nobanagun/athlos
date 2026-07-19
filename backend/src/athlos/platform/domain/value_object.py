"""Base building block for value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ValueObject:
    """Marker base for immutable, value-equality objects.

    Subclasses should also be declared `@dataclass(frozen=True)`; equality,
    hashing and immutability come from the dataclass machinery itself.
    """
