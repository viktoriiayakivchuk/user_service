"""Initial migration

Revision ID: 6fcddb91eccf
Revises: 
Create Date: 2026-05-22 20:31:26.736993

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6fcddb91eccf'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Create roles table if it doesn't exist
    if 'roles' not in tables:
        roles_table = op.create_table(
            'roles',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('name', sa.String(length=50), nullable=False),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('name')
        )
        # Seed default roles
        op.bulk_insert(
            roles_table,
            [
                {'name': 'Student', 'description': 'Default role for enrolled platform consumers'},
                {'name': 'Instructor', 'description': 'Role for content creators and managers'},
                {'name': 'Admin', 'description': 'Platform administrator with account management authorities'}
            ]
        )

    # 2. Create users table if it doesn't exist
    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.Column('role_id', sa.Integer(), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 3. Create profiles table if it doesn't exist
    if 'profiles' not in tables:
        op.create_table(
            'profiles',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('first_name', sa.String(length=50), nullable=False),
            sa.Column('last_name', sa.String(length=50), nullable=False),
            sa.Column('avatar_url', sa.String(length=255), nullable=True),
            sa.Column('bio', sa.Text(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id')
        )


def downgrade() -> None:
    """Downgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'profiles' in tables:
        op.drop_table('profiles')
    if 'users' in tables:
        op.drop_index(op.f('ix_users_email'), table_name='users')
        op.drop_table('users')
    if 'roles' in tables:
        op.drop_table('roles')
