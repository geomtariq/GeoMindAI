import oracledb
from src.config import settings

class OracleGateway:
    def __init__(self):
        self.pool = oracledb.create_pool(
            user=settings.oracle_user,
            password=settings.oracle_password,
            dsn=settings.oracle_dsn,
            min=2,
            max=5,
            increment=1
        )

    def execute_query(self, sql: str) -> list[dict]:
        """
        Executes a SQL query and returns the results as a list of dictionaries.
        """
        with self.pool.acquire() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                cursor.rowfactory = lambda *args: dict(zip(columns, args))
                return cursor.fetchall()

oracle_gateway = OracleGateway()
