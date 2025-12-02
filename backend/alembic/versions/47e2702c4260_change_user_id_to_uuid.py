"""change_user_id_to_uuid

Revision ID: 47e2702c4260
Revises: 32f4a7baf3a2
Create Date: 2025-12-02 19:54:43.247612

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '47e2702c4260'
down_revision: Union[str, None] = '32f4a7baf3a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop foreign key constraints first
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('projects_user_id_fkey', 'projects', type_='foreignkey')

    # Drop the sequence used by users.id (if exists)
    op.execute("DROP SEQUENCE IF EXISTS users_id_seq CASCADE")

    # Add new UUID columns
    op.add_column('users', sa.Column('new_id', UUID(as_uuid=True), nullable=True))
    op.add_column('conversations', sa.Column('new_user_id', UUID(as_uuid=True), nullable=True))
    op.add_column('projects', sa.Column('new_user_id', UUID(as_uuid=True), nullable=True))

    # Generate UUIDs for existing users and update references
    op.execute("""
        UPDATE users SET new_id = gen_random_uuid();
    """)
    op.execute("""
        UPDATE conversations c
        SET new_user_id = u.new_id
        FROM users u
        WHERE c.user_id = u.id;
    """)
    op.execute("""
        UPDATE projects p
        SET new_user_id = u.new_id
        FROM users u
        WHERE p.user_id = u.id;
    """)

    # Drop old columns
    op.drop_column('conversations', 'user_id')
    op.drop_column('projects', 'user_id')
    op.drop_column('users', 'id')

    # Rename new columns
    op.alter_column('users', 'new_id', new_column_name='id', nullable=False)
    op.alter_column('conversations', 'new_user_id', new_column_name='user_id', nullable=False)
    op.alter_column('projects', 'new_user_id', new_column_name='user_id', nullable=False)

    # Add primary key constraint
    op.create_primary_key('users_pkey', 'users', ['id'])

    # Recreate indexes
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

    # Recreate foreign key constraints
    op.create_foreign_key(
        'conversations_user_id_fkey', 'conversations', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'projects_user_id_fkey', 'projects', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    # This is a destructive migration, downgrade will lose data
    # Drop foreign key constraints
    op.drop_constraint('conversations_user_id_fkey', 'conversations', type_='foreignkey')
    op.drop_constraint('projects_user_id_fkey', 'projects', type_='foreignkey')

    # Drop indexes
    op.drop_index('ix_conversations_user_id', 'conversations')
    op.drop_index('ix_projects_user_id', 'projects')

    # Add new int columns
    op.add_column('users', sa.Column('new_id', sa.INTEGER(), autoincrement=True, nullable=True))
    op.add_column('conversations', sa.Column('new_user_id', sa.INTEGER(), nullable=True))
    op.add_column('projects', sa.Column('new_user_id', sa.INTEGER(), nullable=True))

    # Create sequence for auto-increment
    op.execute("CREATE SEQUENCE users_id_seq")
    op.execute("SELECT setval('users_id_seq', 1)")

    # Assign sequential IDs
    op.execute("""
        UPDATE users SET new_id = nextval('users_id_seq');
    """)

    # Update references (this will lose the original UUID mapping)
    op.execute("""
        WITH user_mapping AS (
            SELECT id as uuid_id, new_id as int_id FROM users
        )
        UPDATE conversations c
        SET new_user_id = um.int_id
        FROM user_mapping um
        WHERE c.user_id = um.uuid_id;
    """)
    op.execute("""
        WITH user_mapping AS (
            SELECT id as uuid_id, new_id as int_id FROM users
        )
        UPDATE projects p
        SET new_user_id = um.int_id
        FROM user_mapping um
        WHERE p.user_id = um.uuid_id;
    """)

    # Drop old columns
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_column('conversations', 'user_id')
    op.drop_column('projects', 'user_id')
    op.drop_column('users', 'id')

    # Rename new columns
    op.alter_column('users', 'new_id', new_column_name='id', nullable=False)
    op.alter_column('conversations', 'new_user_id', new_column_name='user_id', nullable=False)
    op.alter_column('projects', 'new_user_id', new_column_name='user_id', nullable=False)

    # Set default for auto-increment
    op.execute("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')")
    op.execute("ALTER SEQUENCE users_id_seq OWNED BY users.id")

    # Add primary key
    op.create_primary_key('users_pkey', 'users', ['id'])

    # Recreate indexes
    op.create_index('ix_conversations_user_id', 'conversations', ['user_id'])
    op.create_index('ix_projects_user_id', 'projects', ['user_id'])

    # Recreate foreign key constraints
    op.create_foreign_key(
        'conversations_user_id_fkey', 'conversations', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
    op.create_foreign_key(
        'projects_user_id_fkey', 'projects', 'users',
        ['user_id'], ['id'], ondelete='CASCADE'
    )
