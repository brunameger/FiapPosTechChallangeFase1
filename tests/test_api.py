import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_home():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "API de vitivinicultura da Embrapa"}


@pytest.mark.asyncio
async def test_login_sucesso():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/login",
            data={"username": "Tech3", "password": "admin"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_falha():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/login",
            data={"username": "usuario_invalido", "password": "senha_invalida"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Usuário ou senha inválidos"}