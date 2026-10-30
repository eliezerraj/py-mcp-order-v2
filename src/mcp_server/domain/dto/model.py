from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class VerifiedIdentity:
    subject: str
    roles: frozenset[str]
    scopes: frozenset[str]
    claims: dict[str, Any]