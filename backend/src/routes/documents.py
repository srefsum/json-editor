from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..db.database import get_db
from ..models import schemas
from ..controllers.controllers import JSONDocumentController

router = APIRouter(prefix="/api/documents", tags=["documents"])

@router.get("/", response_model=List[schemas.JSONDocumentResponse])
def list_documents(db: Session = Depends(get_db)):
    return JSONDocumentController.get_all(db)

@router.get("/{document_id}", response_model=schemas.JSONDocumentResponse)
def get_document(document_id: UUID, db: Session = Depends(get_db)):
    document = JSONDocumentController.get_by_id(db, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document

@router.post("/", response_model=schemas.JSONDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(document: schemas.JSONDocumentCreate, db: Session = Depends(get_db)):
    return JSONDocumentController.create(db, document)

@router.put("/{document_id}", response_model=schemas.JSONDocumentResponse)
def update_document(document_id: UUID, document: schemas.JSONDocumentUpdate, db: Session = Depends(get_db)):
    updated_document = JSONDocumentController.update(db, document_id, document)
    if not updated_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return updated_document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: UUID, db: Session = Depends(get_db)):
    if not JSONDocumentController.delete(db, document_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return None
