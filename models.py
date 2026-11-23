from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, ForeignKey, select, Date)
from sqlalchemy.sql import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import (
    relationship, declarative_base, sessionmaker, scoped_session, DeclarativeBase)

import os
from dotenv import load_dotenv
import hmac
import hashlib
from datetime import datetime
from cryptography.fernet import Fernet

load_dotenv()

FERNET_KEY = os.getenv("FERNET_KEY")
CPF_HASH_KEY = os.getenv("CPF_HASH_KEY")

fernet = Fernet(FERNET_KEY.encode())
CPF_HASH_KEY = CPF_HASH_KEY.encode()

# create an engine to connect to the database
engine = create_engine('sqlite:///saep_db.db', echo=False)

# create a base class for declarative class definitions
#Base = declarative_base()
class Base(DeclarativeBase):
    pass

# create a scoped session to manage database sessions
db_session = scoped_session(sessionmaker(bind=engine))


# define the User model
class Usuario(Base, UserMixin):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    criado_em = Column(DateTime, server_default=func.now())
    # ---------------------
    # Senha
    # ---------------------

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)


class Tutor(Base):
    __tablename__ = 'tutores'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    telefone = Column(String(20), nullable=False)

    #cpf_masc = Column(String(14), nullable=False)
    cpf_hash = Column(String(64),unique=True,nullable=False)
    cpf_criptografado = Column(String(500), nullable=False)

    criado_em = Column( DateTime, server_default=func.now()
    )

    pet_join = relationship(
        'Pet',
        back_populates='tutor_join'
    )

    # ==========================================
    # NORMALIZAÇÃO DO CPF
    # ==========================================

    @staticmethod
    def limpar_cpf(cpf):
        if not isinstance(cpf, str):
            raise ValueError("CPF deve ser uma string")

        return "".join(filter(str.isdigit, cpf))

    @staticmethod
    def validar_formato_cpf(cpf):

        cpf = Tutor.limpar_cpf(cpf)
        if len(cpf) != 11:
            return False
        if cpf == cpf[0] * 11:
            return False
        numeros = [int(d) for d in cpf]
        # Primeiro dígito verificador
        soma = sum( numeros[i] * (10 - i)
                    for i in range(9) )

        digito1 = (soma * 10 % 11) % 10
        if digito1 != numeros[9]:
            return False

        # Segundo dígito verificador
        soma = sum(numeros[i] * (11 - i)
                   for i in range(10))

        digito2 = (soma * 10 % 11) % 10
        return digito2 == numeros[10]


    @staticmethod
    def gerar_hash_cpf(cpf):
        cpf = Tutor.limpar_cpf(cpf)

        return hmac.new(
            CPF_HASH_KEY,
            cpf.encode(),
            hashlib.sha256).hexdigest()

    @staticmethod
    def criptografar_cpf(cpf):

        cpf = Tutor.limpar_cpf(cpf)
        return fernet.encrypt(
            cpf.encode()).decode()


    @staticmethod
    def descriptografar_cpf(cpf_criptografado):

        return fernet.decrypt(
            cpf_criptografado.encode()
        ).decode()

    @staticmethod
    def mascarar_cpf(cpf):
        cpf = Tutor.limpar_cpf(cpf)
        if len(cpf) != 11:
            raise ValueError("CPF inválido")
        return f"***.***.{cpf[6:9]}-**"


    def set_cpf(self, cpf):

        cpf = Tutor.limpar_cpf(cpf)
        if not Tutor.validar_formato_cpf(cpf):
            raise ValueError("CPF inválido")


        self.cpf_hash = Tutor.gerar_hash_cpf(cpf)

        self.cpf_criptografado = (Tutor.criptografar_cpf(cpf)
        )


    def get_cpf(self):

        return Tutor.descriptografar_cpf(
            self.cpf_criptografado
        )

    @property
    def cpf_mascarado(self):
        return Tutor.mascarar_cpf(
            self.get_cpf()
        )

    def validar_cpf(self, cpf):

        cpf = Tutor.limpar_cpf(cpf)

        if not Tutor.validar_formato_cpf(cpf):
            return False
        hash_informado = Tutor.gerar_hash_cpf(cpf)
        return hmac.compare_digest(
            self.cpf_hash,
            hash_informado
        )

    def __repr__(self):
        return (
            f'nome:{self.nome} - '
        )



class Pet(Base):
    __tablename__ = 'pets'

    id = Column(Integer, primary_key=True)
    nome = Column(String(100), nullable=False)
    raca = Column(String(100), nullable=False)
    data_nascimento = Column(Date, nullable=False)
    especie = Column(String(100), nullable=False)
    tutores_id = Column(Integer, ForeignKey('tutores.id'), nullable=False)
    criado_em = Column(DateTime, server_default=func.now())


    tutor_join = relationship(
        'Tutor',
        back_populates='pet_join' )

    agendamentos_join = relationship(
        'Agendamento',
        back_populates='pet_agenda_join' )




class Agendamento(Base):
    __tablename__ = 'agendamentos'
    id = Column(Integer, primary_key=True)
    data_hora = Column(DateTime, nullable=False)
    motivo = Column(String(100), nullable=False)
    pet_id = Column(Integer, ForeignKey('pets.id'), nullable=False)
    criado_em = Column(DateTime, server_default=func.now())

    pet_agenda_join = relationship(
        'Pet',
        back_populates='agendamentos_join'
    )





def criar_tabelas():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    criar_tabelas()
    print("Tabelas criadas no banco")