from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from uuid import UUID
import jsonschema
from jsonschema import validate, ValidationError as JSONSchemaValidationError

from ..models import models, schemas

class JSONDocumentController:
    @staticmethod
    def get_all(db: Session) -> List[models.JSONDocument]:
        return db.query(models.JSONDocument).all()

    @staticmethod
    def get_by_id(db: Session, document_id: UUID) -> Optional[models.JSONDocument]:
        return db.query(models.JSONDocument).filter(models.JSONDocument.id == document_id).first()

    @staticmethod
    def create(db: Session, document: schemas.JSONDocumentCreate) -> models.JSONDocument:
        db_document = models.JSONDocument(
            name=document.name,
            content=document.content,
            schema_id=document.schema_id
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document

    @staticmethod
    def update(db: Session, document_id: UUID, document: schemas.JSONDocumentUpdate) -> Optional[models.JSONDocument]:
        db_document = db.query(models.JSONDocument).filter(models.JSONDocument.id == document_id).first()
        if db_document:
            db_document.name = document.name
            db_document.content = document.content
            db_document.schema_id = document.schema_id
            db.commit()
            db.refresh(db_document)
        return db_document

    @staticmethod
    def delete(db: Session, document_id: UUID) -> bool:
        db_document = db.query(models.JSONDocument).filter(models.JSONDocument.id == document_id).first()
        if db_document:
            db.delete(db_document)
            db.commit()
            return True
        return False

class JSONSchemaController:
    @staticmethod
    def get_all(db: Session) -> List[models.JSONSchema]:
        return db.query(models.JSONSchema).all()

    @staticmethod
    def get_by_id(db: Session, schema_id: UUID) -> Optional[models.JSONSchema]:
        return db.query(models.JSONSchema).filter(models.JSONSchema.id == schema_id).first()

    @staticmethod
    def create(db: Session, schema: schemas.JSONSchemaCreate) -> models.JSONSchema:
        db_schema = models.JSONSchema(
            name=schema.name,
            schema=schema.schema,
            description=schema.description
        )
        db.add(db_schema)
        db.commit()
        db.refresh(db_schema)
        return db_schema

    @staticmethod
    def update(db: Session, schema_id: UUID, schema: schemas.JSONSchemaUpdate) -> Optional[models.JSONSchema]:
        db_schema = db.query(models.JSONSchema).filter(models.JSONSchema.id == schema_id).first()
        if db_schema:
            db_schema.name = schema.name
            db_schema.schema = schema.schema
            db_schema.description = schema.description
            db.commit()
            db.refresh(db_schema)
        return db_schema

    @staticmethod
    def delete(db: Session, schema_id: UUID) -> bool:
        db_schema = db.query(models.JSONSchema).filter(models.JSONSchema.id == schema_id).first()
        if db_schema:
            db.delete(db_schema)
            db.commit()
            return True
        return False

    @staticmethod
    def validate_json(db: Session, schema_id: UUID, content: dict) -> schemas.ValidationResponse:
        db_schema = db.query(models.JSONSchema).filter(models.JSONSchema.id == schema_id).first()
        if not db_schema:
            return schemas.ValidationResponse(valid=False, errors=["Schema not found"])
        
        try:
            validate(instance=content, schema=db_schema.schema)
            return schemas.ValidationResponse(valid=True)
        except JSONSchemaValidationError as e:
            return schemas.ValidationResponse(valid=False, errors=[str(e.message)])
        except Exception as e:
            return schemas.ValidationResponse(valid=False, errors=[f"Validation error: {str(e)}"])
