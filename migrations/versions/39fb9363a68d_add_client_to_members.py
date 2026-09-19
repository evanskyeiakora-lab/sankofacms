"""Add client to members

Revision ID: 39fb9363a68d
Revises: b1c6d1d6db74
Create Date: 2026-09-10 10:13:04.530364

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '39fb9363a68d'
down_revision = 'b1c6d1d6db74'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table(
        'members',
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
            'ix_members_client_id',
            ['client_id'],
            unique=False
        )

        batch_op.create_foreign_key(
            'fk_members_client_id_clients',
            'clients',
            ['client_id'],
            ['id']
        )


def downgrade():

    with op.batch_alter_table(
        'members',
        schema=None
    ) as batch_op:

        batch_op.drop_constraint(
            'fk_members_client_id_clients',
            type_='foreignkey'
        )

        batch_op.drop_index(
            'ix_members_client_id'
        )

        batch_op.drop_column(
            'client_id'
        )