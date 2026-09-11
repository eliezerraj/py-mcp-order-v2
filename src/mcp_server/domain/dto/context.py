from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SecurityContext:
    """Transport-agnostic security and tracing context for application use cases."""
    
    x_request_id: str
    auth_token: Optional[str] = None
