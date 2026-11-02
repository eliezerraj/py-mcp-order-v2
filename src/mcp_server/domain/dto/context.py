from typing import Optional, Any

from dataclasses import field
from dataclasses import dataclass

@dataclass(frozen=True)
class SecurityContext:
    """Transport-agnostic security and tracing context for application use cases."""
    
    x_request_id: str = field(
        metadata={"description": "The unique request identifier"}
    )
    auth_token: Optional[str] = field(
        default=None,
        metadata={"description": "The authentication token for the request"}
    )

    subject: str | None = field(
        default=None,
        metadata={"description": "The unique identifier for the subject"}
    )
    roles: frozenset[str] = field(
        default_factory=frozenset,
        metadata={"description": "The roles assigned to the subject"}
    )
    scopes: frozenset[str] = field(
        default_factory=frozenset,
        metadata={"description": "The scopes assigned to the subject"}
    )
    claims: dict[str, Any] = field(
        default_factory=dict,
        metadata={"description": "The claims associated with the subject"}
    )
