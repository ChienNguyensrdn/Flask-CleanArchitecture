

from infrastructure.databases.abstract_database import AbstractDatabase
from infrastructure.databases.database_mssql import DatabaseMSSQL
from infrastructure.databases.database_postgres import DatabasePostgres


class FactoryDatabase:
    @staticmethod
    def get_database(database_type)-> AbstractDatabase:
        if database_type == 'MSSQL':
            return DatabaseMSSQL()
        if database_type == 'POSTGREE':
            # Return PostgreSQL database instance
            return DatabasePostgres()
        raise ValueError(f"Unsupported database type: {database_type}") 