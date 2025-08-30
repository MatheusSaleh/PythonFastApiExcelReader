import uuid
import enum
import pandas as pd
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

class SexoEnum(enum.Enum):
    FEMININO = "F"
    MASCULINO = "M"
    OUTROS = "O"
    PREFIRO_NAO_DIZER = "P"


class EstadoCivilEnum(enum.Enum):
    SOLTEIRO = "1"
    CASADO = "2"
    VIUVO = "3"
    DIVORCIADO = "4"
    SEPARADO = "5"


class RespostaEnum(enum.Enum):
    SIM = "S"
    NAO = "N"


class Endereco(Base):
    __tablename__ = "endereco"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rua = Column(String)
    bairro = Column(String)
    complemento = Column(String)
    cidade = Column(String)
    numero = Column(String)
    cep = Column(String)
    estado = Column(String)


class Filiacao(Base):
    __tablename__ = "filiacao"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_mae = Column(String)
    telefone_mae = Column(String)
    nome_pai = Column(String)
    telefone_pai = Column(String)


class Patente(Base):
    __tablename__ = "patente"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_patente = Column(String)
    imagem_patente = Column(String)


class Pessoa(Base):
    __tablename__ = "pessoa"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nome_completo = Column(String)
    data_nascimento = Column(String)
    cidade_nascimento = Column(String)
    estado_nascimento = Column(String)
    pais_nascimento = Column(String)
    rg = Column(String)
    orgao_emissor = Column(String)
    cpf = Column(String)
    numero_titulo_de_eleitor = Column(String)
    zona_eleitoral = Column(String)
    secao_eleitoral = Column(String)
    religiao = Column(String)
    escolaridade = Column(String)
    tipo_sanguineo = Column(String)
    cnh = Column(String)
    categoria_cnh = Column(String)
    telefone = Column(String)
    email = Column(String)
    estado_civil = Column(Enum(EstadoCivilEnum, name="estadocivilenum", create_type=False))
    possui_veiculo = Column(Boolean)
    meio_de_transporte = Column(String)
    sexo = Column(Enum(SexoEnum, name="sexoenum", create_type=False))

    id_endereco = Column(UUID(as_uuid=True), ForeignKey("endereco.id"))
    endereco = relationship("Endereco", backref="pessoa", uselist=False)


class Militar(Base):
    __tablename__ = "militar"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ra = Column(String)
    nome_de_guerra = Column(String)
    identidade_militar = Column(String)

    id_pessoa = Column(UUID(as_uuid=True), ForeignKey("pessoa.id"))
    pessoa = relationship("Pessoa", backref="militar", uselist=False)

    id_patente = Column(UUID(as_uuid=True), ForeignKey("patente.id"))
    patente = relationship("Patente", backref="militares")


class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    nome = Column(String)
    telefone_empresa = Column(String)
    nome_chefe_ou_responsavel = Column(String)

    id_endereco = Column(UUID(as_uuid=True), ForeignKey("endereco.id"))
    endereco = relationship("Endereco", backref="empresa", uselist=False)


class Atirador(Base):
    __tablename__ = "atirador"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    atirador_trabalha = Column(Boolean)
    numero_chamada = Column(Integer)
    pelotao = Column(Integer)
    ano_alistamento = Column(String)
    relacao_quem_mora_junto = Column(String)
    nome_quem_mora_junto = Column(String)
    telefone_quem_mora_junto = Column(String)
    estuda = Column(Enum(RespostaEnum, name="respostaenum", create_type=False))
    instituicao_onde_estuda = Column(String)
    foto = Column(String)
    voluntario = Column(Boolean)
    monitor = Column(Boolean, default=False)
    desligado = Column(Boolean, default=False)
    numero_chamada_monitor = Column(Integer)
    confiabilidade_de_dado = Column(Boolean)
    analise_dado = Column(String)
    possui_fatd = Column(Boolean)
    pontos_fatd = Column(Integer)

    id_empresa = Column(UUID(as_uuid=True), ForeignKey("empresa.id"))
    empresa = relationship("Empresa", uselist=False)

    id_militar = Column(UUID(as_uuid=True), ForeignKey("militar.id"))
    militar = relationship("Militar", uselist=False)

    id_filiacao = Column(UUID(as_uuid=True), ForeignKey("filiacao.id"))
    filiacao = relationship("Filiacao", uselist=False)

    fezcfc = Column(Boolean)
    fezinspecaodesaude = Column(Boolean)
    fezcompromissoabandeira = Column(Boolean)
    foiatiradordestaquedoanodeinstrucao = Column(Boolean)
    foimelhoratiradorcombatente = Column(Boolean)
    temhonraaomerito = Column(Boolean)
    foipromovidocabo = Column(Boolean)

    tempocomputadodeefetivoservico = Column(String)
    tempocomputadodeefetivoservicoarregimentado = Column(String)
    temponaocomputado = Column(String)
    temponaocomputadonaoarregimentado = Column(String)
    tempodesvcomputavelparamedalhamilitar = Column(String)
    tempodesvcomputavelparamedalhamilitaratedez = Column(String)
    tempodeserviconacionalrelevante = Column(String)
    tempototaldeefetivoservico = Column(String)
    tempototaldeefetivoservicoatedez = Column(String)
