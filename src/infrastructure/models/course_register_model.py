from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from infrastructure.databases.base import Base

class CourseRegisterModel(Base):
    __tablename__ = 'course_register'
    __table_args__ = {'extend_existing': True}  # Thêm dòng này
    
    id = Column(Integer, primary_key=True)
    
    user_id = Column(Integer, ForeignKey('flask_user.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))