from gemmanode.models import ConnectionStatus, IntegrationStage, ResourceType
from gemmanode.orchestration import NoEligibleResourceError, Orchestrator, TaskRequirements
from gemmanode.providers import StaticProviderAdapter
from gemmanode.resource_manager import ResourceManager


class SelectorProvider(StaticProviderAdapter):
    def test_connection(self, resource, secrets):
        return super().test_connection(resource, secrets)


def make_resources():
    adapters = {
        "eligible": SelectorProvider(
            "eligible",
            "Eligible",
            "local",
            ResourceType.LOCAL_COMPUTE,
            IntegrationStage.AVAILABLE,
            {"compute", "chat"},
            auth_required=False,
            status=ConnectionStatus.AVAILABLE,
        ),
        "disabled": SelectorProvider(
            "disabled",
            "Disabled",
            "local",
            ResourceType.LOCAL_COMPUTE,
            IntegrationStage.AVAILABLE,
            {"compute", "chat"},
            auth_required=False,
            status=ConnectionStatus.DISABLED,
        ),
    }
    manager = ResourceManager(adapters=adapters)
    manager.set_enabled("disabled", False)
    return manager


def test_provider_selection_and_capability_matching():
    manager = make_resources()
    orchestrator = Orchestrator()
    result = orchestrator.submit_task(
        "run task",
        TaskRequirements(capabilities={"compute"}),
        manager.list_resources(),
    )
    assert result.success is True
    assert result.resource_id == "eligible"


def test_no_eligible_resource():
    manager = make_resources()
    manager.set_enabled("eligible", False)
    orchestrator = Orchestrator()
    try:
        orchestrator.submit_task(
            "run task",
            TaskRequirements(capabilities={"compute"}),
            manager.list_resources(),
        )
        assert False, "expected no eligible resource"
    except NoEligibleResourceError:
        assert True


def test_orchestrator_task_submission():
    manager = make_resources()
    orchestrator = Orchestrator()
    result = orchestrator.submit_task(
        "chat task",
        TaskRequirements(capabilities={"chat"}),
        manager.list_resources(),
    )
    assert result.success
    assert "Task accepted" in result.message
