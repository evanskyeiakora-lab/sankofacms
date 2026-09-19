"""Add client to membership applications

Revision ID: e94746576b65
Revises: 7e02195daead
Create Date: 2026-09-11 09:36:27.863492

"""

from alembic import op
import sqlalchemy as sa


# ==========================================================
# REVISION IDENTIFIERS
# ==========================================================

revision = "e94746576b65"
down_revision = "7e02195daead"
branch_labels = None
depends_on = None


# ==========================================================
# UPGRADE
# ==========================================================

def upgrade():

    with op.batch_alter_table(
        "membership_applications",
        schema=None
    ) as batch_op:

        # --------------------------------------------------
        # CLIENT ID
        # --------------------------------------------------

        batch_op.add_column(
            sa.Column(
                "client_id",
                sa.Integer(),
                nullable=True,
            )
        )

        # --------------------------------------------------
        # INDEX
        # --------------------------------------------------

        batch_op.create_index(
            "ix_membership_applications_client_id",
            ["client_id"],
            unique=False,
        )

        # --------------------------------------------------
        # FOREIGN KEY
        # --------------------------------------------------

        batch_op.create_foreign_key(
            "fk_membership_applications_client_id_clients",
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
        "membership_applications",
        schema=None
    ) as batch_op:

        # --------------------------------------------------
        # FOREIGN KEY
        # --------------------------------------------------

        batch_op.drop_constraint(
            "fk_membership_applications_client_id_clients",
            type_="foreignkey",
        )

        # --------------------------------------------------
        # INDEX
        # --------------------------------------------------

        batch_op.drop_index(
            "ix_membership_applications_client_id"
        )

        # --------------------------------------------------
        # CLIENT ID
        # --------------------------------------------------

        batch_op.drop_column(
            "client_id"
        )