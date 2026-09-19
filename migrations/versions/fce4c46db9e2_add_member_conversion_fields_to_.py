"""Add member conversion fields to membership applications

Revision ID: fce4c46db9e2
Revises: 62c35452bafa
Create Date: 2026-08-27
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers
revision = "fce4c46db9e2"
down_revision = "62c35452bafa"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "membership_applications",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "is_converted",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0")
            )
        )

        batch_op.add_column(
            sa.Column(
                "member_id",
                sa.Integer(),
                nullable=True
            )
        )


def downgrade():

    with op.batch_alter_table(
        "membership_applications",
        schema=None
    ) as batch_op:

        batch_op.drop_column(
            "member_id"
        )

        batch_op.drop_column(
            "is_converted"
        )