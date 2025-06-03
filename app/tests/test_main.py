from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"mensagem": "API de vitivinicultura da Embrapa"}


def test_login_sucesso():
    response = client.post("/login", data={"username": "Tech3", "password": "admin"})
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    return body["access_token"]


def test_login_falha():
    response = client.post("/login", data={"username": "errado", "password": "errado"})
    assert response.status_code == 401


def test_dados_sem_token():
    response = client.get("/dados", params={"opcao": "opt_02", "ano": 2023})
    assert response.status_code == 401


def test_dados_com_token():
    token_response = client.post("/login", data={"username": "Tech3", "password": "admin"})
    token = token_response.json()["access_token"]

    response = client.get(
        "/dados",
        params={"opcao": "opt_02", "ano": 2023},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [200, 502, 404]  # Sucesso ou fallback dependendo da conexão
