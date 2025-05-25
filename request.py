from dataclasses import dataclass
from typing import Any

@dataclass
class Request:
    """
    A data class representing a client/server request.

    :param request_type: The type of request being made (e.g., "login", "signup", "edit")
    :type request_type: str

    :param data: The associated data for the request. Can be any type depending on the request_type
    :type data: Any
    """
    request_type: str
    data: Any
