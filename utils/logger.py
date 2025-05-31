import logging
import os
from typing import Optional

def configura_logger(
    nome_logger: str = "embrapa_logger",
    arquivo_log: Optional[str] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Logs"),
    nivel: int = logging.INFO
) -> logging.Logger:
    """
    Configura e retorna um logger com saída para console e arquivo.

    Args:
        nome_logger (str): Nome identificador do logger.
        arquivo_log (str, optional): Caminho para o arquivo de log.
        nivel (int): Nível mínimo de log.

    Returns:
        logging.Logger: Logger configurado.
    """
    logger = logging.getLogger(nome_logger)
    logger.setLevel(nivel)

    if not logger.handlers:
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', "%Y-%m-%d %H:%M:%S")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if arquivo_log:
            os.makedirs(os.path.dirname(arquivo_log), exist_ok=True)
            file_handler = logging.FileHandler(arquivo_log, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger