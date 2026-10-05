"""Deterministic semantic identities for V1 canonical entities.

This module deliberately operates independently from ``SourceEvidence``.  A
source locator describes where an observation occurred; it is retained by the
registry as provenance and is never part of a semantic identity or canonical
ID.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
from typing import Callable, Protocol


class IdentityType(str, Enum):
    """The V1 canonical entity kinds with semantic identities."""

    DATASOURCE = "datasource"
    TABLE = "table"
    COLUMN = "column"
    FIELD = "field"
    COLUMN_INSTANCE = "column_instance"
    WORKSHEET = "worksheet"
    LOGICAL_RELATIONSHIP = "logical_relationship"


class ExtendedIdentityType(str, Enum):
    LOGICAL_RELATIONSHIP = "logical_relationship"


class SemanticIdentity(Protocol):
    """Common interface implemented by the V1 identity value objects."""

    @property
    def identity_type(self) -> IdentityType: ...

    def identity_tuple(self) -> tuple[str, ...]: ...


@dataclass(frozen=True)
class LogicalRelationshipIdentity:
    """Commutative semantic identity for Tableau logical relationships."""

    datasource_id: str
    table_a_id: str
    table_b_id: str

    def __post_init__(self):
        # Enforce canonical lexical order to guarantee commutativity
        if self.table_a_id > self.table_b_id:
            object.__setattr__(self, "table_a_id", self.table_b_id)
            object.__setattr__(self, "table_b_id", self.table_a_id)

    @property
    def identity_type(self) -> str:
        return ExtendedIdentityType.LOGICAL_RELATIONSHIP.value

    def identity_tuple(self) -> tuple[str, ...]:
        return (self.datasource_id, self.table_a_id, self.table_b_id)


@dataclass(frozen=True)
class DatasourceIdentity:
    name: str
    connection_class: str
    version: str

    @property
    def identity_type(self) -> IdentityType:
        return IdentityType.DATASOURCE

    def identity_tuple(self) -> tuple[str, ...]:
        return (self.name, self.connection_class, self.version)


@dataclass(frozen=True)
class TableIdentity:
    datasource_id: str
    relation_name: str
    connection_name: str

    @property
    def identity_type(self) -> IdentityType:
        return IdentityType.TABLE

    def identity_tuple(self) -> tuple[str, ...]:
        return (self.datasource_id, self.relation_name, self.connection_name)


@dataclass(frozen=True)
class ColumnIdentity:
    datasource_id: str
    parent_name: str
    remote_name: str

    @property
    def identity_type(self) -> IdentityType:
        return IdentityType.COLUMN

    def identity_tuple(self) -> tuple[str, ...]:
        return (self.datasource_id, self.parent_name, self.remote_name)


@dataclass(frozen=True)
class FieldIdentity:
    datasource_id: str
    field_name: str

    @property
    def identity_type(self) -> IdentityType:
        return IdentityType.FIELD

    def identity_tuple(self) -> tuple[str, ...]:
        return (self.datasource_id, self.field_name)


@dataclass(frozen=True)
class ColumnInstanceIdentity:
    datasource_id: str
    column_instance_name: str

    @property
    def identity_type(self) -> IdentityType:
        return IdentityType.COLUMN_INSTANCE

    def identity_tuple(self) -> tuple[str, ...]:
        return (self.datasource_id, self.column_instance_name)


@dataclass(frozen=True)
class WorksheetIdentity:
    worksheet_name: str

    @property
    def identity_type(self) -> IdentityType:
        return IdentityType.WORKSHEET

    def identity_tuple(self) -> tuple[str, ...]:
        return (self.worksheet_name,)


def serialize_identity(identity: SemanticIdentity) -> str:
    """Produce the canonical, stable serialization used as hash input."""
    return json.dumps(
        {
            "identity": identity.identity_tuple(),
            "identity_type": identity.identity_type.value,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _sha256_hex(serialized_identity: str) -> str:
    return sha256(serialized_identity.encode("utf-8")).hexdigest()


def canonical_id_for(identity: SemanticIdentity) -> str:
    """Return the reproducible SHA-256 canonical ID for an identity."""
    return f"sha256:{_sha256_hex(serialize_identity(identity))}"


class IdentityCollisionError(ValueError):
    """Raised when one generated canonical ID represents distinct identities."""


HashFunction = Callable[[str], str]


@dataclass
class _RegisteredIdentity:
    identity: SemanticIdentity
    source_locators: set[str] = field(default_factory=set)


class IdentityRegistry:
    """Register semantic identities and their source-occurrence provenance."""

    def __init__(self, hash_function: HashFunction = _sha256_hex):
        self._hash_function = hash_function
        self._identities: dict[str, _RegisteredIdentity] = {}

    def canonical_id_for(self, identity: SemanticIdentity) -> str:
        return f"sha256:{self._hash_function(serialize_identity(identity))}"

    def register(
        self, identity: SemanticIdentity, *, source_locator: str | None = None
    ) -> str:
        """Register an identity and optionally retain its XML occurrence locator.

        Repeated registration of the same semantic identity is idempotent for
        identity purposes.  Distinct locators are retained as provenance.
        """
        canonical_id = self.canonical_id_for(identity)
        registered = self._identities.get(canonical_id)
        if registered is None:
            registered = _RegisteredIdentity(identity)
            self._identities[canonical_id] = registered
        elif registered.identity != identity:
            raise IdentityCollisionError(
                "Canonical ID collision for distinct semantic identities: "
                f"{canonical_id}"
            )

        if source_locator is not None:
            registered.source_locators.add(source_locator)
        return canonical_id

    def source_locators_for(self, canonical_id: str) -> frozenset[str]:
        """Return retained source occurrence locators for a registered identity."""
        return frozenset(self._identities[canonical_id].source_locators)
