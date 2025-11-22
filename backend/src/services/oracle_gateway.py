import oracledb
from threading import Lock

class OracleGateway:
    def __init__(self):
        self._pools = {}
        self._lock = Lock()

    def create_pool_for_session(self, session_id: str, db_config: dict):
        """Creates and stores a connection pool for a given session."""
        dsn = f"{db_config['host']}:{db_config['port']}/{db_config['service_name']}"
        with self._lock:
            # Close existing pool if any
            if session_id in self._pools:
                self._pools[session_id].close()
            
            self._pools[session_id] = oracledb.create_pool(
                user=db_config['user'],
                password=db_config['password'],
                dsn=dsn,
                min=2, max=5, increment=1, thin=True
            )

    def execute_query(self, session_id: str, sql: str) -> list[dict]:
        """Executes a query using the session's specific connection pool."""
        pool = self._pools.get(session_id)
        if not pool:
            raise ValueError("No database connection for this session.")

        with pool.acquire() as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                columns = [col[0] for col in cursor.description]
                cursor.rowfactory = lambda *args: dict(zip(columns, args))
                return cursor.fetchall()

oracle_gateway = OracleGateway()
