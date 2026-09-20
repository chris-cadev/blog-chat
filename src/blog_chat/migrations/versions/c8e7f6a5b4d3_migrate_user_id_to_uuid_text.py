"""migrate user id to uuid text and message user_id to text

Revision ID: c8e7f6a5b4d3
Revises: b7d6c1a2e5f4
Create Date: 2026-09-20
"""

from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c8e7f6a5b4d3'
down_revision: Union[str, Sequence[str], None] = 'b7d6c1a2e5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # create users_new with TEXT PK
    op.create_table(
        'users_new',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('alias', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('alias', name='uq_users_alias'),
    )

    # copy users with new uuids
    # use raw select to fetch existing
    result = bind.execute(sa.text("SELECT id, username, alias, ip_address, created_at FROM users"))
    rows = result.fetchall()
    mapping: dict[int, str] = {}
    for r in rows:
        old_id, username, alias, ip_address, created_at = r
        new_id = str(uuid.uuid4())
        mapping[int(old_id)] = new_id
        bind.execute(
            sa.text("INSERT INTO users_new (id, username, alias, ip_address, created_at) VALUES (:id, :username, :alias, :ip, :created_at)"),
            {"id": new_id, "username": username, "alias": alias, "ip": ip_address, "created_at": created_at},
        )

    # create messages_new with TEXT user_id
    op.create_table(
        'messages_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('room_slug', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users_new.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_messages_new_room_slug', 'messages_new', ['room_slug'])
    op.create_index('ix_messages_new_timestamp', 'messages_new', ['timestamp'])

    # copy messages
    result = bind.execute(sa.text("SELECT id, room_slug, user_id, username, content, timestamp, ip_address FROM messages"))
    for r in result.fetchall():
        mid, room_slug, user_id, username, content, timestamp, ip_address = r
        new_user_id = None
        if user_id is not None:
            new_user_id = mapping.get(int(user_id))
        bind.execute(
            sa.text("INSERT INTO messages_new (id, room_slug, user_id, username, content, timestamp, ip_address) VALUES (:id, :room, :uid, :uname, :content, :ts, :ip)"),
            {"id": mid, "room": room_slug, "uid": new_user_id, "uname": username, "content": content, "ts": timestamp, "ip": ip_address},
        )

    # drop old tables and rename
    # need to drop indexes before drop table on sqlite
    # messages indexes were ix_messages_room_slug and ix_messages_timestamp
    try:
        op.drop_index('ix_messages_room_slug', table_name='messages')
    except Exception:
        pass
    try:
        op.drop_index('ix_messages_timestamp', table_name='messages')
    except Exception:
        pass
    op.drop_table('messages')
    op.drop_table('users')
    op.rename_table('users_new', 'users')
    op.rename_table('messages_new', 'messages')
    # rename indexes to expected names
    # sqlite autocreates indexes with new names, ensure we have correct names
    # drop the _new indexes and create proper ones if needed
    try:
        op.drop_index('ix_messages_new_room_slug', table_name='messages')
    except Exception:
        pass
    try:
        op.drop_index('ix_messages_new_timestamp', table_name='messages')
    except Exception:
        pass
    op.create_index(op.f('ix_messages_room_slug'), 'messages', ['room_slug'], unique=False)
    op.create_index(op.f('ix_messages_timestamp'), 'messages', ['timestamp'], unique=False)


def downgrade() -> None:
    # downgrade is lossy (uuid -> int not reversible deterministically)
    # We implement a simple int PK restore by reassigning row_number as new id
    # This is not perfect but allows downgrade for dev.
    bind = op.get_bind()
    # create users_old int
    op.create_table(
        'users_old',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('alias', sa.String(length=50), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('alias', name='uq_users_alias'),
    )
    # copy with row_number
    result = bind.execute(sa.text("SELECT id, username, alias, ip_address, created_at FROM users"))
    rows = result.fetchall()
    mapping: dict[str, int] = {}
    for idx, r in enumerate(rows, start=1):
        old_uuid, username, alias, ip_address, created_at = r
        mapping[str(old_uuid)] = idx
        bind.execute(
            sa.text("INSERT INTO users_old (id, username, alias, ip_address, created_at) VALUES (:id, :username, :alias, :ip, :created_at)"),
            {"id": idx, "username": username, "alias": alias, "ip": ip_address, "created_at": created_at},
        )
    op.create_table(
        'messages_old',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('room_slug', sa.String(length=100), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users_old.id']),
    )
    result = bind.execute(sa.text("SELECT id, room_slug, user_id, username, content, timestamp, ip_address FROM messages"))
    for r in result.fetchall():
        mid, room_slug, user_id, username, content, timestamp, ip_address = r
        new_uid = mapping.get(str(user_id)) if user_id else None
        bind.execute(
            sa.text("INSERT INTO messages_old (id, room_slug, user_id, username, content, timestamp, ip_address) VALUES (:id, :room, :uid, :uname, :content, :ts, :ip)"),
            {"id": mid, "room": room_slug, "uid": new_uid, "uname": username, "content": content, "ts": timestamp, "ip": ip_address},
        )
    try:
        op.drop_index('ix_messages_room_slug', table_name='messages')
    except Exception:
        pass
    try:
        op.drop_index('ix_messages_timestamp', table_name='messages')
    except Exception:
        pass
    op.drop_table('messages')
    op.drop_table('users')
    op.rename_table('users_old', 'users')
    op.rename_table('messages_old', 'messages')
    op.create_index(op.f('ix_messages_room_slug'), 'messages', ['room_slug'], unique=False)
    op.create_index(op.f('ix_messages_timestamp'), 'messages', ['timestamp'], unique=False)
