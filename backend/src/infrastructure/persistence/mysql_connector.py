from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

class MySQLConnector:
    def __init__(self):
        # Charger les variables d'environnement
        load_dotenv()
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.host = os.getenv("MYSQL_HOST", "localhost")
        self.port = os.getenv("MYSQL_PORT", 3306)
        self.db = os.getenv("MYSQL_DB")
        self.engine = None
        self.Session = None

    def create_db_if_not_exists(self):
        # Connexion au serveur sans DB
        engine = create_engine(f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}")
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{self.db}`"))
            print(f"Database `{self.db}` checked/created.")

    def connect(self):
        # Créer l'engine SQLAlchemy
        connection_string = f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        self.engine = create_engine(connection_string, echo=True)  # echo=True pour debug SQL
        self.Session = sessionmaker(bind=self.engine)
        return self.engine, self.Session

    def get_session(self):
        if not self.Session:
            self.connect()
        return self.Session()