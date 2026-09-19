"""Add client to users

Revision ID: 7e02195daead
Revises: 39fb9363a68d
Create Date: 2026-09-10 17:29:31.247090

"""

from alembic import op
import sqlalchemy as sa


# ==========================================================
# REVISION IDENTIFIERS
# ==========================================================

revision = "7e02195daead"
down_revision = "39fb9363a68d"
branch_labels = None
depends_on = None


# ==========================================================
# UPGRADE
# ==========================================================

def upgrade():

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        # Add tenant/client column
        batch_op.add_column(
            sa.Column(
                "client_id",
                sa.Integer(),
                nullable=True,
            )
        )

        # Index
        batch_op.create_index(
            "ix_users_client_id",
            ["client_id"],
            unique=False,
        )

        # Named foreign key
        batch_op.create_foreign_key(
            "fk_users_client_id_clients",
            "clients",
            ["client_id"],
            ["id"],
            ondelete="SET NULL",
        )


# ==========================================================
# DOWNGRADE
# ==========================================================

def downgrade():

    with op.batch_alter_table(
        "users",
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_users_client_id_clients",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_users_client_id"
        )

        batch_op.drop_column(
            "client_id"
        )