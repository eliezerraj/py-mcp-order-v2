from dataclasses import dataclass
from typing import Any
from pydantic import Field

@dataclass(frozen=True, slots=True)
class VerifiedIdentity:
    subject: str = Field(
        description="The unique identifier for the verified identity"
    )
    roles: frozenset[str] = Field(
        description="The roles assigned to the verified identity"
    )
    scopes: frozenset[str] = Field(
        description="The scopes assigned to the verified identity"
    )
    claims: dict[str, Any] = Field(
        description="The claims associated with the verified identity"
    )