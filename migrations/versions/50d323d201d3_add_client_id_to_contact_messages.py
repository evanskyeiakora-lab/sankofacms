
"""Add client ID to contact messages

Revision ID: 50d323d201d3
Revises: e94746576b65
"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "50d323d201d3"
down_revision = "e94746576b65"
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        "contact_messages",
        schema=None,
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                "client_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_index(
            "ix_contact_messages_client_id",
            ["client_id"],
            unique=False,
        )

        batch_op.create_foreign_key(
            "fk_contact_messages_client_id_clients",
            "clients",
            ["client_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade():

    with op.batch_alter_table(
        "contact_messages",
        schema=None,
    ) as batch_op:

        batch_op.drop_constraint(
            "fk_contact_messages_client_id_clients",
            type_="foreignkey",
        )

        batch_op.drop_index(
            "ix_contact_messages_client_id",
        )

        batch_op.drop_column(
            "client_id",
        )