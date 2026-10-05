from collections.abc import Mapping, MutableMapping, MutableSequence, MutableSet
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any


class EvidenceType(Enum):
    """Classifies the kind of evidence being represented."""

    DATASOURCE = auto()
    RELATION = auto()
    METADATA_RECORD = auto()
    COLUMN_INSTANCE = auto()
    WORKSHEET = auto()
    OBJECT = auto()
    LOGICAL_RELATIONSHIP = auto()
    UNKNOWN = auto()


class DerivationStatus(Enum):
    """Distinguishes direct source evidence from internally derived evidence."""

    DIRECT = auto()
    DERIVED = auto()


class FrozenDict(Mapping):
    """Small immutable, hashable mapping used inside SourceEvidence.

    The mapping stores its entries as an immutable tuple rather than
    subclassing ``dict``. This closes dictionary mutation paths, including
    in-place union (``|=``).
    """

    __slots__ = ("_items", "_hash")

    def __init__(self, source: Mapping):
        self._items = tuple(source.items())
        self._hash = hash(frozenset(self._items))

    def __getitem__(self, key: Any) -> Any:
        for item_key, value in self._items:
            if item_key == key:
                return value
        raise KeyError(key)

    def __iter__(self):
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __hash__(self) -> int:
        return self._hash

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            return len(self) == len(other) and all(
                key in other and value == other[key]
                for key, value in self._items
            )
        return NotImplemented

    def __or__(self, other):
        raise TypeError("FrozenDict is immutable")

    def __ror__(self, other):
        raise TypeError("FrozenDict is immutable")

    def __ior__(self, other):
        raise TypeError("FrozenDict is immutable")

    def __setitem__(self, key, value):
        raise TypeError("FrozenDict is immutable")

    def __delitem__(self, key):
        raise TypeError("FrozenDict is immutable")

    def update(self, *args, **kwargs):
        raise TypeError("FrozenDict is immutable")

    def pop(self, *args, **kwargs):
        raise TypeError("FrozenDict is immutable")

    def popitem(self):
        raise TypeError("FrozenDict is immutable")

    def clear(self):
        raise TypeError("FrozenDict is immutable")

    def setdefault(self, *args, **kwargs):
        raise TypeError("FrozenDict is immutable")


def _freeze(obj: Any) -> Any:
    """Recursively convert supported mutable containers to immutable values.

    Unsupported mutable container types are rejected rather than retained,
    because retaining them would create a mutation path into SourceEvidence.
    """
    if isinstance(obj, Mapping):
        if isinstance(obj, MutableMapping):
            return FrozenDict({key: _freeze(value) for key, value in obj.items()})
        return FrozenDict({key: _freeze(value) for key, value in obj.items()})

    if isinstance(obj, (list, MutableSequence)):
        return tuple(_freeze(item) for item in obj)

    if isinstance(obj, (set, frozenset, MutableSet)):
        return frozenset(_freeze(item) for item in obj)

    if isinstance(obj, bytearray):
        return bytes(obj)

    # Tuples may themselves contain mutable values.
    if isinstance(obj, tuple):
        return tuple(_freeze(item) for item in obj)

    # Mapping/list/set handling above covers the mutable container types
    # supported by this representation. Reject other explicitly mutable
    # containers rather than silently retaining them.
    if isinstance(obj, (MutableMapping, MutableSequence, MutableSet)):
        raise TypeError(f"Unsupported mutable value type: {type(obj).__name__}")

    try:
        hash(obj)
    except TypeError as exc:
        raise TypeError(
            f"Unsupported unhashable value type: {type(obj).__name__}"
        ) from exc

    return obj


@dataclass(frozen=True)
class SourceEvidence:
    """
    Minimal representation for source observations and provenance.

    This is an evidence/provenance container, not a canonical semantic model.
    """

    source_file: str
    representation: str
    source_structure: str
    source_locator: str
    source_attributes: Mapping[str, Any] = field(default_factory=dict)
    evidence_type: EvidenceType = EvidenceType.UNKNOWN
    derivation_status: DerivationStatus = DerivationStatus.DIRECT

    def __post_init__(self):
        object.__setattr__(self, "source_attributes", _freeze(self.source_attributes))
