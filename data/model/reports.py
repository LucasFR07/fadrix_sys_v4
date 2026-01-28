from data.config.base import Base
from sqlalchemy import Column, String, Integer, DateTime


class Reports(Base):

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True)
    report_date = Column(DateTime, index=True, nullable=False)
    report_user = Column(String, nullable=False)
    report_type = Column(String, nullable=False)
    report_title = Column(String, nullable=False)
    report_file_extension = Column(String(5), nullable=True)
    report_path = Column(String, nullable=False)

    def __repr__(self):
        return {"id": self.id, "report_date": self.report_date, "report_user": self.report_user, "report_type": self.report_type, "report_title": self.report_title, "report_file_extension": self.report_file_extension, "report_path": self.report_path}

        # return f"Sector(id={self.id!r}, name={self.name!r}, default={self.default!r}, asanaID={self.asanaID!r})"
