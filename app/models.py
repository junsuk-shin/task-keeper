from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship

from app.database import Base

# 할 일과 태그는 다대다 관계입니다.
task_tags = Table(
    "task_tags",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # 기본은 lazy 로딩(select)입니다. 단건 조회에는 이걸로 충분하므로
    # 즉시 로딩은 모델이 아니라 쿼리에서 지정합니다.
    # 여러 Task를 반환하는 조회는 N+1을 피하려고 반드시
    # options(selectinload(Task.tags))를 붙입니다(예: task_service.list_tasks).
    tags = relationship("Tag", secondary=task_tags, lazy="select")
