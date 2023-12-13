"""The linters were applied

Revision ID: 9e177d6825dd
Revises: 11d7fb364e9e
Create Date: 2023-11-29 01:34:47.035518

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9e177d6825dd'
down_revision: Union[str, None] = '11d7fb364e9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
