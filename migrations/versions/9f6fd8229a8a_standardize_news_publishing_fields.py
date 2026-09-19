"""Standardize news publishing fields

Revision ID: 9f6fd8229a8a
Revises: fce4c46db9e2
"""

from alembic import op
import sqlalchemy as sa


# ==========================================================
# REVISION IDENTIFIERS
# ==========================================================

revision = "9f6fd8229a8a"

down_revision = "fce4c46db9e2"

branch_labels = None

depends_on = None


# ==========================================================
# UPGRADE
# ==========================================================

def upgrade():

    # ------------------------------------------------------
    # NEWS
    # ------------------------------------------------------

    with op.batch_alter_table(
        "news",
        schema=None
    ) as batch_op:

        # Add the new publication field.
        #
        # Existing News records are currently zero,
        # so this is safe.

        batch_op.add_column(
            sa.Column(
                "is_published",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()
            )
        )

        # Remove the old publication status field.

        batch_op.drop_column(
            "status"
        )

        # Add index to slug.

        batch_op.create_index(
            batch_op.f("ix_news_slug"),
            ["slug"],
            unique=True
        )


# ==========================================================
# DOWNGRADE
# ==========================================================

def downgrade():

    with op.batch_alter_table(
        "news",
        schema=None
    ) as batch_op:

        # Restore old status field.

        batch_op.add_column(
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=True
            )
        )

        # Remove slug index.

        batch_op.drop_index(
            batch_op.f("ix_news_slug")
        )

        # Remove new publication field.

        batch_op.drop_column(
            "is_published"
        )