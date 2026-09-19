"""Add client to settings

Revision ID: 03dfc8f597b8
Revises: c5f5bd633420
Create Date: 2026-09-08 17:42:24.567048

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "03dfc8f597b8"
down_revision = "c5f5bd633420"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table("settings", schema=None) as batch_op:

        batch_op.add_column(
            sa.Column(
                "client_id",
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            "uq_settings_client_id",
            ["client_id"]
        )

        batch_op.create_foreign_key(
            "fk_settings_client_id_clients",
            "clients",
            ["client_id"],
            ["id"]
        )


def downgrade():

    with op.batch_alter_table("settings", schema=None) as batch_op:

        batch_op.drop_constraint(
            "fk_settings_client_id_clients",
            type_="foreignkey"
        )

        batch_op.drop_constraint(
            "uq_settings_client_id",
            type_="unique"
        )

        batch_op.drop_column("client_id")