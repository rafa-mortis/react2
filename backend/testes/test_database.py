# Testes para a base de dados e operações SQL
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import User
import hashlib

@pytest.fixture(scope="function")
def db_session():
    # Criar motor de teste em memória para cada teste
    test_engine = create_engine('sqlite:///:memory:', echo=False)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    # Criar tabelas
    Base.metadata.create_all(bind=test_engine)
    
    # Criar sessão
    db = TestSessionLocal()
    
    yield db
    
    # Limpar após o teste
    db.close()
    Base.metadata.drop_all(bind=test_engine)

def test_create_user(db_session):
    # Testar criação de utilizador na base de dados
    db = db_session
    
    # Criar utilizador de teste
    hashed_password = hashlib.sha256('test123'.encode()).hexdigest()
    test_user = User(email='test1@gmail.com', password=hashed_password)
    
    # Adicionar à base de dados
    db.add(test_user)
    db.commit()
    
    # Verificar se utilizador foi criado
    retrieved_user = db.query(User).filter(User.email == 'test1@gmail.com').first()
    
    assert retrieved_user is not None
    assert retrieved_user.email == 'test1@gmail.com'
    assert retrieved_user.password == hashed_password
    
    print(" Teste de criação de utilizador passou")

def test_duplicate_email(db_session):
    # Testar registo de email duplicado
    db = db_session
    
    # Criar primeiro utilizador
    hashed_password = hashlib.sha256('test123'.encode()).hexdigest()
    first_user = User(email='test2@gmail.com', password=hashed_password)
    db.add(first_user)
    db.commit()
    
    # Tentar criar segundo utilizador com mesmo email
    try:
        second_user = User(email='test2@gmail.com', password=hashed_password)
        db.add(second_user)
        db.commit()
        assert False, "Email duplicado não deveria ser criado"
    except Exception as e:
        # Esperado - email duplicado não deve ser permitido
        print(" Teste de email duplicado passou")

if __name__ == '__main__':
    test_create_user()
    test_duplicate_email()
    print(" Todos os testes de base de dados passaram!")
