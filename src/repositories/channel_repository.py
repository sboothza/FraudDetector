from sqlalchemy.orm import Session

from models.channel import Channel
from repositories.repository import Repository


class ChannelRepository(Repository):
    model = Channel


    def add(self, name:str, description:str)->Channel:
        channel=Channel(name=name, description=description)
        self.session.add(channel)
        self.session.commit()
        self.session.expunge(channel)
        return channel