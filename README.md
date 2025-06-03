# Fiap PosTech Challenge – Fase 1

Este projeto foi desenvolvido como parte do Tech Challenge da Fase 1 da pós-graduação em Machine Learning da FIAP.  
O desafio consistiu em construir uma API pública com Python e FastAPI que realiza scraping de dados de Vitivinicultura em tempo real do site da Embrapa, com fallback automático para arquivos CSV locais.

---

## Tecnologias Utilizadas

- Python 3.11+
- FastAPI – construção da API REST
- BeautifulSoup4 – scraping de dados da Embrapa
- Uvicorn – servidor ASGI
- Pytest – testes automatizados
- Docker – empacotamento e deploy
- GitHub Actions – CI/CD
- Render – deploy automatizado (via `render.yaml`)

---

## Como Executar Localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/brunameger/FiapPosTechChallangeFase1.git
cd FiapPosTechChallangeFase1
```

### 2. Criar o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate no Windows
pip install -r requirements.txt
```

### 3. Executar a API

```bash
uvicorn app.main:app --reload
```

Acesse: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para utilizar a documentação interativa da API (Swagger UI).

### 4. Executar os testes

```bash
pytest tests/
```

---

## Deploy na Render

- URL base: https://fiappostechchallangefase1.onrender.com/  
- Swagger UI: https://fiappostechchallangefase1.onrender.com/docs

---

## Raspagem de Dados

### 1. Autenticação

- Acesse `/docs`
- Encontre a seção "LOGIN"
- Clique em "Try it out"
- Use as credenciais de exemplo:
  ```
  username: Tech3
  password: admin
  ```
- Clique em "Execute"

### 2. Autorização

- Na mesma página, clique em "Authorize"
- Repita as credenciais e clique em "Authorize"

### 3. Executar Scraping

- Vá até a seção "dados"
- Clique em "Try it out"
- Preencha os campos:
  - `opcao`
  - `ano`
  - `subopcao`
- Clique em "Execute"
- O resultado será exibido no formato JSON

---

## Estrutura do Projeto

```
.
├── app/                 # Lógica principal da API
│   ├── auth.py          # Middleware de autenticação
│   ├── main.py          # Ponto de entrada da aplicação
│   └── scrapper.py      # Módulo de scraping da Embrapa
│
├── fallback_arquivos/   # Arquivos CSV usados como fallback
│
├── tests/               # Testes unitários e de integração
│
├── utils/               # Utilitários e logger customizado
│
├── fluxograma/          # Diagrama de fluxo do projeto
│
├── start.sh             # Script de inicialização
├── render.yaml          # Configuração para deploy Render
└── requirements.txt     # Dependências
```

---

## Modo Fallback

Se o scraping falhar (por instabilidade do site da Embrapa), a API automaticamente carrega os dados do diretório `fallback_arquivos/`, garantindo alta disponibilidade das informações.

---

## Fluxograma

O projeto inclui um fluxograma `.drawio` que descreve o fluxo de scraping e fallback:  
`fluxograma/Fluxograma_Tech_Challenge.drawio`  
Você pode abrir com draw.io para visualização gráfica.

---

Desenvolvido para o Tech Challenge da Pós em Machine Learning - FIAP
