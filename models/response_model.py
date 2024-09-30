from typing import Optional, Dict, Any
from pydantic import BaseModel
class ResponseModel(BaseModel):
    success: bool
    data:Optional[Dict[str, Any]] = None