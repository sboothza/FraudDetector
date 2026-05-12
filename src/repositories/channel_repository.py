from sqlalchemy.orm import Session

from models.channel import Channel
from repositories.repository import Repository


class ChannelRepository(Repository):
    model = Channel


    def add(self, name:str, description:str):
        self.session.add(Channel(name=name, description=description))