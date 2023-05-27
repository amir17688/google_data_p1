"""switching owner_id to str

Revision ID: 143201389156
Revises: 136275e06649
Create Date: 2014-09-08 15:15:45.393535

"""

# revision identifiers, used by Alembic.
revision = '143201389156'
down_revision = '136275e06649'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("bundle", 'owner_id', type_=sa.String(255), existing_type=sa.Integer(), nullable=True)
    op.alter_column("worksheet", 'owner_id', type_=sa.String(255), existing_type=sa.Integer(), nullable=True)
    op.alter_column("group", 'owner_id', type_=sa.String(255), existing_type=sa.Integer(), nullable=True)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("bundle", 'owner_id', type_=sa.Integer(), existing_type=sa.String(255), nullable=True)
    op.alter_column("worksheet", 'owner_id', type_=sa.Integer(), existing_type=sa.String(255), nullable=True)
    op.alter_column("group", 'owner_id', type_=sa.Integer(), existing_type=sa.String(255), nullable=True)
    ### end Alembic commands ###
