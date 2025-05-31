import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from fastapi import HTTPException
from typing import Dict, Optional, Any
from utils.logger import configura_logger
from datetime import datetime

logger = configura_logger("scrapper_logger")

def coletar_tabela_embrapa(opcao: str, ano: int, subopcao: Optional[str] = None) -> Dict[str, Any]:
    """Coleta e estrutura a tabela da Embrapa em formato adequado.

    Args:
        opcao (str): Aba principal (ex: 'opt_02').
        ano (int): Ano da consulta.
        subopcao (Optional[str]): Sub-aba (ex: 'subopt_02').

    Returns:
        Dict: Dados estruturados.
    """
    BASE_URL = "http://vitibrasil.cnpuv.embrapa.br/index.phpa"
    params = {"opcao": opcao, "ano": ano}
    if subopcao:
        params["subopcao"] = subopcao

    try:
        logger.info(f"Tentando acessar a página da Embrapa: {params}")
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        logger.info("Conexão bem-sucedida com a Embrapa.")
    except requests.RequestException as e:
        logger.warning(f"Erro de requisição à página da Embrapa: {e}. Utilizando fallback CSV.")
        return _ler_csv_fallback(opcao, ano, subopcao)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Erro ao acessar página da Embrapa")

    soup = BeautifulSoup(response.content, "html.parser")
    tabela = soup.find("table", class_="tb_dados")
    if not tabela:
        logger.error("Tabela HTML não encontrada na resposta da Embrapa.")
        raise HTTPException(status_code=404, detail="Tabela de dados não encontrada")

    thead = tabela.find("thead")
    if not thead:
        logger.error("Cabeçalho da tabela não encontrado.")
        raise HTTPException(status_code=500, detail="Cabeçalho da tabela não encontrado")

    colunas = [th.get_text(strip=True) for th in thead.find_all("th")]

    dados_hierarquicos = []
    item_atual = None
    possui_tb_item = False

    for linha in tabela.find("tbody").find_all("tr"):
        celulas = linha.find_all("td")
        if any("tb_item" in td.get("class", []) for td in celulas):
            possui_tb_item = True
            break

    for linha in tabela.find("tbody").find_all("tr"):
        celulas = linha.find_all("td")
        if not celulas or len(celulas) != len(colunas):
            continue

        valores = [td.get_text(strip=True).replace(".", "").replace(",", ".") for td in celulas]
        registro = dict(zip(colunas, valores))

        if possui_tb_item:
            celula_0 = celulas[0].get("class", [])
            celula_1 = celulas[1].get("class", [])

            tipo = "subitem"
            if "tb_item" in celula_0 and "tb_item" in celula_1:
                tipo = "item"

            if tipo == "item":
                item_atual = registro
                item_atual["Subitens"] = []
                dados_hierarquicos.append(item_atual)
            elif tipo == "subitem" and item_atual:
                item_atual["Subitens"].append(registro)
        else:
            dados_hierarquicos.append(registro)

    if not possui_tb_item and not dados_hierarquicos:
        logger.warning("Tabela sem itens detectada, tentando agrupar como subitens.")
        subitens = []
        for linha in tabela.find("tbody").find_all("tr"):
            celulas = linha.find_all("td")
            if not celulas or len(celulas) != len(colunas):
                continue
            valores = [td.get_text(strip=True).replace(".", "").replace(",", ".") for td in celulas]
            subitens.append(dict(zip(colunas, valores)))

        if subitens:
            dados_hierarquicos.append({
                "Produto": "Dados agrupados",
                "Subitens": subitens
            })

    return {
        "Ano": ano,
        "Opcao": opcao,
        "Subopcao": subopcao,
        "Quantidade_Linhas": len(dados_hierarquicos),
        "Dados": dados_hierarquicos
    }


def _ler_csv_fallback(opcao: str, ano: int, subopcao: Optional[str]) -> Dict[str, Any]:
    """
    Lê arquivo CSV da pasta local como fallback.

    Args:
        opcao (str): Nome da aba principal.
        ano (int): Ano da consulta.
        subopcao (Optional[str]): Subopção, se existir.

    Returns:
        Dict: Estrutura JSON com dados do CSV.
    """
    nome_arquivo = f"{opcao}{subopcao}.csv" if subopcao else f"{opcao}.csv"
    caminho_arquivo = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fallback_arquivos", nome_arquivo)

    if not os.path.exists(caminho_arquivo):
        logger.error(f"Arquivo CSV de fallback não encontrado: {caminho_arquivo}")
        raise HTTPException(status_code=500, detail="Arquivo de fallback não encontrado")

    logger.info(f"Lendo dados do arquivo de fallback: {caminho_arquivo}")

    df = None
    try:
        df = pd.read_csv(caminho_arquivo, encoding='utf-8')
        if df.shape[1] <= 1:
            raise ValueError("Poucas colunas detectadas, tentando com separadores.")
    except Exception:
        separadores = [';', '\t', ',']
        max_colunas = 0
        for sep in separadores:
            try:
                df_temp = pd.read_csv(caminho_arquivo, sep=sep, encoding='utf-8')
                if len(df_temp.columns) > max_colunas:
                    df = df_temp
                    max_colunas = len(df_temp.columns)
            except Exception:
                continue

    if df is None:
        logger.error("Não foi possível determinar o separador do CSV.")
        raise HTTPException(status_code=500, detail="Erro ao ler o arquivo CSV.")
    
    # DEBUG: Verifica as colunas reais do CSV
    logger.debug(f"Colunas encontradas no CSV: {list(df.columns)}")

    ano_col = None
    for col in df.columns:
        if str(col).strip() == str(ano):
            ano_col = col
            break

    if not ano_col:
        raise HTTPException(status_code=404, detail=f"Ano {ano} não encontrado no arquivo")

    nome_coluna_item = None
    nome_campo_item = "Item"
    ignorar_colunas = {str(a) for a in range(1970, datetime.now().year + 1)} | {"control", "id"}

    for col in df.columns:
        col_strip = col.strip()
        if col_strip.lower() not in ignorar_colunas:
            prefixo = col_strip.lower()[0]
            nome_coluna_item = col_strip
            nome_campo_item = {
                "p": "Produto" if col_strip.lower().startswith("pr") else "País",
                "c": "Cultivar"
            }.get(prefixo, "Item")
            break

    dados_final = []
    item_atual = None

    if nome_coluna_item is None:
        logger.warning("Coluna de item principal não detectada. Retornando apenas colunas com ano.")
        for _, linha in df.iterrows():
            valor = linha.get(ano_col, "")
            dados_final.append({
                "Produção (L)": valor if pd.notna(valor) else None
            })
    else:
        if "control" not in df.columns:
            for _, linha in df.iterrows():
                nome_item = linha.get(nome_coluna_item, "")
                valor = linha.get(ano_col, "")
                dados_final.append({
                    nome_campo_item: nome_item if pd.notna(nome_item) else None,
                    "Produção (L)": valor if pd.notna(valor) else None
                })
        else:
            for _, linha in df.iterrows():
                control = str(linha.get("control", ""))
                nome_item = linha.get(nome_coluna_item, "")
                valor = linha.get(ano_col, "")

                if isinstance(control, str) and len(control) > 2 and control[:2].islower() and control[2] == "_":
                    subitem = {
                        "Produto": nome_item if pd.notna(nome_item) else None,
                        "Produção (L)": valor if pd.notna(valor) else None
                    }
                    if item_atual is not None:
                        item_atual.setdefault("Subitens", []).append(subitem)
                else:
                    item_atual = {
                        nome_campo_item: nome_item if pd.notna(nome_item) else None,
                        "Produção (L)": valor if pd.notna(valor) else None
                    }
                    dados_final.append(item_atual)

    return print({
        "Ano": ano,
        "Opcao": opcao,
        "Subopcao": subopcao,
        "Origem": nome_arquivo,
        "Dados": dados_final
    })

coletar_tabela_embrapa('opt_02', 2023)