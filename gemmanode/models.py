from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ResourceType(str, Enum):
    LOCAL_COMPUTE = "Local Compute"
    CLOUD_COMPUTE = "Cloud Compute"
    AI_PROVIDER = "AI Provider"
    AGENT_FRAMEWORK = "Agent Framework"
    MANUAL_ESCALATION = "Manual Escalation"


class IntegrationStage(str, Enum):
    AVAILABLE = "Available"
    EXPERIMENTAL = "Experimental"
    PLANNED = "Planned"
    REQUIRES_CONFIGURATION = "Requires configuration"


class ConnectionStatus(str, Enum):
    AVAILABLE = "Available"
    CONNECTED = "Connected"
    NOT_CONFIGURED = "Not configured"
    UNTESTED = "Untested"
    FAILED = "Failed"
    NOT_IMPLEMENTED = "Not implemented"
    DISABLED = "Disabled"


class AuthenticationState(str, Enum):
    NOT_REQUIRED = "Not required"
    NOT_CONFIGURED = "Not configured"
    CONFIGURED = "Configured"


@dataclass
class ConnectionTestRecord:
    at: str
    success: bool
    message: str


@dataclass
class Resource:
    id: str
    name: str
    provider: str
    type: ResourceType
    status: ConnectionStatus
    enabled: bool
    capabilities: set[str] = field(default_factory=set)
    configuration: dict[str, Any] = field(default_factory=dict)
    authentication_state: AuthenticationState = AuthenticationState.NOT_REQUIRED
    last_connection_test: ConnectionTestRecord | None = None
    error_state: str | None = None
    stage: IntegrationStage = IntegrationStage.AVAILABLE

    def set_connection_result(self, success: bool, message: str, status: ConnectionStatus) -> None:
        self.status = status
        self.error_state = None if success else message
        self.last_connection_test = ConnectionTestRecord(
            at=datetime.now(timezone.utc).isoformat(),
            success=success,
            message=message,
        )

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["type"] = self.type.value
        payload["status"] = self.status.value
        payload["authentication_state"] = self.authentication_state.value
        payload["stage"] = self.stage.value
        payload["capabilities"] = sorted(self.capabilities)
        return payload
