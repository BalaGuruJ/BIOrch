import os
import json
from typing import List, Dict, Any, Optional
import jsonschema
from biorch.orchestration.handoff import HandoffPayload
from biorch.orchestration.result import WorkflowResultStatus

def synthesize_result(handoff: HandoffPayload) -> Dict[str, Any]:
    """
    Transforms a validated HandoffPayload into a governed SynthesisResult
    complying with BIORCH-SYNTH-001 and schemas/synthesis_result.schema.json.
    """
    workflow = handoff.workflow
    workflow_result = handoff.workflow_result
    synthesis_eligible = handoff.synthesis_eligible

    # 1. Determine terminal status according to SYNTHESIS_CONTRACT.md Section 4 & 11
    if not synthesis_eligible or workflow_result.status == WorkflowResultStatus.REJECTED:
        terminal_status = "FAILED"
    elif workflow_result.status == WorkflowResultStatus.SUCCESS:
        terminal_status = "SUCCESS"
    elif workflow_result.status == WorkflowResultStatus.FAILED:
        terminal_status = "PARTIAL" if synthesis_eligible else "FAILED"
    else:
        terminal_status = "FAILED"

    # 2. Build task attributions strictly in declared workflow task order
    task_attributions = []
    aggregated_findings = []

    step_results = workflow_result.step_results or {}
    artifacts_map = handoff.artifacts or {}

    for task in workflow.tasks:
        task_id = task.task_id
        agent_id = task.agent_id
        step_res = step_results.get(task_id, {})
        raw_status = step_res.get("status", "NOT_EXECUTED")

        # Normalize step status to enum: ["SUCCESS", "FAILED", "TIMEOUT", "NOT_EXECUTED"]
        raw_upper = str(raw_status).upper()
        if "SUCCESS" in raw_upper or "COMPLETED" in raw_upper:
            norm_status = "SUCCESS"
        elif "FAIL" in raw_upper or "REJECTED" in raw_upper or "FAILURE" in raw_upper:
            norm_status = "FAILED"
        elif "TIMEOUT" in raw_upper:
            norm_status = "TIMEOUT"
        else:
            norm_status = "NOT_EXECUTED"

        # Findings: only included if status is SUCCESS and synthesis is eligible
        if norm_status == "SUCCESS" and synthesis_eligible:
            findings = step_res.get("findings", [])
            if not isinstance(findings, list):
                findings = [findings] if findings else []
        else:
            findings = []

        # Artifacts: list of strings
        raw_artifacts = artifacts_map.get(task_id, step_res.get("artifacts", []))
        if isinstance(raw_artifacts, list):
            artifacts = [str(a) for a in raw_artifacts]
        elif raw_artifacts:
            artifacts = [str(raw_artifacts)]
        else:
            artifacts = []

        # Errors: list of strings
        raw_errors = step_res.get("errors", [])
        if isinstance(raw_errors, list):
            errors = [str(e) for e in raw_errors]
        elif raw_errors:
            errors = [str(raw_errors)]
        else:
            errors = []

        attribution = {
            "task_id": task_id,
            "agent_id": agent_id,
            "status": norm_status,
            "findings": findings,
            "artifacts": artifacts,
            "errors": errors
        }
        task_attributions.append(attribution)

        # Build aggregated findings strictly in declared order without deduplication/reordering
        if terminal_status in ("SUCCESS", "PARTIAL") and norm_status == "SUCCESS":
            for f in findings:
                if isinstance(f, dict):
                    aggregated_findings.append({
                        "task_id": task_id,
                        "data": f
                    })
                elif isinstance(f, (int, float, str, bool)):
                    aggregated_findings.append({
                        "task_id": task_id,
                        "data": {"value": f}
                    })
                else:
                    aggregated_findings.append({
                        "task_id": task_id,
                        "data": {"raw": str(f)}
                    })

    # 3. Consolidate errors
    all_errors = []
    if workflow_result.errors:
        all_errors.extend([str(e) for e in workflow_result.errors])
    for attr in task_attributions:
        for err in attr["errors"]:
            if err not in all_errors:
                all_errors.append(err)

    if not synthesis_eligible and not all_errors:
        all_errors.append("Synthesis not eligible based on Join Gate evaluation")

    # 4. Provenance preservation and augmentation
    incoming_provenance = dict(workflow_result.provenance or {})
    provenance = {
        **incoming_provenance,
        "workflow_id": workflow.workflow_id,
        "workflow_version": workflow.version,
        "synthesis_contract": "BIORCH-SYNTH-001",
        "synthesis_version": "1.0",
        "synthesis_status": terminal_status,
        "synthesis_task_count": len(workflow.tasks)
    }

    result_dict = {
        "workflow_id": workflow.workflow_id,
        "workflow_version": workflow.version,
        "status": terminal_status,
        "synthesis_eligible": synthesis_eligible,
        "task_attributions": task_attributions,
        "aggregated_findings": aggregated_findings,
        "errors": all_errors,
        "provenance": provenance
    }

    # 5. Schema validation against schemas/synthesis_result.schema.json
    schema_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../schemas/synthesis_result.schema.json")
    )
    if not os.path.exists(schema_path):
        schema_path = "schemas/synthesis_result.schema.json"

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_data = json.load(f)

    jsonschema.validate(instance=result_dict, schema=schema_data)

    return result_dict
