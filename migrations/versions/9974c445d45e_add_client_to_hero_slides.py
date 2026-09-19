"""Add client to hero slides

Revision ID: 9974c445d45e
Revises: 03dfc8f597b8
Create Date: 2026-09-08
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9974c445d45e'
down_revision = '03dfc8f597b8'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        'hero_slides',
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
            'ix_hero_slides_client_id',
            ['client_id'],
            unique=False
        )

        batch_op.create_foreign_key(
            'fk_hero_slides_client_id_clients',
            'clients',
            ['client_id'],
            ['id']
        )


def downgrade():

    with op.batch_alter_table(
        'hero_slides',
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            'fk_hero_slides_client_id_clients',
            type_='foreignkey'
        )

        batch_op.drop_index(
            'ix_hero_slides_client_id'
        )

        batch_op.drop_column(
            'client_id'
        )