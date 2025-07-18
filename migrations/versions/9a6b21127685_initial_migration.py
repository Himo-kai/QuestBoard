"""Initial migration

Revision ID: 9a6b21127685
Revises: 
Create Date: 2025-07-17 21:05:11.952442

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a6b21127685'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tags',
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_tags_name'), ['name'], unique=True)

    op.create_table('users',
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('password_hash', sa.String(length=256), nullable=True),
    sa.Column('avatar_url', sa.String(length=255), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=False),
    sa.Column('email_verified', sa.Boolean(), nullable=False),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('email_verified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_users_email'), ['email'], unique=True)
        batch_op.create_index(batch_op.f('ix_users_is_active'), ['is_active'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_is_admin'), ['is_admin'], unique=False)
        batch_op.create_index(batch_op.f('ix_users_username'), ['username'], unique=True)

    op.create_table('quests',
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('source', sa.String(length=100), nullable=True),
    sa.Column('url', sa.String(length=500), nullable=False),
    sa.Column('difficulty', sa.Float(), nullable=False),
    sa.Column('reward', sa.String(length=200), nullable=False),
    sa.Column('region', sa.String(length=100), nullable=False),
    sa.Column('is_approved', sa.Boolean(), nullable=False),
    sa.Column('posted_date', sa.DateTime(), nullable=False),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('approved_by_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('quests', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_quests_approved_by_id'), ['approved_by_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_creator_id'), ['creator_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_difficulty'), ['difficulty'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_is_approved'), ['is_approved'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_posted_date'), ['posted_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_region'), ['region'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_source'), ['source'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_title'), ['title'], unique=False)
        batch_op.create_index(batch_op.f('ix_quests_url'), ['url'], unique=True)

    op.create_table('quest_tags',
    sa.Column('quest_id', sa.Integer(), nullable=False),
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ),
    sa.PrimaryKeyConstraint('quest_id', 'tag_id'),
    sa.UniqueConstraint('quest_id', 'tag_id', name='uq_quest_tag')
    )
    op.create_table('user_quests',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('quest_id', sa.Integer(), nullable=False),
    sa.Column('bookmarked_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['quest_id'], ['quests.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'quest_id'),
    sa.UniqueConstraint('user_id', 'quest_id', name='uq_user_quest')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_quests')
    op.drop_table('quest_tags')
    with op.batch_alter_table('quests', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_quests_url'))
        batch_op.drop_index(batch_op.f('ix_quests_title'))
        batch_op.drop_index(batch_op.f('ix_quests_source'))
        batch_op.drop_index(batch_op.f('ix_quests_region'))
        batch_op.drop_index(batch_op.f('ix_quests_posted_date'))
        batch_op.drop_index(batch_op.f('ix_quests_is_approved'))
        batch_op.drop_index(batch_op.f('ix_quests_difficulty'))
        batch_op.drop_index(batch_op.f('ix_quests_creator_id'))
        batch_op.drop_index(batch_op.f('ix_quests_approved_by_id'))

    op.drop_table('quests')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_username'))
        batch_op.drop_index(batch_op.f('ix_users_is_admin'))
        batch_op.drop_index(batch_op.f('ix_users_is_active'))
        batch_op.drop_index(batch_op.f('ix_users_email'))

    op.drop_table('users')
    with op.batch_alter_table('tags', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_tags_name'))

    op.drop_table('tags')
    # ### end Alembic commands ###
