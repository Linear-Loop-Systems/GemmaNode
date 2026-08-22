from __future__ import annotations

import logging
from typing import Any

from .credentials import CredentialStore, CredentialStoreUnavailable, KeyringCredentialStore
from .models import AuthenticationState, ConnectionStatus, Resource
from .providers import ProviderAdapter, default_adapters

logger = logging.getLogger(__name__)


class ResourceNotFoundError(Exception):
    pass


class InvalidConfigurationError(Exception):
    pass


class ResourceManager:
    def __init__(
        self,
        adapters: dict[str, ProviderAdapter] | None = None,
        credential_store: CredentialStore | None = None,
    ) -> None:
        self.adapters = adapters or default_adapters()
        self.credential_store = credential_store or KeyringCredentialStore()
        self.resources: dict[str, Resource] = {
            resource_id: adapter.make_resource() for resource_id, adapter in self.adapters.items()
        }

    def list_resources(self) -> list[Resource]:
        return list(self.resources.values())

    def get_resource(self, resource_id: str) -> Resource:
        try:
            return self.resources[resource_id]
        except KeyError as exc:
            raise ResourceNotFoundError(f"Resource '{resource_id}' not found") from exc

    def set_enabled(self, resource_id: str, enabled: bool) -> Resource:
        resource = self.get_resource(resource_id)
        resource.enabled = enabled
        if not enabled:
            resource.status = ConnectionStatus.DISABLED
        elif resource.status == ConnectionStatus.DISABLED:
            resource.status = ConnectionStatus.UNTESTED
        return resource

    def configure_resource(
        self,
        resource_id: str,
        configuration: dict[str, Any] | None = None,
        secrets: dict[str, str] | None = None,
    ) -> Resource:
        resource = self.get_resource(resource_id)
        adapter = self.adapters[resource_id]
        configuration = configuration or {}
        secrets = secrets or {}

        resource.configuration.update(configuration)

        required = adapter.required_secrets()
        for field in required:
            value = secrets.get(field)
            if value:
                try:
                    self.credential_store.set_secret(resource_id, field, value)
                except CredentialStoreUnavailable as exc:
                    raise InvalidConfigurationError(str(exc)) from exc

        if required:
            if all(self.credential_store.get_secret(resource_id, field) for field in required):
                resource.authentication_state = AuthenticationState.CONFIGURED
                if resource.status in {ConnectionStatus.NOT_CONFIGURED, ConnectionStatus.DISABLED}:
                    resource.status = ConnectionStatus.UNTESTED
            else:
                resource.authentication_state = AuthenticationState.NOT_CONFIGURED
                resource.status = ConnectionStatus.NOT_CONFIGURED
        return resource

    def remove_credentials(self, resource_id: str) -> Resource:
        resource = self.get_resource(resource_id)
        adapter = self.adapters[resource_id]
        for field in adapter.required_secrets():
            self.credential_store.delete_secret(resource_id, field)

        resource.configuration = {}
        if adapter.required_secrets():
            resource.authentication_state = AuthenticationState.NOT_CONFIGURED
            resource.status = ConnectionStatus.NOT_CONFIGURED
        resource.error_state = None
        resource.last_connection_test = None
        return resource

    def test_connection(self, resource_id: str) -> Resource:
        resource = self.get_resource(resource_id)
        if not resource.enabled:
            resource.set_connection_result(False, "Resource is disabled.", ConnectionStatus.DISABLED)
            return resource

        adapter = self.adapters[resource_id]
        secrets = {
            key: self.credential_store.get_secret(resource_id, key) or ""
            for key in adapter.required_secrets()
        }

        result = adapter.test_connection(resource, secrets)
        resource.set_connection_result(result.success, result.message, result.status)
        return resource
