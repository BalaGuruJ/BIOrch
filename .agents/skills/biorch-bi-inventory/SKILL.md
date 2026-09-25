---
name: biorch-bi-inventory
description: Standardize inventory and inspection of BI artifacts without implementing parser logic.
---

# BIOrch BI Inventory

## Purpose
Standardize the inventory and inspection of Business Intelligence (BI) artifacts to understand available metadata before orchestration routing.

## When to Use
When interrogating Tableau or Power BI artifacts to determine what objects exist for downstream analysis.

## Inputs
- Tableau artifacts (e.g., TWB, TWBX).
- Power BI artifacts (e.g., PBIP, SemanticModel, Report, TMDL).

## Procedure
Inventory the following as applicable:

**Tableau examples:**
- datasources
- tables
- columns
- worksheets
- dashboards
- calculations
- relationships
- filters
- lineage

**Power BI examples:**
- tables
- columns
- measures
- relationships
- hierarchies
- visuals
- dependencies

## Expected Outputs
- structured metadata
- metadata packages
- Excel-ready analysis packages
- comparison-ready normalized metadata

## Rules
- BIOrch coordinates BI analysis. It does not become the Tableau or Power BI parser.
- TabUI and PBIParser remain separate domain systems.
- Do not implement parser functionality.

## Boundaries
Metadata aggregation and standardization, not parsing.

## Evidence / Traceability
Generated metadata payload or inventory lists.

## Future Refinement
Standardized canonical schemas for BI object representations.
