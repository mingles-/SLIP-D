"""empty message

Revision ID: 3c1107bed5e9
Revises: 4a7cc09bd8d2
Create Date: 2015-11-10 17:17:03.462387

"""

# revision identifiers, used by Alembic.
revision = '3c1107bed5e9'
down_revision = '4a7cc09bd8d2'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lock', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('lock', 'name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    ### end Alembic commands ###
