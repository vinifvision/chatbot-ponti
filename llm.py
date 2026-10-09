"""Configuração e conexão com o LLM, usada pelo servidor (app.py) e pelo diagnóstico (testar_llm.py)."""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import APIConnectionError, APIStatusError, OpenAI, OpenAIError

# override=True: o que está no .env vale mais do que variáveis antigas do terminal.
load_dotenv(Path(__file__).parent / ".env", override=True)


class ConfigError(Exception):
    """Faltou configurar ou há algo errado na configuração do LLM."""


def _env(nome):
    """Lê uma variável e tira espaços e aspas que costumam sobrar ao colar a chave."""
    return (os.getenv(nome) or "").strip().strip("\"'").strip()


def ler_config():
    chave, modelo, url = _env("LLM_API_KEY"), _env("LLM_MODEL"), _env("LLM_BASE_URL")
    if not chave or not modelo:
        raise ConfigError("O LLM não está configurado. Preencha LLM_API_KEY e LLM_MODEL no arquivo .env.")

    temperatura = _env("LLM_TEMPERATURE")
    try:
        temperatura = float(temperatura) if temperatura else None
    except ValueError:
        raise ConfigError("LLM_TEMPERATURE precisa ser um número, por exemplo 0.2. Ou apague essa linha do .env.")

    return {"chave": chave, "modelo": modelo, "url": url or None, "temperatura": temperatura}


def criar_cliente(config):
    return OpenAI(api_key=config["chave"], base_url=config["url"], timeout=30, max_retries=1)


def mensagem_de_erro(erro):
    """Traduz o erro do provedor numa dica que ajuda a corrigir a configuração."""
    if isinstance(erro, APIConnectionError):
        return "Não consegui conectar ao LLM. Confira LLM_BASE_URL e a conexão com a internet."
    if isinstance(erro, APIStatusError):
        codigo = erro.status_code
        if codigo in (401, 403):
            return (f"O LLM recusou a chave (erro {codigo}). Confira LLM_API_KEY e se a chave tem "
                    "restrições (por IP, site ou API) que bloqueiam este servidor.")
        if codigo == 404:
            return "Modelo ou endereço não encontrado (erro 404). Confira LLM_MODEL e LLM_BASE_URL."
        if codigo == 400:
            return ("O LLM recusou a requisição (erro 400). Pode ser chave inválida ou modelo que não aceita "
                    "algum parâmetro. Rode python testar_llm.py para ver o detalhe.")
        if codigo == 429:
            return "O limite de uso do LLM foi atingido (erro 429). Espere um pouco e tente de novo."
        if codigo >= 500:
            return f"O serviço do LLM está instável (erro {codigo}). Tente de novo em instantes."
        return f"O LLM devolveu o erro {codigo}. Rode python testar_llm.py para ver o detalhe."
    if isinstance(erro, OpenAIError):
        return "Não consegui falar com o LLM. Rode python testar_llm.py para ver o detalhe."
    return "Erro inesperado ao falar com o LLM."
