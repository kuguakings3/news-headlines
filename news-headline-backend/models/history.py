from datetime import datetime

from sqlalchemy import UniqueConstraint, Index, Integer, ForeignKey, DateTime, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from models.news import News
from models.users import User
from models.users import Base    # 复用，不要新建


class History(Base):
    __tablename__ = "history"

    __table_args__ = (
        Index('fk_history_user_idx', 'user_id'),
        Index('fk_history_news_idx', 'news_id'),
        Index('idx_view_time', 'view_time')
    )
    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey(User.id), nullable=False)
    news_id:Mapped[int] = mapped_column(Integer, ForeignKey(News.id), nullable=False)
    view_time:Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<History id={self.id} news_id={self.news_id} view_time={self.view_time}>"