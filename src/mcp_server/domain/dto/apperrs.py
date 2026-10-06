from typing import Optional

class AppError(Exception):
    
    def __init__(self, message: str, uri: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.uri: Optional[str] = uri
        self.status_code: Optional[int] = status_code
        self.message: str = message
        
    def to_dict(self):
        return {
            "uri": self.uri,
            "status_code": self.status_code,
            "message": self.message
        }