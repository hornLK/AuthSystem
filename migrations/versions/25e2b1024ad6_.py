"""empty message

Revision ID: 25e2b1024ad6
Revises: e1db03176ef8
Create Date: 2018-03-10 08:51:25.507530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25e2b1024ad6'
down_revision = 'e1db03176ef8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('userkeys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('userPubkey', sa.String(length=256), nullable=True),
    sa.Column('userPrikey', sa.String(length=256), nullable=True),
    sa.Column('keyUpdate', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('userkeys')
    # ### end Alembic commands ###
