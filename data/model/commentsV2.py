from data.config.base import Base
from sqlalchemy import Column, String, Integer, DateTime


class CommentsV2(Base):

    __tablename__ = "commentsv2"

    id = Column(Integer, primary_key=True)
    sign = Column(String, nullable=True)
    module = Column(String(30), nullable=False)
    reference = Column(String(30), nullable=False)

    user = Column(String(30), nullable=False)
    date = Column(DateTime, index=True, nullable=False)

    type_msg = Column(String(30), nullable=False)
    text = Column(String, nullable=True)
    sticker = Column(String, nullable=True)
    image = Column(String, nullable=True)
    audio = Column(String, nullable=True)
    video = Column(String, nullable=True)
    attachment = Column(String, nullable=True)

    reply = Column(Integer, nullable=True)


    def __repr__(self):
        return f"CommentsV2(id={self.id!r}, sign={self.sign!r}, module={self.module!r}, reference={self.reference!r}, user={self.user!r}, date={self.date!r}, type_msg={self.type_msg!r}, text={self.text!r}, sticker={self.sticker!r}, image={self.image!r}, audio={self.audio!r}, video={self.video!r}, attachment={self.attachment!r}, reply={self.reply!r})"
