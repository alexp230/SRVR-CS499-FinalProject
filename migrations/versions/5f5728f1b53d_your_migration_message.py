"""Your migration message

<<<<<<<< HEAD:migrations/versions/2865b8619948_your_migration_message.py
Revision ID: 2865b8619948
Revises: 
Create Date: 2023-11-06 20:23:47.780356
========
Revision ID: 5f5728f1b53d
Revises: 
Create Date: 2023-11-06 20:24:35.454969
>>>>>>>> 7f197e88a0c23996a8c2c8c7308e5a0eb4ddab3c:migrations/versions/5f5728f1b53d_your_migration_message.py

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b06599062522'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
