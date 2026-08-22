from gemmanode.credentials import InMemoryCredentialStore
from gemmanode.models import ConnectionStatus, IntegrationStage, ResourceType
from gemmanode.providers import ConnectionTestResult, StaticProviderAdapter
from gemmanode.resource_manager import InvalidConfigurationError, ResourceManager


class WorkingProvider(StaticProviderAdapter):
    def test_connection(self, resource, secrets):
        if self.auth_required and not secrets.get("api_key"):
            return ConnectionTestResult(False, "Missing key", ConnectionStatus.NOT_CONFIGURED)
        return ConnectionTestResult(True, "Connected", ConnectionStatus.CONNECTED)


class FailingProvider(StaticProviderAdapter):
    def test_connection(self, resource, secrets):
        return ConnectionTestResult(False, "Provider failure", ConnectionStatus.FAILED)


def make_manager():
    adapters = {
        "p1": WorkingProvider(
            "p1",
            "Provider 1",
            "p1",
            ResourceType.AI_PROVIDER,
            IntegrationStage.AVAILABLE,
            {"chat"},
            auth_required=True,
        ),
        "p2": FailingProvider(
            "p2",
            "Provider 2",
            "p2",
            ResourceType.CLOUD_COMPUTE,
            IntegrationStage.EXPERIMENTAL,
            {"compute"},
            auth_required=False,
            status=ConnectionStatus.UNTESTED,
        ),
    }
    return ResourceManager(adapters=adapters, credential_store=InMemoryCredentialStore())


def test_resource_creation():
    manager = make_manager()
    resources = manager.list_resources()
    assert len(resources) == 2
    assert {r.id for r in resources} == {"p1", "p2"}


def test_enable_disable_resource():
    manager = make_manager()
    manager.set_enabled("p1", False)
    assert manager.get_resource("p1").enabled is False
    assert manager.get_resource("p1").status == ConnectionStatus.DISABLED
    manager.set_enabled("p1", True)
    assert manager.get_resource("p1").enabled is True


def test_credential_configuration_and_removal():
    manager = make_manager()
    manager.configure_resource("p1", secrets={"api_key": "abc"}, configuration={"model": "x"})
    resource = manager.get_resource("p1")
    assert resource.configuration["model"] == "x"
    assert resource.status == ConnectionStatus.UNTESTED
    manager.remove_credentials("p1")
    resource = manager.get_resource("p1")
    assert resource.configuration == {}
    assert resource.status == ConnectionStatus.NOT_CONFIGURED


def test_connection_status_success_and_failure():
    manager = make_manager()
    manager.configure_resource("p1", secrets={"api_key": "abc"})
    manager.test_connection("p1")
    assert manager.get_resource("p1").status == ConnectionStatus.CONNECTED

    manager.test_connection("p2")
    assert manager.get_resource("p2").status == ConnectionStatus.FAILED


def test_invalid_configuration_when_store_missing():
    class UnavailableStore(InMemoryCredentialStore):
        def is_available(self):
            return False

        def set_secret(self, resource_id, name, value):
            raise InvalidConfigurationError("Secure credential storage is unavailable.")

    adapters = {
        "p1": WorkingProvider(
            "p1",
            "Provider 1",
            "p1",
            ResourceType.AI_PROVIDER,
            IntegrationStage.AVAILABLE,
            {"chat"},
            auth_required=True,
        )
    }
    manager = ResourceManager(adapters=adapters, credential_store=UnavailableStore())
    try:
        manager.configure_resource("p1", secrets={"api_key": "x"})
        assert False, "expected exception"
    except InvalidConfigurationError:
        assert True
