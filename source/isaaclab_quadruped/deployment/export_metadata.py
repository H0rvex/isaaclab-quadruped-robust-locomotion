"""Export metadata contract for deployed policy artifacts.

Metadata recorded here lets a hardware bridge check whether an exported policy
matches the local interface contract. It is not an exporter implementation and
does not load inference backends.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from isaaclab_quadruped.deployment.policy_contract import PolicyInterfaceContract


@dataclass(frozen=True)
class PolicyExportMetadata:
    """Metadata that should travel with an exported policy artifact."""

    policy_name: str
    artifact_path: str
    checkpoint_path: str
    export_format: str
    observation_dim: int
    action_dim: int
    joint_names: tuple[str, ...]
    source_config: str
    created_by: str

    def validate_against(self, contract: PolicyInterfaceContract) -> None:
        """Validate metadata against the policy interface contract."""

        contract.validate()
        if self.policy_name != contract.policy_name:
            raise ValueError("metadata policy_name does not match contract")
        if self.observation_dim != contract.observation_dim:
            raise ValueError("metadata observation_dim does not match contract")
        if self.action_dim != contract.action_dim:
            raise ValueError("metadata action_dim does not match contract")
        if self.joint_names != contract.joint_names:
            raise ValueError("metadata joint_names do not match contract")
        if not self.artifact_path:
            raise ValueError("artifact_path must not be empty")
        if not self.checkpoint_path:
            raise ValueError("checkpoint_path must not be empty")
        if self.export_format not in {"torchscript", "onnx"}:
            raise ValueError("export_format must be torchscript or onnx")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
