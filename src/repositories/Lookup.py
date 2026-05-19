from __future__ import annotations

from typing import TYPE_CHECKING

import datetime

from models import Base

if TYPE_CHECKING:
    from repositories.repository import Repository


class Lookup:
    _data: dict[str, Base]
    key_col: str

    def __init__(self, repo: Repository, key_col: str) -> None:
        self._data = {}
        self.key_col = key_col
        data = repo.get_all()
        for d in data:
            key = getattr(d, self.key_col)
            self._data[key] = d

    def get_by_name(self, name: str) -> Base:
        result = next(d for k, d in self._data.items() if k == name)
        return result
