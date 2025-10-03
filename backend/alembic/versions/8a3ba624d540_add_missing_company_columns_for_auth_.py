"""Add missing company columns for auth and SSO

Revision ID: 8a3ba624d540
Revises: 0001
Create Date: 2025-10-02 05:39:55.650337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8a3ba624d540'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing columns to companies table
    op.add_column('companies', sa.Column('auth_provider', sa.String(50), nullable=False, server_default='local'))
    op.add_column('companies', sa.Column('azure_tenant_id', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('azure_domain', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('ldap_domain', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('saml_entity_id', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('sso_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('companies', sa.Column('auto_provision_users', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('companies', sa.Column('data_processing_consent', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('companies', sa.Column('popia_consent_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('companies', sa.Column('privacy_policy_accepted', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('companies', sa.Column('privacy_policy_version', sa.String(10), nullable=True))
    op.add_column('companies', sa.Column('data_retention_period', sa.Integer(), nullable=False, server_default='7'))
    op.add_column('companies', sa.Column('popia_compliance_officer', sa.String(255), nullable=True))
    op.add_column('companies', sa.Column('popia_compliance_email', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove the added columns
    op.drop_column('companies', 'popia_compliance_email')
    op.drop_column('companies', 'popia_compliance_officer')
    op.drop_column('companies', 'data_retention_period')
    op.drop_column('companies', 'privacy_policy_version')
    op.drop_column('companies', 'privacy_policy_accepted')
    op.drop_column('companies', 'popia_consent_date')
    op.drop_column('companies', 'data_processing_consent')
    op.drop_column('companies', 'auto_provision_users')
    op.drop_column('companies', 'sso_enabled')
    op.drop_column('companies', 'saml_entity_id')
    op.drop_column('companies', 'ldap_domain')
    op.drop_column('companies', 'azure_domain')
    op.drop_column('companies', 'azure_tenant_id')
    op.drop_column('companies', 'auth_provider')
