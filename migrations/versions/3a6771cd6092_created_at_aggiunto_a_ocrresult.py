"""created at aggiunto a ocrresult

Revision ID: 3a6771cd6092
Revises: e055a6233136
Create Date: 2024-11-25 10:52:48.255741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3a6771cd6092'
down_revision = 'e055a6233136'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ocr_result', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ocr_result', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###