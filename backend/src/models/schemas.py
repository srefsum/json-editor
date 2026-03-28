from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from uuid import UUID

class JSONDocumentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    content: dict[str, Any]
    schema_id: Optional[UUID] = None

class JSONDocumentCreate(JSONDocumentBase):
    pass

class JSONDocumentUpdate(JSONDocumentBase):
    pass

class JSONDocumentResponse(JSONDocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JSONSchemaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    schema: dict[str, Any]
    description: Optional[str] = None

class JSONSchemaCreate(JSONSchemaBase):
    pass

class JSONSchemaUpdate(JSONSchemaBase):
    pass

class JSONSchemaResponse(JSONSchemaBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ValidationRequest(BaseModel):
    content: dict[str, Any]

class ValidationResponse(BaseModel):
    valid: bool
    errors: Optional[list[str]] = None
