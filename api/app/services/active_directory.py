from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

try:
    from ldap3 import ALL, Connection, Server
except ImportError:  # pragma: no cover
    ALL = Connection = Server = None


@dataclass
class ActiveDirectoryConfig:
    host: str
    search_base: str
    bind_dn: str
    bind_password: str
    port: int = 636
    use_ssl: bool = True


class ActiveDirectoryClient:
    def __init__(self, config: ActiveDirectoryConfig):
        if Server is None or Connection is None:
            raise RuntimeError("ldap3 is required for Active Directory integration")
        self.config = config
        self.server = Server(config.host, port=config.port, use_ssl=config.use_ssl, get_info=ALL)

    def test_connection(self) -> None:
        conn = Connection(self.server, user=self.config.bind_dn, password=self.config.bind_password, auto_bind=True)
        conn.unbind()

    def fetch_users(self) -> list[dict[str, Any]]:
        attributes = [
            "objectGUID",
            "distinguishedName",
            "userPrincipalName",
            "sAMAccountName",
            "displayName",
            "mail",
            "department",
            "title",
            "whenCreated",
            "whenChanged",
            "userAccountControl",
        ]
        return self._search(
            ldap_filter="(&(objectClass=user)(objectCategory=person))",
            attributes=attributes,
        )

    def fetch_computers(self) -> list[dict[str, Any]]:
        attributes = [
            "objectGUID",
            "distinguishedName",
            "dNSHostName",
            "sAMAccountName",
            "operatingSystem",
            "operatingSystemVersion",
            "whenCreated",
            "whenChanged",
            "userAccountControl",
        ]
        return self._search(
            ldap_filter="(objectClass=computer)",
            attributes=attributes,
        )

    def _search(self, ldap_filter: str, attributes: list[str]) -> list[dict[str, Any]]:
        conn = Connection(self.server, user=self.config.bind_dn, password=self.config.bind_password, auto_bind=True)
        conn.search(search_base=self.config.search_base, search_filter=ldap_filter, attributes=attributes)
        rows: list[dict[str, Any]] = []
        for entry in conn.entries:
            entry_dict = entry.entry_attributes_as_dict
            rows.append({k: self._normalize(v) for k, v in entry_dict.items()})
        conn.unbind()
        return rows

    def _normalize(self, value: Any) -> Any:
        if isinstance(value, (list, tuple)):
            if len(value) == 1:
                return self._normalize(value[0])
            return [self._normalize(item) for item in value]
        if isinstance(value, bytes):
            return value.hex()
        if isinstance(value, datetime):
            return value.astimezone(UTC).isoformat()
        return value


def parse_ad_config(config_json: dict[str, Any] | list[Any]) -> ActiveDirectoryConfig:
    if not isinstance(config_json, dict):
        raise ValueError("Active Directory config_json must be a JSON object")

    required = ["host", "search_base", "bind_dn", "bind_password"]
    missing = [k for k in required if not config_json.get(k)]
    if missing:
        raise ValueError(f"Missing required AD config fields: {', '.join(missing)}")

    return ActiveDirectoryConfig(
        host=str(config_json["host"]),
        search_base=str(config_json["search_base"]),
        bind_dn=str(config_json["bind_dn"]),
        bind_password=str(config_json["bind_password"]),
        port=int(config_json.get("port", 636)),
        use_ssl=bool(config_json.get("use_ssl", True)),
    )
