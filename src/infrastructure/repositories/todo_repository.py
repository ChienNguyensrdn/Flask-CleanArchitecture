from domain.models.itodo_repository import ITodoRepository
from domain.models.todo import Todo
from typing import List, Optional
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config
from sqlalchemy import Column, Integer, String, DateTime
from infrastructure.databases import Base
from sqlalchemy.orm import Session
from infrastructure.models.todo_model import TodoModel
from infrastructure.databases.mssql import session
from infrastructure.databases.factory_database import FactoryDatabase as db_factory
load_dotenv()

class TodoRepository(ITodoRepository):
    def __init__(self, session: Session = db_factory.get_database('POSTGREE').session):
        self._todos = []
        self._id_counter = 1
        self.session = db_factory.get_database('POSTGREE').session

    def add(self, todo: Todo) -> TodoModel:
        try:
            #Manual mapping from Todo to TodoModel
            todo = TodoModel(
                title=todo.title,
                description=todo.description,
                status=todo.status,
                created_at=todo.created_at,
                updated_at=todo.updated_at
            )
            self.session.add(todo)
            self.session.commit()
            self.session.refresh(todo)
            return todo
        except Exception as e:
            self.session.rollback()
            raise ValueError('Todo not found')
        finally:
            self.session.close()
    
    # def add(self, todo: Todo) -> Todo:
    #     todo.id = self._id_counter
    #     self._id_counter += 1
    #     self._todos.append(todo)
    #     return todo

    def get_by_id(self, todo_id: int) -> Optional[TodoModel]:
        return self.session.query(TodoModel).filter_by(id=todo_id).first()


    # def list(self) -> List[Todo]:
    #     self._todos
    #     return self._todos
    def list(self) -> List[TodoModel]:
        self._todos = session.query(TodoModel).all()
        # select * from todos
        return self._todos


    def update(self, todo: TodoModel) -> TodoModel:
        try:
             #Manual mapping from Todo to TodoModel
            todo = TodoModel(
                id = todo.id,
                title=todo.title,
                description=todo.description,
                status=todo.status,
                created_at=todo.created_at,
                updated_at=todo.updated_at
            )
            self.session.merge(todo)
            self.session.commit()
            return todo
        except Exception as e:
            self.session.rollback()
            raise ValueError('Todo not found')
        finally:
            self.session.close()

    def delete(self, todo_id: int) -> None:
        # self._todos = [t for t in self._todos if t.id != todo_id] 
        try:
            todo = self.session.query(TodoModel).filter_by(id=todo_id).first()
            if todo:
                self.session.delete(todo)
                self.session.commit()
            else:
                raise ValueError('Todo not found')
        except Exception as e:
            self.session.rollback()
            raise ValueError('Todo not found')
        finally:
            self.session.close()

