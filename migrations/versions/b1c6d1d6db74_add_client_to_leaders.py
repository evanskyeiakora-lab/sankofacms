"""Add client to leaders

Revision ID: b1c6d1d6db74
Revises: 36942623b801
Create Date: 2026-09-09

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b1c6d1d6db74"
down_revision = "8cd81dd4453e"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "leaders",
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "client_id",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_index(
            "ix_leaders_client_id",
            ["client_id"],
            unique=False
        )

        batch_op.create_foreign_key(
            "fk_leaders_client_id_clients",
            "clients",
            ["client_id"],
            ["id"]
        )


def downgrade():

    with op.batch_alter_table(
        "leaders",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_leaders_client_id_clients",
            type_="foreignkey"
        )

        batch_op.drop_index(
            "ix_leaders_client_id"
        )

        batch_op.drop_column(
            "client_id"
        )