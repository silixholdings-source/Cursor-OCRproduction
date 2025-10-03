"""Add missing user columns for SSO and enterprise auth

Revision ID: 8a3ba624d541
Revises: 8a3ba624d540
Create Date: 2025-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a3ba624d541'
down_revision = '8a3ba624d540'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to users table for SSO and enterprise auth
    op.add_column('users', sa.Column('auth_provider', sa.String(50), nullable=False, server_default='local'))
    op.add_column('users', sa.Column('azure_ad_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('azure_tenant_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('ldap_dn', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('saml_name_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('sso_session_id', sa.String(255), nullable=True))
    
    # Add extended profile fields from SSO
    op.add_column('users', sa.Column('job_title', sa.String(200), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(200), nullable=True))
    op.add_column('users', sa.Column('office_location', sa.String(200), nullable=True))
    op.add_column('users', sa.Column('manager_email', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('users', 'manager_email')
    op.drop_column('users', 'office_location')
    op.drop_column('users', 'department')
    op.drop_column('users', 'job_title')
    op.drop_column('users', 'sso_session_id')
    op.drop_column('users', 'saml_name_id')
    op.drop_column('users', 'ldap_dn')
    op.drop_column('users', 'azure_tenant_id')
    op.drop_column('users', 'azure_ad_id')
    op.drop_column('users', 'auth_provider')






