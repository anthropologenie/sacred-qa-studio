from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_campaign_lineage_table'
down_revision = None  # or your last migration revision id
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'campaign_lineage',
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('brand_sankalpa', sa.Text(), nullable=False),
        sa.Column('copy_iterations', postgresql.JSONB(), server_default='{}'),
        sa.Column('trust_score_evolution', postgresql.JSONB(), server_default='{}'),
        sa.Column('consciousness_impact', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        schema='app'  # optional, remove if you don’t use schema prefix
    )

def downgrade():
    op.drop_table('campaign_lineage', schema='app')
