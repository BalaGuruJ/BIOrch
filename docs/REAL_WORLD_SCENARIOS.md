# Real-World Workflow Scenarios

## 1. BIOrch Purpose

> BIOrch is intended to become a BI analysis copilot capable of coordinating specialized BI capabilities such as Tableau metadata analysis, Power BI metadata analysis, cross-platform comparison, migration analysis, and business-oriented reporting.

BIOrch is NOT itself the Tableau parser.
BIOrch is NOT itself the Power BI parser.

Instead:

```text
BIOrch
├── coordinates capabilities
├── routes work
├── manages workflow/state
├── combines results
└── produces useful business outputs
```

while:

- **TabUI** → Tableau capabilities
- **PBIParser** → Power BI capabilities

remain separate domain systems.

## 2. Canonical Real-World Scenarios

### BI-01 — Power BI Metadata Analysis
**User question:**
"Analyze this Power BI project and tell me which tables, columns, measures, relationships and visuals exist, and produce an Excel-ready metadata package."

**Expected conceptual flow:**
```text
User
↓
BIOrch
↓
identify Power BI request
↓
Power BI capability
↓
PBIParser
↓
structured Power BI metadata
↓
validation / analysis
↓
Excel-ready metadata package
↓
User
```

### BI-02 — Tableau Metadata Analysis
**User question:**
"Analyze this Tableau workbook and tell me which data sources, tables, columns, worksheets, dashboards, calculations and relationships exist, and produce an Excel-ready metadata package."

**Conceptual flow:**
```text
User
↓
BIOrch
↓
identify Tableau request
↓
Tableau capability
↓
TabUI
↓
structured Tableau metadata
↓
validation / analysis
↓
Excel-ready metadata package
↓
User
```

### BI-03 — Tableau vs Power BI Comparison
**User question:**
"Compare this Tableau workbook with this Power BI project and show me what has already been migrated and what is still missing."

**Conceptual flow:**
```text
User
↓
BIOrch
↓
TabUI ─────────────┐
                   │
                   ▼
               normalized
                metadata
                   ▲
                   │
PBIParser ─────────┘
                   │
                   ▼
               comparison
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
      matched   missing   changed
                   │
                   ▼
            migration report
                   │
                   ▼
                  User
```

### BI-04 — Migration Gap Analysis
**User question:**
"I am migrating this Tableau workbook to Power BI. Which Tableau tables and columns are already available in the Power BI semantic model, and which ones are missing?"

**Expected conceptual capabilities:**
- extract Tableau objects
- extract Power BI objects
- normalize object representations
- compare candidates
- classify migration status
- produce migration gap output

### BI-05 — Calculation and Relationship Migration
**User question:**
"Compare the calculations and relationships in the Tableau workbook and Power BI model. Which calculations or relationships are missing, changed, or require review?"

**Include:**
- Tableau calculated fields
- Power BI measures
- calculated columns
- relationships
- inactive relationships
- transformed logic
- review-required cases

*Note: A Tableau object does not necessarily have a one-to-one Power BI equivalent.*

### BI-06 — Excel Migration Tracker
**User question:**
"Compare the current Tableau and Power BI metadata and generate an Excel migration tracker with object, Tableau name, Power BI equivalent, status and comments."

**Expected conceptual output columns:**
| Object Type | Tableau Object | Power BI Object | Status | Comments |
| ----------- | -------------- | --------------- | ------ | -------- |

**Possible statuses:**
- MATCHED
- MISSING
- PARTIAL
- CHANGED
- TRANSFORMED
- NOT_APPLICABLE
- REVIEW_REQUIRED

## 3. Additional Real-World Questions
1. "Which Tableau dashboards depend on data or calculations that are not yet available in Power BI?"
2. "Show me all Tableau fields used in worksheets and identify whether each field has an equivalent field in Power BI."
3. "Identify Tableau calculations that may require redesign in Power BI rather than a direct one-to-one conversion."
4. "Which Power BI visuals currently depend on fields that have no corresponding Tableau source object?"
5. "The Power BI migration is only partially complete. Give me a migration coverage report showing completed, partially migrated and missing objects."
6. "What is still preventing this Tableau workbook from being considered fully migrated to Power BI?"
7. "Show me the migration progress between Tableau and Power BI and summarize the categories of missing objects."

## 4. Common Migration Object Vocabulary

| #  | Object                | Tableau             | Power BI                    |
| -- | --------------------- | ------------------- | --------------------------- |
| 1  | Data source           | Datasource          | Data source / connection    |
| 2  | Table                 | Table               | Table                       |
| 3  | Column                | Column              | Column                      |
| 4  | Measure / calculation | Calculated field    | Measure / calculated column |
| 5  | Relationship          | Relationship        | Relationship                |
| 6  | Hierarchy             | Hierarchy           | Hierarchy                   |
| 7  | Worksheet             | Worksheet           | Visual/report element       |
| 8  | Dashboard             | Dashboard           | Report/page                 |
| 9  | Filter                | Filter              | Filter/slicer               |
| 10 | Parameter             | Parameter           | Parameter/equivalent        |
| 11 | Calculation logic     | Tableau calculation | DAX                         |
| 12 | Dependency            | Lineage             | Lineage/dependency          |
| 13 | Usage                 | Worksheet → field   | Visual → field              |

> These categories establish a common analysis vocabulary. They do NOT imply that Tableau and Power BI objects are technically or semantically identical.

## 5. Migration Status Concepts
- **MATCHED:** The object exists in both systems and is functionally equivalent.
- **MISSING:** The object exists in the source but is completely absent from the destination.
- **PARTIAL:** The object exists in the destination but is incomplete or lacking all source functionality.
- **CHANGED:** The object exists in both systems but its logic or structure has been materially altered.
- **TRANSFORMED:** The object was fundamentally redesigned to fit the paradigm of the destination system.
- **NOT_APPLICABLE:** The object is specific to the source system and has no logical counterpart in the destination.
- **REVIEW_REQUIRED:** The migration state is uncertain or complex and requires human validation.

## 6. Emerging BIOrch Capability Model

```text
User
↓
BIOrch
↓
Understand request
↓
Select required capabilities
↓
┌───────────────────────┐
│                       │
▼                       ▼
TabUI                 PBIParser
│                       │
▼                       ▼
Tableau               Power BI
metadata              metadata
│                       │
└──────────┬────────────┘
           ▼
        Analysis
           │
           ▼
       Comparison
           │
           ▼
       Reporting
           │
           ▼
          User
```
*(This is a conceptual architecture, not an implementation.)*

## 7. What These Scenarios Will Tell Us
These scenarios will eventually help us determine:
- when an Agent is actually required
- when a deterministic workflow is sufficient
- what constitutes a Task
- what constitutes a Tool
- what constitutes a Result
- when multiple agents are useful
- when TabUI should be called
- when PBIParser should be called
- when parallel work is possible
- when results must be combined
- when human review may be required

## 8. Initial BIOrch Validation Matrix

| ID    | Scenario                           | Tableau | Power BI | Cross-platform | Excel Output | Future Agent/Orchestration Relevance |
| ----- | ---------------------------------- | ------- | -------- | -------------- | ------------ | ------------------------------------ |
| BI-01 | Power BI metadata                  | No      | Yes      | No             | Yes          | Medium                               |
| BI-02 | Tableau metadata                   | Yes     | No       | No             | Yes          | Medium                               |
| BI-03 | Tableau vs Power BI                | Yes     | Yes      | Yes            | Yes          | High                                 |
| BI-04 | Migration gap                      | Yes     | Yes      | Yes            | Yes          | High                                 |
| BI-05 | Calculation/relationship migration | Yes     | Yes      | Yes            | Yes          | High                                 |
| BI-06 | Excel migration tracker            | Yes     | Yes      | Yes            | Yes          | High                                 |

## 9. Connect this document to existing architecture
- `docs/ARCHITECTURE.md`
- `docs/ROADMAP.md`
- `docs/SECURITY.md`
- `docs/FRAMEWORK_EVALUATION.md`
- `schemas/agent.schema.json`
- `schemas/task.schema.json`
- `schemas/result.schema.json`
- `schemas/tool.schema.json`
- `schemas/workflow.schema.json`

## 10. Important Architectural Rules

> BIOrch will be designed from real user workflows backward, rather than starting with a multi-agent framework and forcing the workflows into that framework.

> More agents are not automatically better. A deterministic workflow should be preferred where the workflow is known and predictable. Agents should be introduced where specialized reasoning, adaptive routing, or independent context is genuinely useful.
