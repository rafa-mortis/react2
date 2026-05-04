# Configuração da base de dados com SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Criar motor da base de dados SQLite
engine = create_engine('sqlite:///users.db', echo=True)

# Criar sessão da base de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Session = SessionLocal()

# Base declarativa para modelos
Base = declarative_base()

# Função para obter sessão da base de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
