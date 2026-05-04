# Modelo de utilizador para a base de dados
from sqlalchemy import Column, Integer, String
from database import Base

# Classe modelo para a tabela de utilizadores
class User(Base):
    __tablename__ = 'users'
    
    # ID único do utilizador
    id = Column(Integer, primary_key=True, index=True)
    
    # Email do utilizador único
    email = Column(String(120), unique=True, nullable=False)
    
    # Password encriptada do utilizador
    password = Column(String(255), nullable=False)
    
    # Tipo de utilizador (normal, admin, guest)
    role = Column(String(20), nullable=False, default='normal')
    
    def __repr__(self):
        # Representação string do objeto User
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
