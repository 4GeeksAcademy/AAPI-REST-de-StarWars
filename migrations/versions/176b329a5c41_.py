"""empty message

Revision ID: 176b329a5c41
Revises: e3f544c774cb
Create Date: 2025-05-19 16:07:28.682969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '176b329a5c41'
down_revision = 'e3f544c774cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.alter_column('bio',
               existing_type=sa.VARCHAR(length=250),
               nullable=True)
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('profiles', schema=None) as batch_op:
        batch_op.alter_column('user_id',
               existing_type=sa.INTEGER(),
               nullable=False)
        batch_op.alter_column('bio',
               existing_type=sa.VARCHAR(length=250),
               nullable=False)

    # ### end Alembic commands ###
