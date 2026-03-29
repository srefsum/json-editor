from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..db.database import get_db
from ..models import schemas
from ..controllers.controllers import JSONSchemaController
from ..utils.infer_schema import build_proposed_schema

router = APIRouter(prefix="/api/schemas", tags=["schemas"])

@router.get("/", response_model=List[schemas.JSONSchemaResponse])
def list_schemas(db: Session = Depends(get_db)):
    return JSONSchemaController.get_all(db)

@router.post("/propose", response_model=schemas.ProposedSchemaResponse)
def propose_schema(request: schemas.ProposeSchemaRequest):
    return schemas.ProposedSchemaResponse(schema=build_proposed_schema(request.sample))

@router.get("/{schema_id}", response_model=schemas.JSONSchemaResponse)
def get_schema(schema_id: UUID, db: Session = Depends(get_db)):
    schema = JSONSchemaController.get_by_id(db, schema_id)
    if not schema:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found")
    return schema

@router.post("/", response_model=schemas.JSONSchemaResponse, status_code=status.HTTP_201_CREATED)
def create_schema(schema: schemas.JSONSchemaCreate, db: Session = Depends(get_db)):
    return JSONSchemaController.create(db, schema)

@router.put("/{schema_id}", response_model=schemas.JSONSchemaResponse)
def update_schema(schema_id: UUID, schema: schemas.JSONSchemaUpdate, db: Session = Depends(get_db)):
    updated_schema = JSONSchemaController.update(db, schema_id, schema)
    if not updated_schema:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found")
    return updated_schema

@router.delete("/{schema_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_schema(schema_id: UUID, db: Session = Depends(get_db)):
    if not JSONSchemaController.delete(db, schema_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Schema not found")
    return None

@router.post("/{schema_id}/validate", response_model=schemas.ValidationResponse)
def validate_json(schema_id: UUID, request: schemas.ValidationRequest, db: Session = Depends(get_db)):
    return JSONSchemaController.validate_json(db, schema_id, request.content)
