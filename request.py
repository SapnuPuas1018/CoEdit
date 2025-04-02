from dataclasses import dataclass
from typing import Any

@dataclass
class Request:
    request_type: str
    data: Any