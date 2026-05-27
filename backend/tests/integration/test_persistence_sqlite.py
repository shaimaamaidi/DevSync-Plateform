"""
Integration test for persistence using an in-memory SQLite engine.

This test patches `MySQLConnector`'s `create_engine` to return a
SQLite in-memory engine so we can validate session creation and
basic CRUD without a real MySQL server.
"""

from sqlalchemy import text, create_engine as real_create_engine


def test_mysql_connector_works_with_sqlite(monkeypatch):
    # Prevent loading repo .env
    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.load_dotenv", lambda *a, **k: True)

    monkeypatch.setenv("MYSQL_USER", "u")
    monkeypatch.setenv("MYSQL_PASSWORD", "p")
    monkeypatch.setenv("MYSQL_HOST", "local")
    monkeypatch.setenv("MYSQL_PORT", "0")
    monkeypatch.setenv("MYSQL_DB", "devsync")

    def fake_create_engine(conn_str, echo=False, connect_args=None):
        return real_create_engine("sqlite:///:memory:")

    monkeypatch.setattr("backend.src.infrastructure.persistence.mysql_connector.create_engine", fake_create_engine)

    from backend.src.infrastructure.persistence.mysql_connector import MySQLConnector

    connector = MySQLConnector()

    engine, Session = connector.connect()

    sess = connector.get_session()

    sess.execute(text("CREATE TABLE demo (id INTEGER PRIMARY KEY, name TEXT)"))
    sess.execute(text("INSERT INTO demo (name) VALUES ('alpha')"))
    sess.commit()

    result = sess.execute(text("SELECT count(*) FROM demo")).scalar()
    assert result == 1

    connector.close()
