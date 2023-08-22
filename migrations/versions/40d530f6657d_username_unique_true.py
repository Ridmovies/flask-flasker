"""username unique=True

Revision ID: 40d530f6657d
Revises: 0ed377a5c1dd
Create Date: 2023-08-16 13:26:19.469688

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40d530f6657d'
down_revision = '0ed377a5c1dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint(batch_op.f('uq_users_email'), ['email'])
        batch_op.create_unique_constraint(batch_op.f('uq_users_username'), ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_users_username'), type_='unique')
        batch_op.drop_constraint(batch_op.f('uq_users_email'), type_='unique')

    # ### end Alembic commands ###
