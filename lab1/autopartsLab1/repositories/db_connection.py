import mysql.connector

class DBConnection:
    """
    кто такие скоморохи?
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, host="localhost", port=3306, user="root",
                 password="", database="autoparts"):
        if self._initialized:
            return
        self._config = dict(
            host=host, port=port, user=user,
            password=password, database=database,
        )
        self._conn = None
        self._initialized = True

    def connect(self):
        if self._conn is None or not self._conn.is_connected():
            self._conn = mysql.connector.connect(**self._config)
        return self._conn

    def fetch_all(self, query: str, params=None) -> list[dict]:
        cursor = self.connect().cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchall()

    def fetch_one(self, query: str, params=None) -> dict | None:
        cursor = self.connect().cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor.fetchone()

    def execute_commit(self, query: str, params=None) -> int:
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return cursor.lastrowid

    def close(self):
        if self._conn is not None and self._conn.is_connected():
            self._conn.close()
            self._conn = None