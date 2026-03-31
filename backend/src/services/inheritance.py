"""Resolve inherited JSON documents and schemas (reference + local overlay)."""

from __future__ import annotations

import copy
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import models

INHERITANCE_MAX_DEPTH = 32


class InheritanceError(ValueError):
    pass


def deep_merge_document(base: Any, overlay: Any) -> Any:
    """Deep-merge objects; arrays and scalars from overlay replace at that key."""
    if isinstance(base, dict) and isinstance(overlay, dict):
        out = copy.deepcopy(base)
        for key, val in overlay.items():
            if (
                key in out
                and isinstance(out[key], dict)
                and isinstance(val, dict)
            ):
                out[key] = deep_merge_document(out[key], val)
            else:
                out[key] = copy.deepcopy(val)
        return out
    return copy.deepcopy(overlay)


def resolve_document_content(db: Session, document_id: UUID) -> Any:
    row = db.query(models.JSONDocument).filter(models.JSONDocument.id == document_id).first()
    if not row:
        raise InheritanceError("Document not found")

    chain: list[models.JSONDocument] = []
    seen: set[UUID] = set()
    cur: Optional[models.JSONDocument] = row
    depth = 0

    while cur is not None:
        if depth >= INHERITANCE_MAX_DEPTH:
            raise InheritanceError("Document inheritance chain exceeds maximum depth")
        if cur.id in seen:
            raise InheritanceError("Cycle detected in document inheritance")
        seen.add(cur.id)
        chain.append(cur)
        if cur.extends_document_id is None:
            break
        parent = (
            db.query(models.JSONDocument)
            .filter(models.JSONDocument.id == cur.extends_document_id)
            .first()
        )
        if not parent:
            raise InheritanceError("Parent document not found")
        cur = parent
        depth += 1

    root = chain[-1]
    merged: Any = copy.deepcopy(root.content)
    for child in reversed(chain[:-1]):
        merged = deep_merge_document(merged, child.content)
    return merged


def document_inheritance_path(db: Session, document_id: UUID) -> list[UUID]:
    row = db.query(models.JSONDocument).filter(models.JSONDocument.id == document_id).first()
    if not row:
        raise InheritanceError("Document not found")

    path: list[UUID] = []
    seen: set[UUID] = set()
    cur: Optional[models.JSONDocument] = row
    depth = 0

    while cur is not None:
        if depth >= INHERITANCE_MAX_DEPTH:
            raise InheritanceError("Document inheritance chain exceeds maximum depth")
        if cur.id in seen:
            raise InheritanceError("Cycle detected in document inheritance")
        seen.add(cur.id)
        path.append(cur.id)
        if cur.extends_document_id is None:
            break
        parent = (
            db.query(models.JSONDocument)
            .filter(models.JSONDocument.id == cur.extends_document_id)
            .first()
        )
        if not parent:
            raise InheritanceError("Parent document not found")
        cur = parent
        depth += 1

    return list(reversed(path))


def resolve_schema_for_validation(db: Session, schema_id: UUID) -> dict[str, Any]:
    row = db.query(models.JSONSchema).filter(models.JSONSchema.id == schema_id).first()
    if not row:
        raise InheritanceError("Schema not found")

    chain: list[models.JSONSchema] = []
    seen: set[UUID] = set()
    cur: Optional[models.JSONSchema] = row
    depth = 0

    while cur is not None:
        if depth >= INHERITANCE_MAX_DEPTH:
            raise InheritanceError("Schema inheritance chain exceeds maximum depth")
        if cur.id in seen:
            raise InheritanceError("Cycle detected in schema inheritance")
        seen.add(cur.id)
        chain.append(cur)
        if cur.extends_schema_id is None:
            break
        parent = (
            db.query(models.JSONSchema)
            .filter(models.JSONSchema.id == cur.extends_schema_id)
            .first()
        )
        if not parent:
            raise InheritanceError("Parent schema not found")
        cur = parent
        depth += 1

    root = chain[-1]
    acc: dict[str, Any] = copy.deepcopy(root.schema)
    for child in reversed(chain[:-1]):
        acc = {"allOf": [acc, copy.deepcopy(child.schema)]}
    return acc


def schema_inheritance_path(db: Session, schema_id: UUID) -> list[UUID]:
    row = db.query(models.JSONSchema).filter(models.JSONSchema.id == schema_id).first()
    if not row:
        raise InheritanceError("Schema not found")

    path: list[UUID] = []
    seen: set[UUID] = set()
    cur: Optional[models.JSONSchema] = row
    depth = 0

    while cur is not None:
        if depth >= INHERITANCE_MAX_DEPTH:
            raise InheritanceError("Schema inheritance chain exceeds maximum depth")
        if cur.id in seen:
            raise InheritanceError("Cycle detected in schema inheritance")
        seen.add(cur.id)
        path.append(cur.id)
        if cur.extends_schema_id is None:
            break
        parent = (
            db.query(models.JSONSchema)
            .filter(models.JSONSchema.id == cur.extends_schema_id)
            .first()
        )
        if not parent:
            raise InheritanceError("Parent schema not found")
        cur = parent
        depth += 1

    return list(reversed(path))


def validate_document_extends(
    db: Session,
    document_id: Optional[UUID],
    parent_id: Optional[UUID],
) -> None:
    if parent_id is None:
        return
    if document_id is not None and parent_id == document_id:
        raise InheritanceError("A document cannot extend itself")

    cur: Optional[UUID] = parent_id
    seen: set[UUID] = set()
    depth = 0

    while cur is not None:
        if depth >= INHERITANCE_MAX_DEPTH:
            raise InheritanceError("Inheritance chain exceeds maximum depth")
        if cur in seen:
            raise InheritanceError("Cycle detected in document inheritance")
        seen.add(cur)
        if document_id is not None and cur == document_id:
            raise InheritanceError("Cannot extend: would create a cycle in document inheritance")
        row = db.query(models.JSONDocument).filter(models.JSONDocument.id == cur).first()
        if not row:
            raise InheritanceError("Parent document not found")
        cur = row.extends_document_id
        depth += 1


def validate_schema_extends(
    db: Session,
    schema_id: Optional[UUID],
    parent_id: Optional[UUID],
) -> None:
    if parent_id is None:
        return
    if schema_id is not None and parent_id == schema_id:
        raise InheritanceError("A schema cannot extend itself")

    cur: Optional[UUID] = parent_id
    seen: set[UUID] = set()
    depth = 0

    while cur is not None:
        if depth >= INHERITANCE_MAX_DEPTH:
            raise InheritanceError("Inheritance chain exceeds maximum depth")
        if cur in seen:
            raise InheritanceError("Cycle detected in schema inheritance")
        seen.add(cur)
        if schema_id is not None and cur == schema_id:
            raise InheritanceError("Cannot extend: would create a cycle in schema inheritance")
        row = db.query(models.JSONSchema).filter(models.JSONSchema.id == cur).first()
        if not row:
            raise InheritanceError("Parent schema not found")
        cur = row.extends_schema_id
        depth += 1
