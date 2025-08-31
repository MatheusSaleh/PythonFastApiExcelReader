from fastapi import FastAPI, HTTPException, Request, UploadFile, File, Depends, status
from sqlalchemy.orm import Session
import pandas as pd
from database import get_db
from models import Pessoa, Endereco, Militar, Empresa, Atirador, Patente, Filiacao
from datetime import datetime
from io import BytesIO
from fastapi import Depends
import logging
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

from security_token import verify_jwt_token

app = FastAPI()

bearer_scheme = HTTPBearer()



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funções auxiliares
def safe_str(value, max_len=None):
    if value is None or pd.isna(value):
        return None
    value = str(value).strip()
    return value[:max_len] if max_len else value

def format_date(value):
    if value is None or pd.isna(value):
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    try:
        return datetime.strptime(str(value), "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

def parse_bool_sim_nao(valor):
    if valor is None or pd.isna(valor):
        return False
    valor_str = str(valor).strip().upper()
    return valor_str in ("SIM", "S", "TRUE", "1")

def parse_estuda(valor):
    if valor is None or pd.isna(valor):
        return 'N'
    valor_str = str(valor).strip().upper()
    if valor_str in ("SIM", "S", "TRUE", "1"):
        return 'S'
    return 'N'

def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token ausente")
    token = auth_header.split(" ")[1]
    return verify_jwt_token(token)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Meu Serviço de Upload",
        version="1.0.0",
        description="API de leitura de planilhas",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.post("/upload-atiradores-index/{ano_alistamento}")
async def upload_atiradores_index(
    ano_alistamento: int, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
    ):
    try:
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents), header=None)
        df = df.iloc[1:]  # ignora cabeçalho

        col = {
            "numero_chamada": 0,
            "ra": 1,
            "nome_completo": 2,
            "nome_guerra": 3,
            "pelotao": 4,
            "data_nascimento": 5,
            "cidade_nascimento": 6,
            "estado_nascimento": 7,
            "email": 8,
            "telefone": 9,
            "rg": 10,
            "cpf": 11,
            "numero_titulo_de_eleitor": 12,
            "zona_eleitoral": 13,
            "secao_eleitoral": 14,
            "escolaridade": 15,
            "estuda": 16,
            "instituicao_onde_estuda": 17,
            "religiao": 18,
            "tipo_sanguineo": 19,
            "possui_veiculo": 20,
            "cnh": 21,
            "categoria_cnh": 22,
            "meio_de_transporte": 23,
            "nome_mae": 24,
            "telefone_mae": 25,
            "nome_pai": 26,
            "telefone_pai": 27,
            "relacao_quem_mora_junto": 28,
            "nome_quem_mora_junto": 29,
            "cep": 30,
            "rua": 31,
            "numero": 32,
            "complemento": 33,
            "atirador_trabalha": 34,
            "voluntario": 35,
            "nome_empresa": 36,
            "telefone_empresa": 37,
            "nome_chefe_ou_responsavel": 38,
            "rua_empresa": 39,
            "cep_empresa": 40,
        }

        # Patente Atirador
        patente = db.query(Patente).filter_by(nome_patente="Atirador").first()
        if not patente:
            patente = Patente(nome_patente="Atirador", imagem_patente="")
            db.add(patente)
            db.flush()

        inserted = 0

        for index, row in df.iterrows():
            try:
                # Valores primários
                ano_alistamento_str = str(ano_alistamento)
                numero_chamada_str = safe_str(row.get(col.get("numero_chamada")), 10)

                # Verifica duplicidade
                exists = db.query(Atirador).filter(
                    Atirador.numero_chamada == numero_chamada_str,
                    Atirador.ano_alistamento == ano_alistamento_str
                ).first()
                if exists:
                    logger.info(f"Linha {index} ignorada: já existe.")
                    continue

                # Endereço do atirador
                endereco = Endereco(
                    rua=safe_str(row.get(col.get("rua")), 50),
                    numero=safe_str(row.get(col.get("numero")), 30),
                    complemento=safe_str(row.get(col.get("complemento")), 100),
                    cep=safe_str(row.get(col.get("cep")), 20),
                    cidade=safe_str(row.get(col.get("cidade_nascimento")), 50),
                    estado=safe_str(row.get(col.get("estado_nascimento")), 3),
                )
                db.add(endereco)
                db.flush()

                # Pessoa
                pessoa = Pessoa(
                    nome_completo=safe_str(row.get(col.get("nome_completo")), 80),
                    data_nascimento=format_date(row.get(col.get("data_nascimento"))),
                    cidade_nascimento=safe_str(row.get(col.get("cidade_nascimento")), 50),
                    estado_nascimento=safe_str(row.get(col.get("estado_nascimento")), 2),
                    cpf=safe_str(row.get(col.get("cpf")), 15),
                    rg=safe_str(row.get(col.get("rg")), 13),
                    telefone=safe_str(row.get(col.get("telefone")), 15),
                    email=safe_str(row.get(col.get("email")), 60),
                    numero_titulo_de_eleitor=safe_str(row.get(col.get("numero_titulo_de_eleitor")), 13),
                    zona_eleitoral=safe_str(row.get(col.get("zona_eleitoral")), 4),
                    secao_eleitoral=safe_str(row.get(col.get("secao_eleitoral")), 5),
                    religiao=safe_str(row.get(col.get("religiao")), 25),
                    escolaridade=safe_str(row.get(col.get("escolaridade")), 30),
                    tipo_sanguineo=safe_str(row.get(col.get("tipo_sanguineo")), 8),
                    cnh=safe_str(row.get(col.get("cnh")), 12),
                    categoria_cnh=safe_str(row.get(col.get("categoria_cnh")), 3),
                    possui_veiculo=parse_bool_sim_nao(row.get(col.get("possui_veiculo"))),
                    meio_de_transporte=safe_str(row.get(col.get("meio_de_transporte")), 60),
                    id_endereco=endereco.id
                )
                db.add(pessoa)
                db.flush()

                # Militar
                militar = Militar(
                    ra=str(row.get(col.get("ra"))) if row.get(col.get("ra")) else None,
                    nome_de_guerra=row.get(col.get("nome_guerra")),
                    pessoa=pessoa,
                    id_patente=patente.id
                )
                db.add(militar)
                db.flush()

                # Endereço empresa
                endereco_empresa = Endereco(
                    rua=safe_str(row.get(col.get("rua_empresa")), 50),
                    cep=safe_str(row.get(col.get("cep_empresa")), 15)
                )
                db.add(endereco_empresa)
                db.flush()

                # Empresa
                empresa = Empresa(
                    nome=safe_str(row.get(col.get("nome_empresa")), 200),
                    telefone_empresa=safe_str(row.get(col.get("telefone_empresa")), 15),
                    nome_chefe_ou_responsavel=safe_str(row.get(col.get("nome_chefe_ou_responsavel")), 80),
                    id_endereco=endereco_empresa.id
                )
                db.add(empresa)
                db.flush()

                # Filiação
                filiacao = Filiacao(
                    nome_mae=safe_str(row.get(col.get("nome_mae")), 100),
                    telefone_mae=safe_str(row.get(col.get("telefone_mae")), 20),
                    nome_pai=safe_str(row.get(col.get("nome_pai")), 100),
                    telefone_pai=safe_str(row.get(col.get("telefone_pai")), 20)
                )
                db.add(filiacao)
                db.flush()

                # Atirador
                atirador = Atirador(
                    numero_chamada=numero_chamada_str,
                    pelotao=safe_str(row.get(col.get("pelotao")), 20),
                    estuda=parse_estuda(row.get(col.get("estuda"))),
                    voluntario=parse_bool_sim_nao(row.get(col.get("voluntario"))),
                    atirador_trabalha=parse_bool_sim_nao(row.get(col.get("atirador_trabalha"))),
                    militar=militar,
                    empresa=empresa,
                    filiacao=filiacao,
                    ano_alistamento=ano_alistamento_str,
                    relacao_quem_mora_junto=safe_str(row.get(col.get("relacao_quem_mora_junto")), 12) or "N/A",
                    nome_quem_mora_junto=safe_str(row.get(col.get("nome_quem_mora_junto")), 80) or "N/A",
                    confiabilidade_de_dado=True,
                    possui_fatd=False,
                    pontos_fatd=0,
                    instituicao_onde_estuda=safe_str(row.get(col.get("instituicao_onde_estuda")), 60) or "N/A",
                    fezcfc=False,
                    fezinspecaodesaude=False,
                    fezcompromissoabandeira=False,
                    foiatiradordestaquedoanodeinstrucao=False,
                    foimelhoratiradorcombatente=False,
                    temhonraaomerito=False,
                    foipromovidocabo=False
                )
                db.add(atirador)
                db.flush()
                inserted += 1

            except Exception as e:
                db.rollback()
                logger.error(f"Linha {index} falhou: {e}")
                continue

        db.commit()
        return {"status": "sucesso", "linhas_inseridas": inserted}

    except Exception as e:
        logger.critical(f"Falha geral: {e}")
        return {"status": "erro", "mensagem": str(e)}
