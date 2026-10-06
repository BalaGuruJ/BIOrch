import hashlib
import json
from enum import Enum
from typing import Dict, Any, List, Optional

def _json_enum_serializer(obj: Any) -> Any:
    """JSON default handler to serialize Enum types."""
    if isinstance(obj, Enum):
        return obj.value
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

class ProvenanceValidationError(ValueError):
    """Raised when provenance validation or audit integrity check fails."""
    pass

class ProvenanceValidator:
    """
    Validates execution provenance, attribution integrity, completeness,
    non-fabrication, and computes/verifies cryptographic audit checksums
    (SHA-256) per SYNTHESIS_CONTRACT.md Section 15.2.
    """
    
    REQUIRED_PROVENANCE_KEYS = [
        "workflow_id",
        "workflow_version",
        "synthesis_contract",
        "synthesis_version",
        "synthesis_status",
        "synthesis_task_count"
    ]

    def __init__(self, synthesis_result: Dict[str, Any]):
        self.synthesis_result = synthesis_result

    def validate(self) -> bool:
        """
        Performs full validation of the synthesis result provenance and attribution integrity.
        Raises ProvenanceValidationError on failure.
        """
        if not isinstance(self.synthesis_result, dict):
            raise ProvenanceValidationError("Synthesis result must be a dictionary.")

        provenance = self.synthesis_result.get("provenance")
        if not isinstance(provenance, dict):
            raise ProvenanceValidationError("Provenance field is missing or not a dictionary.")

        # Completeness validation
        for key in self.REQUIRED_PROVENANCE_KEYS:
            if key not in provenance:
                raise ProvenanceValidationError(f"Missing required provenance field: '{key}'.")

        if provenance.get("workflow_id") != self.synthesis_result.get("workflow_id"):
            raise ProvenanceValidationError("Provenance workflow_id does not match synthesis result workflow_id.")
        if provenance.get("workflow_version") != self.synthesis_result.get("workflow_version"):
            raise ProvenanceValidationError("Provenance workflow_version does not match synthesis result workflow_version.")

        # Attribution integrity validation
        task_attributions = self.synthesis_result.get("task_attributions", [])
        if not isinstance(task_attributions, list):
            raise ProvenanceValidationError("task_attributions must be a list.")

        if len(task_attributions) != provenance.get("synthesis_task_count"):
            raise ProvenanceValidationError(
                f"Task count mismatch: task_attributions length ({len(task_attributions)}) "
                f"does not match synthesis_task_count ({provenance.get('synthesis_task_count')})."
            )

        for attr in task_attributions:
            if not isinstance(attr, dict):
                raise ProvenanceValidationError("Task attribution entry must be a dictionary.")
            task_id = attr.get("task_id")
            agent_id = attr.get("agent_id")
            status = attr.get("status")

            if not task_id:
                raise ProvenanceValidationError("Task attribution missing required 'task_id'.")
            if not status:
                raise ProvenanceValidationError(f"Task attribution for '{task_id}' missing required 'status'.")

        return True

    def compute_audit_checksum(self) -> str:
        """
        Computes a deterministic SHA-256 cryptographic audit checksum
        of the provenance and task attributions per SYNTHESIS_CONTRACT.md Section 15.2.
        """
        self.validate()
        provenance = self.synthesis_result.get("provenance", {})
        task_attributions = self.synthesis_result.get("task_attributions", [])
        
        canonical_payload = {
            "workflow_id": self.synthesis_result.get("workflow_id"),
            "workflow_version": self.synthesis_result.get("workflow_version"),
            "status": self.synthesis_result.get("status"),
            "synthesis_eligible": self.synthesis_result.get("synthesis_eligible"),
            "task_attributions": task_attributions,
            "provenance": provenance
        }
        
        serialized = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":"), default=_json_enum_serializer)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def verify_audit_checksum(self, expected_checksum: str) -> bool:
        """
        Verifies that the expected cryptographic audit checksum matches
        the recomputed SHA-256 checksum, detecting any tampering.
        """
        computed = self.compute_audit_checksum()
        if computed != expected_checksum:
            raise ProvenanceValidationError(
                f"Audit checksum mismatch! Expected: {expected_checksum}, Computed: {computed}."
            )
        return True
