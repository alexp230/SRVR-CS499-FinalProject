"""empty message

Revision ID: b3aa5ce93035
Revises: cef0d88f4672
Create Date: 2023-11-07 10:40:27.582016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b3aa5ce93035'
down_revision = 'cef0d88f4672'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meals', schema=None) as batch_op:
        batch_op.add_column(sa.Column('instructions', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('meals', schema=None) as batch_op:
        batch_op.drop_column('instructions')

    # ### end Alembic commands ###
