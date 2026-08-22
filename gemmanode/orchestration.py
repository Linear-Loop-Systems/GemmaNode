from __future__ import annotations

from dataclasses import dataclass, field

from .models import ConnectionStatus, Resource


@dataclass
class TaskRequirements:
    capabilities: set[str] = field(default_factory=set)


@dataclass
class ExecutionResult:
    success: bool
    message: str
    resource_id: str | None = None


class NoEligibleResourceError(Exception):
    pass


class ResourceSelector:
    def select(self, resources: list[Resource], requirements: TaskRequirements) -> Resource:
        eligible: list[Resource] = []
        for resource in resources:
            if not resource.enabled:
                continue
            if resource.status in {
                ConnectionStatus.NOT_CONFIGURED,
                ConnectionStatus.FAILED,
                ConnectionStatus.NOT_IMPLEMENTED,
                ConnectionStatus.DISABLED,
            }:
                continue
            if not requirements.capabilities.issubset(resource.capabilities):
                continue
            eligible.append(resource)

        if not eligible:
            raise NoEligibleResourceError("No eligible resource is available for this task.")

        return eligible[0]


class ExecutionProvider:
    def execute(self, task: str, resource: Resource) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            message=(
                f"Task accepted for routing through {resource.name}. "
                "Execution adapters can now be implemented per provider."
            ),
            resource_id=resource.id,
        )


class Orchestrator:
    def __init__(
        self,
        selector: ResourceSelector | None = None,
        execution_provider: ExecutionProvider | None = None,
    ) -> None:
        self.selector = selector or ResourceSelector()
        self.execution_provider = execution_provider or ExecutionProvider()

    def submit_task(self, task: str, requirements: TaskRequirements, resources: list[Resource]) -> ExecutionResult:
        selected = self.selector.select(resources, requirements)
        return self.execution_provider.execute(task, selected)
