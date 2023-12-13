"""spec was updated, test was created

Revision ID: 11d7fb364e9e
Revises: c37c16f08ab4
Create Date: 2023-11-29 00:58:30.091874

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11d7fb364e9e'
down_revision: Union[str, None] = 'c37c16f08ab4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
