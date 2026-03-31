"""add document and schema inheritance foreign keys

Revision ID: 001_inherit
Revises:
Create Date: 2026-03-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_inherit"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "json_documents",
        sa.Column("extends_document_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_json_documents_extends_document_id",
        "json_documents",
        "json_documents",
        ["extends_document_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.add_column(
        "json_schemas",
        sa.Column("extends_schema_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_json_schemas_extends_schema_id",
        "json_schemas",
        "json_schemas",
        ["extends_schema_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_json_schemas_extends_schema_id", "json_schemas", type_="foreignkey"
    )
    op.drop_column("json_schemas", "extends_schema_id")
    op.drop_constraint(
        "fk_json_documents_extends_document_id", "json_documents", type_="foreignkey"
    )
    op.drop_column("json_documents", "extends_document_id")
