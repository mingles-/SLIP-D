"""empty message

Revision ID: 4a7cc09bd8d2
Revises: 34431ad060db
Create Date: 2015-11-10 16:50:25.042982

"""

# revision identifiers, used by Alembic.
revision = '4a7cc09bd8d2'
down_revision = '34431ad060db'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('user', 'first_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('user', 'last_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.alter_column('user', 'password',
               existing_type=sa.VARCHAR(length=255),
               nullable=False)
    op.drop_constraint(u'user_first_name_key', 'user', type_='unique')
    op.drop_constraint(u'user_last_name_key', 'user', type_='unique')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(u'user_last_name_key', 'user', ['last_name'])
    op.create_unique_constraint(u'user_first_name_key', 'user', ['first_name'])
    op.alter_column('user', 'password',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('user', 'last_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('user', 'first_name',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    op.alter_column('user', 'email',
               existing_type=sa.VARCHAR(length=255),
               nullable=True)
    ### end Alembic commands ###
