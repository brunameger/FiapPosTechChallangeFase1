# Imports e Bibliotecas
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext

# JWT
SECRET_KEY = "123456789"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 (Criptografia e a parada do Forms)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Configurações Passlib - Dar um jeito de ocultar
senha = 'admin'

def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

# Usuário Fake
username_fake = {
    "username": "Tech3",
    "hash_senha": gerar_hash_senha(senha)
}

def verificar_senha(senha: str, hash: str) -> bool:
    """Verifica se a senha fornecida corresponde ao hash armazenado."""
    return pwd_context.verify(senha, hash)

def autenticar_usuario(username: str, senha: str) -> Optional[dict]:
    """Valida credenciais e retorna o usuário se autenticado."""
    if username == username_fake["username"] and verificar_senha(senha, username_fake["hash_senha"]):
        return {"username": username}
    return None

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Cria um token JWT com os dados e tempo de expiração fornecidos.

    Args:
        data (dict): Dados para codificação no token.
        expires_delta (Optional[timedelta]): Tempo até expiração.

    Returns:
        str: Token JWT.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15)) # Mudar para UTC (Padrão JWT)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def obter_usuario(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Decodifica o token JWT e valida o usuário.

    Args:
        token (str): Token JWT.

    Returns:
        dict: Dados do usuário autenticado.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username != username_fake["username"]:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")
        return {"username": username}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    
