from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"

DATABASE_NAME = "GrooveR"


# Conexão com o MySQL sem escolher um database
SERVER_URL = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
    f"@{MYSQL_HOST}:{MYSQL_PORT}"
)


# Cria uma conexão com o servidor MySQL
server_engine = create_engine(SERVER_URL)


# Cria o database caso ele não exista
with server_engine.connect() as connection:
    connection.execute(
        text(
            f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"
        )
    )

    connection.commit()


# Agora conecta especificamente no database criado
DATABASE_URL = (
    f"{SERVER_URL}/{DATABASE_NAME}"
)


engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()