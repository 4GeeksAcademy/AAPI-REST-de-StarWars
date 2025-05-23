"""empty message

Revision ID: e3f544c774cb
Revises: 0f1203c85518
Create Date: 2025-05-13 17:03:56.797861

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f544c774cb'
down_revision = '0f1203c85518'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profiles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('bio', sa.String(length=250), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('profile')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('profile',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('bio', sa.VARCHAR(length=250), autoincrement=False, nullable=False),
    sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='profile_user_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='profile_pkey')
    )
    op.drop_table('profiles')
    # ### end Alembic commands ###
