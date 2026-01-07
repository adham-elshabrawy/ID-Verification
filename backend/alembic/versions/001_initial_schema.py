"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create locations table
    op.create_table(
        'locations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False, unique=True),
        sa.Column('manager_email', sa.String(), nullable=False),
        sa.Column('export_time', sa.Time(), nullable=False),
        sa.Column('timezone', sa.String(), nullable=False, server_default='America/Toronto'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )
    
    # Create devices table
    op.create_table(
        'devices',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('device_id', sa.String(), nullable=False, unique=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('api_key', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('registered_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_seen_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    )
    
    # Create employees table
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employee_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('pin_hash', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.UniqueConstraint('location_id', 'employee_id', name='uq_location_employee_id'),
    )
    
    # Create face_embeddings table
    op.create_table(
        'face_embeddings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('embedding_encrypted', postgresql.BYTEA(), nullable=False),
        sa.Column('encryption_key_id', sa.String(), nullable=False, server_default='v1'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    )
    
    # Create time_events table
    op.create_table(
        'time_events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('event_time', sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('method', sa.String(), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
    )
    
    # Create settings table
    op.create_table(
        'settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('location_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['location_id'], ['locations.id'], ),
        sa.UniqueConstraint('location_id', 'key', name='uq_location_key'),
    )


def downgrade() -> None:
    op.drop_table('settings')
    op.drop_table('time_events')
    op.drop_table('face_embeddings')
    op.drop_table('employees')
    op.drop_table('devices')
    op.drop_table('locations')

