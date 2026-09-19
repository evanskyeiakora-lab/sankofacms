"""Add client to pages

Revision ID: 9d9214a018b5
Revises: 9974c445d45e
Create Date: 2026-09-09 14:45:11.126811

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d9214a018b5'
down_revision = '9974c445d45e'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        'pages',
        schema=None
    ) as batch_op:

        batch_op.add_column(
            sa.Column(
                'client_id',
                sa.Integer(),
                nullable=True
            )
        )

        batch_op.create_index(
            'ix_pages_client_id',
            ['client_id'],
            unique=False
        )

        batch_op.create_foreign_key(
            'fk_pages_client_id_clients',
            'clients',
            ['client_id'],
            ['id']
        )


def downgrade():

    with op.batch_alter_table(
        'pages',
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            'fk_pages_client_id_clients',
            type_='foreignkey'
        )

        batch_op.drop_index(
            'ix_pages_client_id'
        )

        batch_op.drop_column(
            'client_id'
        )