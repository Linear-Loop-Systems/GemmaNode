from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class CredentialStoreUnavailable(Exception):
    pass


class CredentialStore(Protocol):
    def is_available(self) -> bool:
        ...

    def set_secret(self, resource_id: str, name: str, value: str) -> None:
        ...

    def get_secret(self, resource_id: str, name: str) -> str | None:
        ...

    def delete_secret(self, resource_id: str, name: str) -> None:
        ...


@dataclass
class KeyringCredentialStore:
    service_prefix: str = "gemmanode"

    def __post_init__(self) -> None:
        try:
            import keyring

            self._keyring = keyring
        except Exception:
            self._keyring = None

    def _service_name(self, resource_id: str) -> str:
        return f"{self.service_prefix}.{resource_id}"

    def is_available(self) -> bool:
        return self._keyring is not None

    def set_secret(self, resource_id: str, name: str, value: str) -> None:
        if not self._keyring:
            raise CredentialStoreUnavailable("Secure credential storage is unavailable.")
        self._keyring.set_password(self._service_name(resource_id), name, value)

    def get_secret(self, resource_id: str, name: str) -> str | None:
        if not self._keyring:
            return None
        return self._keyring.get_password(self._service_name(resource_id), name)

    def delete_secret(self, resource_id: str, name: str) -> None:
        if not self._keyring:
            return
        try:
            self._keyring.delete_password(self._service_name(resource_id), name)
        except Exception:
            return


class InMemoryCredentialStore:
    def __init__(self) -> None:
        self._secrets: dict[tuple[str, str], str] = {}

    def is_available(self) -> bool:
        return True

    def set_secret(self, resource_id: str, name: str, value: str) -> None:
        self._secrets[(resource_id, name)] = value

    def get_secret(self, resource_id: str, name: str) -> str | None:
        return self._secrets.get((resource_id, name))

    def delete_secret(self, resource_id: str, name: str) -> None:
        self._secrets.pop((resource_id, name), None)
