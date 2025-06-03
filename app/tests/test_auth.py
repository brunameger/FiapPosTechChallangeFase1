from app import auth
from datetime import timedelta
import jwt

SECRET_KEY = auth.SECRET_KEY
ALGORITHM = auth.ALGORITHM


def test_verificar_senha():
    senha = "admin"
    hash = auth.gerar_hash_senha(senha)
    assert auth.verificar_senha(senha, hash) is True
    assert auth.verificar_senha("senha_errada", hash) is False


def test_autenticar_usuario_sucesso():
    user = auth.autenticar_usuario("Tech3", "admin")
    assert user is not None
    assert user["username"] == "Tech3"


def test_autenticar_usuario_falha():
    user = auth.autenticar_usuario("usuario_invalido", "senha_invalida")
    assert user is None


def test_criar_token_acesso():
    data = {"sub": "Tech3"}
    token = auth.criar_token_acesso(data, timedelta(minutes=5))
    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == "Tech3"
