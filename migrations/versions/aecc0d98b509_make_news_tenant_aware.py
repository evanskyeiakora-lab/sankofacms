"""Make news tenant aware

Revision ID: aecc0d98b509
Revises: 9d9214a018b5
Create Date: 2026-09-09 15:30:45.562650

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aecc0d98b509'
down_revision = '9d9214a018b5'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        'news',
        schema=None
    ) as batch_op:

        # Add tenant/client reference
        batch_op.add_column(
            sa.Column(
                'client_id',
                sa.Integer(),
                nullable=True
            )
        )

        # Change slug index from UNIQUE to normal index
        batch_op.drop_index(
            'ix_news_slug'
        )

        batch_op.create_index(
            'ix_news_slug',
            ['slug'],
            unique=False
        )

        # Index client_id for tenant queries
        batch_op.create_index(
            'ix_news_client_id',
            ['client_id'],
            unique=False
        )

        # Tenant foreign key
        batch_op.create_foreign_key(
            'fk_news_client_id_clients',
            'clients',
            ['client_id'],
            ['id']
        )


def downgrade():

    with op.batch_alter_table(
        'news',
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            'fk_news_client_id_clients',
            type_='foreignkey'
        )

        batch_op.drop_index(
            'ix_news_client_id'
        )

        batch_op.drop_index(
            'ix_news_slug'
        )

        batch_op.create_index(
            'ix_news_slug',
            ['slug'],
            unique=True
        )

        batch_op.drop_column(
            'client_id'
        )