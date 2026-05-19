from sqlalchemy.orm import Session

from models.channel import Channel
from repositories.Lookup import Lookup
from repositories.repository import Repository


class ChannelRepository(Repository, Lookup):
    model = Channel

    def __init__(self, session: Session):
        Repository.__init__(self, session)
        Lookup.__init__(self, self, "name")

    def add(self, name: str, description: str) -> Channel:
        channel = Channel(name=name, description=description)
        self.session.add(channel)
        self.session.commit()
        self.session.refresh(channel)
        self.session.expunge(channel)
        self._data[channel.name] = channel
        return channel
