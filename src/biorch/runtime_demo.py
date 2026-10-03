"""
BIOrch Runtime Demonstration Module
Executes Tableau and Power BI integration pipelines in parallel through the
existing BIOrch orchestration runtime (ToolGateway, AgentResolver, DeterministicOrchestrator),
followed by synthesis and provenance validation.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, Any, List

from biorch.core.workflow import Workflow
from biorch.core.task import Task, TaskStatus
from biorch.core.agent import Agent
from biorch.core.gateway import ToolGateway, ToolRegistry, ToolDefinition, ToolResult, ToolStatus
from biorch.agents.deterministic_agent import DeterministicAgentExecutor
from biorch.orchestration.agent_resolver import AgentResolver
from biorch.orchestration.orchestrator import DeterministicOrchestrator
from biorch.orchestration.synthesis import synthesize_result
from biorch.orchestration.provenance_validator import ProvenanceValidator

# Import existing integration pipelines
from biorch.integrations.tableau.cli import run_pipeline as run_tableau_pipeline
from biorch.integrations.powerbi.adapter import PowerBIAdapter
from biorch.integrations.powerbi.canonicalizer import canonicalize


class RuntimeDemoGateway(ToolGateway):
    """
    Custom ToolGateway subclass that performs standard security/authorization checks
    and executes the actual Tableau or Power BI integration pipelines.
    """
    def invoke(self, tool_id: str, version: str, resource: str, operation: str, inputs: Dict[str, Any]) -> ToolResult:
        # Perform standard validation checks from parent ToolGateway via custom logic or super()
        tool = self.registry.get_tool(tool_id)
        if not tool:
            return self._create_error_result(tool_id, version, ["Unknown tool"])
        if tool.version != version:
            return self._create_error_result(tool_id, version, ["Incorrect tool version"])
        if operation not in tool.permitted_operations:
            return self._create_error_result(tool_id, version, [f"Unauthorized operation: {operation}"])
        if not any(resource.startswith(r) for r in tool.allowed_resources):
            return self._create_error_result(tool_id, version, [f"Unauthorized resource: {resource}"])

        # Execute tool-specific logic
        try:
            if tool_id == "tableau_extractor":
                input_path = inputs.get("input_path")
                output_dir = inputs.get("output_directory", "/tmp/biorch_runtime_demo/tableau")
                published = run_tableau_pipeline(input_path, output_dir)
                artifacts = [str(p) for p in published]
                
                # Load metadata summary if available
                meta_json = Path(output_dir) / "metadata.json"
                meta_summary = {}
                if meta_json.exists():
                    import json
                    with open(meta_json, "r", encoding="utf-8") as f:
                        meta_content = json.load(f)
                        entities = meta_content.get("workbook_metadata", {}).get("entities", {})
                        meta_summary = {
                            "datasources_count": len(entities.get("datasources", [])),
                            "tables_count": len(entities.get("tables", [])),
                            "columns_count": len(entities.get("columns", [])),
                            "worksheets_count": len(entities.get("worksheets", []))
                        }

                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    tool_id=tool_id,
                    tool_version=version,
                    data={
                        "source": "tableau",
                        "input_path": str(input_path),
                        "output_directory": str(output_dir),
                        "summary": meta_summary
                    },
                    provenance={
                        "timestamp": os.getenv("BIORCH_TIMESTAMP", "2026-10-03T00:00:00"),
                        "artifacts": artifacts
                    }
                )

            elif tool_id == "powerbi_adapter":
                model_folder = inputs.get("model_folder")
                dll_path = os.environ.get("BIORCH_TOM_DLL_PATH")
                
                adapter = PowerBIAdapter(dll_path)
                db = adapter.load_model(model_folder)
                canonical_model = canonicalize(db)

                tables_count = len(canonical_model.tables)
                columns_count = len(canonical_model.columns)
                relationships_count = len(canonical_model.relationships)

                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    tool_id=tool_id,
                    tool_version=version,
                    data={
                        "source": "powerbi",
                        "model_folder": str(model_folder),
                        "database_name": getattr(db, "Name", "AdventureWorks Sales"),
                        "summary": {
                            "tables_count": tables_count,
                            "columns_count": columns_count,
                            "relationships_count": relationships_count
                        }
                    },
                    provenance={
                        "timestamp": os.getenv("BIORCH_TIMESTAMP", "2026-10-03T00:00:00"),
                        "artifacts": [str(model_folder)]
                    }
                )
            else:
                return self._create_error_result(tool_id, version, [f"Unrecognized tool execution handler for {tool_id}"])
        except Exception as e:
            return self._create_error_result(tool_id, version, [str(e)])


def run_demonstration() -> int:
    print("BIOrch Runtime Demonstration")
    print("----------------------------\n")

    # 1. Locate repository samples and check prerequisites
    repo_root = Path(__file__).resolve().parent.parent.parent
    tableau_input = repo_root / "examples/artifacts/tableau/superstore_base.twb"
    pbi_input = repo_root / "examples/artifacts/powerbi/AdventureWorks Sales/AdventureWorks Sales.SemanticModel"

    print(f"Tableau input path exists: {tableau_input.exists()} ({tableau_input})")
    print(f"Power BI input path exists: {pbi_input.exists()} ({pbi_input})")

    dotnet_root = os.environ.get("DOTNET_ROOT")
    tom_dll = os.environ.get("BIORCH_TOM_DLL_PATH")
    print(f"DOTNET_ROOT: {dotnet_root}")
    print(f"BIORCH_TOM_DLL_PATH: {tom_dll}")

    if not tableau_input.exists():
        print(f"Error: Tableau sample not found at {tableau_input}", file=sys.stderr)
        return 1

    pbi_ready = pbi_input.exists() and dotnet_root and tom_dll
    if not pbi_ready:
        print("Warning: Power BI prerequisites not fully met (TOM DLL / DOTNET_ROOT / model path).", file=sys.stderr)

    # 2. Register Tools in Registry
    registry = ToolRegistry()
    registry.register(ToolDefinition(
        tool_id="tableau_extractor",
        name="Tableau Metadata Extractor",
        purpose="Extract metadata and canonical entities from Tableau workbook",
        version="1.0",
        input_schema={"input_path": "str", "output_directory": "str"},
        output_schema={"source": "str", "summary": "dict"},
        allowed_resources=["examples/artifacts/tableau/", "/tmp/"],
        permitted_operations=["EXTRACT"],
        security_classification="INTERNAL"
    ))
    registry.register(ToolDefinition(
        tool_id="powerbi_adapter",
        name="Power BI Model Adapter",
        purpose="Deserialize and canonicalize Power BI semantic models",
        version="1.0",
        input_schema={"model_folder": "str"},
        output_schema={"source": "str", "summary": "dict"},
        allowed_resources=["examples/artifacts/powerbi/"],
        permitted_operations=["ANALYZE"],
        security_classification="INTERNAL"
    ))

    gateway = RuntimeDemoGateway(registry)

    # 3. Define Agents
    tableau_agent_def = Agent(
        agent_id="tableau_agent",
        name="Tableau Specialist",
        role="Tableau Extraction Agent",
        allowed_tools=["tableau_extractor"],
        supported_operations=["EXTRACT"]
    )
    pbi_agent_def = Agent(
        agent_id="powerbi_agent",
        name="Power BI Specialist",
        role="Power BI Analysis Agent",
        allowed_tools=["powerbi_adapter"],
        supported_operations=["ANALYZE"]
    )

    # 4. Configure AgentResolver
    resolver = AgentResolver({
        "tableau_agent": DeterministicAgentExecutor(gateway, tableau_agent_def),
        "powerbi_agent": DeterministicAgentExecutor(gateway, pbi_agent_def)
    })

    # 5. Construct Workflow with 2 parallel-ready independent tasks
    tableau_task = Task(
        task_id="tableau_task",
        objective="Extract Tableau workbook metadata",
        agent_id="tableau_agent",
        dependencies=[],
        inputs={
            "tool_id": "tableau_extractor",
            "version": "1.0",
            "operation": "EXTRACT",
            "resource": str(tableau_input),
            "tool_inputs": {
                "input_path": str(tableau_input),
                "output_directory": "/tmp/biorch_runtime_demo/tableau"
            }
        },
        status=TaskStatus.PENDING
    )

    pbi_task = Task(
        task_id="pbi_task",
        objective="Analyze Power BI semantic model",
        agent_id="powerbi_agent",
        dependencies=[],
        inputs={
            "tool_id": "powerbi_adapter",
            "version": "1.0",
            "operation": "ANALYZE",
            "resource": str(pbi_input),
            "tool_inputs": {
                "model_folder": str(pbi_input)
            }
        },
        status=TaskStatus.PENDING
    )

    workflow = Workflow(
        workflow_id="bi_parallel_analysis_workflow",
        version="1.0",
        tasks=[tableau_task, pbi_task],
        status="running"
    )

    # 6. Execute via DeterministicOrchestrator
    orchestrator = DeterministicOrchestrator(resolver)
    print("\nExecuting workflow via DeterministicOrchestrator (parallel dispatch)...")
    
    # Run with synthesis & handoff
    try:
        handoff = orchestrator.run_with_handoff(workflow)
        synthesis_result = synthesize_result(handoff)
    except Exception as e:
        print(f"Execution failed with exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1

    # 7. Validate Provenance
    try:
        validator = ProvenanceValidator(synthesis_result)
        validator.validate()
        checksum = validator.compute_audit_checksum()
        provenance_valid = True
    except Exception as e:
        provenance_valid = False
        print(f"Provenance validation failed: {e}", file=sys.stderr)

    # 8. Extract results for reporting
    step_results = handoff.workflow_result.step_results or {}
    tableau_res = step_results.get("tableau_task", {})
    pbi_res = step_results.get("pbi_task", {})

    tableau_status = tableau_res.get("status", "UNKNOWN").upper()
    pbi_status = pbi_res.get("status", "UNKNOWN").upper()

    tableau_findings = tableau_res.get("findings", [{}])
    pbi_findings = pbi_res.get("findings", [{}])

    tableau_summary = tableau_findings[0].get("summary", {}) if tableau_findings else {}
    pbi_summary = pbi_findings[0].get("summary", {}) if pbi_findings else {}

    synthesis_status = synthesis_result.get("status", "FAILED")

    # 9. Print required human-readable execution summary
    print(f"\nTableau")
    print(f"  input: {tableau_input}")
    print(f"  status: {tableau_status}")
    print(f"  key result information: extracted datasources={tableau_summary.get('datasources_count')}, tables={tableau_summary.get('tables_count')}, columns={tableau_summary.get('columns_count')}, worksheets={tableau_summary.get('worksheets_count')}")

    print(f"\nPower BI")
    print(f"  input: {pbi_input}")
    print(f"  status: {pbi_status}")
    print(f"  key result information: tables={pbi_summary.get('tables_count')}, columns={pbi_summary.get('columns_count')}, relationships={pbi_summary.get('relationships_count')}")

    print(f"\nOrchestration")
    print(f"  workflow: {workflow.workflow_id}")
    print(f"  task count: {len(workflow.tasks)}")
    print(f"  parallel-ready tasks: 2")
    print(f"  synthesis: {synthesis_status}")
    print(f"  provenance: {'VALID' if provenance_valid else 'INVALID'}")

    if tableau_status == "SUCCESS" and pbi_status == "SUCCESS" and synthesis_status in ("SUCCESS", "PARTIAL") and provenance_valid:
        print("\nDemonstration PASSED successfully.")
        return 0
    else:
        print("\nDemonstration encountered failures or invalid provenance.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(run_demonstration())
