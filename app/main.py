# Imports e Bibliotecas
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Optional
from app.auth import autenticar_usuario, criar_token_acesso, obter_usuario, ACCESS_TOKEN_EXPIRE_MINUTES
from app.scrapper import coletar_tabela_embrapa

app = FastAPI(title="API Vitivinicultura - Embrapa", version="2.0")

@app.get("/")
def home():
    """Retorna uma mensagem de boas-vindas para a API de vitivinicultura."""
    return {"mensagem": "API de vitivinicultura da Embrapa"}

@app.post("/login")
def login(forms: OAuth2PasswordRequestForm = Depends()):
    """
    Realiza login do usuário e gera um token JWT de acesso.

    Args:
        forms (OAuth2PasswordRequestForm): Formulário com nome de usuário e senha.

    Returns:
        dict: Token de acesso e tipo do token.
    """
    usuario = autenticar_usuario(forms.username, forms.password)
    print(forms.username)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")
    token = criar_token_acesso(
        data={"sub": usuario["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/dados")
def dados(
    opcao: str = Query(..., description="Ex: opt_02 (produção), opt_06 (exportação), etc."),
    ano: int = Query(..., ge=1970, le=2023, description="Ano entre 1970 e 2023"),
    subopcao: Optional[str] = Query(None, description="Ex: subopt_02 (necessário para algumas abas como exportação)"),
    usuario: dict = Depends(obter_usuario)
):
    """
    Retorna os dados coletados da Embrapa com base nos parâmetros fornecidos.

    Args:
        opcao (str): Aba principal da Embrapa (ex: 'opt_02').
        ano (int): Ano da consulta (entre 1970 e 2023).
        subopcao (Optional[str]): Sub-aba, se necessário.
        usuario (dict): Usuário autenticado (via token).

    Returns:
        dict: Dados estruturados da tabela.
    """
    return coletar_tabela_embrapa(opcao, ano, subopcao)