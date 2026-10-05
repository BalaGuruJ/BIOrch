# Tableau Logical Relationship Architecture Design (Frozen Specification)

**Document ID:** `BIORCH-ARCH-TABLEAU-LOGICAL-RELATIONSHIPS-001`  
**Lifecycle Status:** FROZEN ARCHITECTURAL DESIGN (READ-ONLY — NO CODE/SCHEMA/CONTRACT MUTATION)  
**Target Domain:** Tableau Metadata Capability (Logical Layer / Object Model)  
**Downstream Dependency:** Phase 11 Structural Cross-Platform Comparison  

---

## 1. Frozen Design Decisions

| Decision Area | Frozen Architectural Rule | Architectural Rationale |
| :--- | :--- | :--- |
| **1. Endpoint Model** | Neutral `first_table_id` and `second_table_id`. Binary and non-directional. | Aligns directly with Tableau XML (`<first-end-point>`, `<second-end-point>`) while preventing false SQL directional join semantics (`left`/`right`). |
| **2. Commutative Identity** | $\text{identity\_tuple} = (\text{datasource\_id}, \min(T_1, T_2), \max(T_1, T_2))$. | Guarantees identity commutativity. In Tableau, at most one logical relationship exists between any two tables; XML serialization order variance cannot mutate the canonical ID. |
| **3. Opaque Expression** | `expression_raw` is preserved as a deterministic, normalized C14N XML fragment. No AST parsing or semantic interpretation. | Preserves 100% source fidelity and syntax without brittle partial SQL/AST parsing. Completely decouples extraction from downstream expression compilers. |
| **4. Object-to-Table Resolution** | `<first-end-point object-id="...">` maps via `<object id="...">` to the enclosed root `<relation>` to resolve the canonical `Table`. | Connects Tableau's logical layer abstraction cleanly to the existing BIOrch canonical `Table` entity graph. |
| **5. Strict Error Reporting** | Dangling or unresolvable endpoints MUST produce a deterministic `TableLogicalRelationshipResolutionIssue`. Never dropped silently. | Complies with BIOrch's strict provenance and validation mandate. |
| **6. Scope Boundaries** | **IN:** Binary logical `<relationship>` ("noodles") only.<br>**OUT:** Physical joins, custom SQL, physical decomposition, blending, semantic inference. | Strictly bounds implementation complexity and avoids scope creep. |
| **7. Phase 11 Comparison** | Phase 11 comparison is authorized to compare relationships at **Table grain** (`TableA <-> TableB`) when column pairs are opaque. | Unblocks structural cross-platform comparison without forcing prematurely scoped column-pair extraction. |

---

## 2. Canonical Relationship Model

### 2.1 Data Structure (`canonical_entities.py` / `relationships.py`)
```python
from dataclasses import dataclass, field
from typing import Optional
from biorch.integrations.tableau.entities import SourceEvidence


@dataclass(frozen=True)
class TableLogicalRelationship:
    """Canonical representation of a Tableau logical-layer relationship ('noodle').

    Represents a binary, context-aware semantic association between two logical
    tables within a single datasource.
    """

    canonical_id: str
    datasource_id: str
    first_table_id: str
    second_table_id: str
    expression_raw: str
    cardinality: Optional[str] = None
    source_evidence: frozenset[SourceEvidence] = field(default_factory=frozenset)
```

### 2.2 Resolution Issue Data Structure (`relationships.py`)
```python
@dataclass(frozen=True)
class TableLogicalRelationshipResolutionIssue:
    """Represents a failure to resolve a relationship endpoint to a canonical Table."""

    relationship_locator: str
    datasource_id: Optional[str]
    missing_endpoint_object_id: str
    evidence: SourceEvidence
    reason: str
```

---

## 3. Identity and Determinism Rules

### 3.1 Semantic Identity Class (`identity.py`)
```python
from dataclasses import dataclass
from enum import Enum
from biorch.integrations.tableau.identity import IdentityType, SemanticIdentity


class ExtendedIdentityType(str, Enum):
    LOGICAL_RELATIONSHIP = "logical_relationship"


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
```

### 3.2 Canonical ID Generation
The canonical ID is computed strictly via the existing BIOrch registry mechanism:
$$\text{canonical\_id} = \text{canonical\_id\_for}(\text{LogicalRelationshipIdentity}(\text{datasource\_id}, T_1, T_2))$$
producing a deterministic `sha256:{...}` hash that is independent of endpoint appearance order in the source `.twb` XML.

### 3.3 Expression Determinism Rule
The `expression_raw` string is generated by canonicalizing the inner XML of the `<expression>` subtree:
- Trim leading/trailing whitespace.
- Canonical XML formatting (`lxml.etree.tostring(elem, method="c14n2")` or normalized attribute order with standard indentation/newlines stripped).
- Guarantees byte-for-byte serialization determinism across repeated parses and operating systems.

---

## 4. Object-to-Table Resolution Rules

```
                      Tableau XML Source (.twb)
  +-------------------------------------------------------------------+
  | <object-graph>                                                    |
  |   <objects>                                                       |
  |     <object id="Orders_6D2EF...">                                 |
  |       <properties>                                                |
  |         <relation name="Orders" connection="excel-direct..." />   |
  |       </properties>                                               |
  |     </object>                                                     |
  |   </objects>                                                      |
  |   <relationships>                                                 |
  |     <relationship>                                                |
  |       <first-end-point object-id="Orders_6D2EF..." />             |
  |       <second-end-point object-id="People_37AF..." />             |
  |     </relationship>                                               |
  |   </relationships>                                                |
  | </object-graph>                                                   |
  +-------------------------------------------------------------------+
                                    |
                                    v
                       Resolution Execution Pipeline
  +-------------------------------------------------------------------+
  | Step 1: Extraction captures (object_id -> relation_locator) map   |
  | Step 2: Canonical Table lookup matches relation_locator to Table  |
  | Step 3: Verify first_table and second_table share datasource_id   |
  | Step 4: Emit TableLogicalRelationship (or ResolutionIssue)        |
  +-------------------------------------------------------------------+
```

### Exact Resolution Steps:
1. **Extraction Mapping:** During `extract_evidence()`, capture every `<object>` element to record the mapping:
   $$\text{object\_id} \longmapsto \text{source\_locator of enclosed root relation}$$
2. **Table Endpoint Lookup:**
   - Locate the canonical `Table` entity whose `source_evidence` contains the relation at that locator.
   - Map `first-end-point/@object-id` $\longrightarrow$ `first_table_id = Table_A.canonical_id`.
   - Map `second-end-point/@object-id` $\longrightarrow$ `second_table_id = Table_B.canonical_id`.
3. **Datasource Boundary Validation:** Both `Table_A` and `Table_B` MUST have `Table.datasource_id == relationship.datasource_id`.
4. **Issue Generation on Failure:**
   - If `object-id` does not exist in `<objects>`: emit `TableLogicalRelationshipResolutionIssue("referenced object-id not found")`.
   - If the enclosed relation did not form a valid canonical `Table`: emit `TableLogicalRelationshipResolutionIssue("underlying relation not constructed as table")`.
   - If tables belong to distinct datasources: emit `TableLogicalRelationshipResolutionIssue("cross-datasource logical relationship not permitted")`.
   - Under no circumstances is an unresolvable relationship silently discarded.

---

## 5. Scope Boundaries

```
+---------------------------------------------------------------------------------------------+
|                                    IN SCOPE (FROZEN)                                        |
+---------------------------------------------------------------------------------------------+
| 1. Tableau 2020.2+ Object Model logical relationships (<relationship> under <object-graph>)|
| 2. Binary, non-directional Table-to-Table logical graph topology                            |
| 3. Commutative identity hashing and deterministic SHA-256 canonical ID generation          |
| 4. Opaque, lossless XML preservation of <expression> (C14N format)                          |
| 5. Optional cardinality/referential-integrity attribute capture                             |
| 6. Deterministic resolution issue reporting for unresolvable endpoints                       |
| 7. JSON and CSV serialization parity                                                        |
+---------------------------------------------------------------------------------------------+

+---------------------------------------------------------------------------------------------+
|                                EXPLICITLY OUT OF SCOPE                                      |
+---------------------------------------------------------------------------------------------+
| 1. Expression AST decomposition (no column-level foreign key extraction in this phase)       |
| 2. Physical join trees (<relation type='join'>) inside an <object>                          |
| 3. Custom SQL parsing (<relation type='text'>) inside an <object>                           |
| 4. Multi-table physical decomposition when an <object> wraps joined relations               |
| 5. Cross-datasource blending (<blend-relationships>)                                        |
| 6. Semantic equivalence assertions or business logic inference                              |
+---------------------------------------------------------------------------------------------+
```

---

## 6. Phase 11 Compatibility

### 6.1 Grain Harmonization
- **Power BI Relationships:** Provide Table-to-Table and Column-to-Column endpoints (`from_table:from_col -> to_table:to_col`).
- **Tableau Logical Relationships (Frozen Design):** Provide Table-to-Table endpoints with opaque column expressions (`Table_A <-> Table_B [expression_raw]`).

### 6.2 Comparison Governance
Phase 11 comparison is governed to compare relationships at the **Table-Pair Grain**:
$$\text{Relationship Key} = \text{TableA} \longleftrightarrow \text{TableB}$$
- When comparing against Power BI, Phase 11 checks whether a relationship exists connecting Table A and Table B.
- Column-grain comparison for Tableau relationships is marked as `OPAQUE_EXPRESSION_EVALUATION_DEFERRED` without causing comparison failure or report corruption.

---

## 7. Explicit Future-Extension Points

The design intentionally leaves clean, non-breaking extension points for subsequent phases:
1. **Expression Parser Phase (Future):** When foreign-key column pairs are needed, an expression compiler can consume `expression_raw` and produce a downstream `CanonicalRelationshipFieldPair` model without changing this foundational relationship contract.
2. **Physical Join Parser Phase (Future):** If physical joins inside `<object>` ever need representation, they can be introduced as a separate physical relationship collection (`physical_table_joins`) without perturbing `logical_relationships`.
3. **Cardinality Inference Phase (Future):** If Tableau's Performance Options (`assume-referential-integrity`, `cardinality`) need mapping to standard relational cardinality enums, this can be layered directly onto the `cardinality` attribute.

---

## 8. Implementation Prerequisites

The following prerequisites must be formally satisfied before beginning code execution in a future implementation phase:

1. **Governance:**
   - Formal creation and approval of a task record in `governance/gemini/` under the appropriate phase.
2. **Contract Update:**
   - Surgical addition of `logical_relationships` into `contracts/tableau-agent/TABLEAU_AGENT_CONTRACT.md` (Sections 6 and 8).
3. **Schema Update:**
   - Surgical update to `schemas/tableau_metadata.schema.json` to declare `logical_relationships` under `workbook_metadata.relationships` and define `$defs/logical_relationship`.
4. **Implementation Sequence:**
   - `entities.py` $\longrightarrow$ `identity.py` $\longrightarrow$ `extraction.py` $\longrightarrow$ `canonical_entities.py` $\longrightarrow$ `relationships.py` $\longrightarrow$ `validation.py` $\longrightarrow$ `writer.py` $\longrightarrow$ unit/integration tests.
5. **Zero Workspace Modification Rule:**
   - Confirmed: No workspace files were modified during this investigation, design, or freeze lifecycle.
