"""Diagnóstico da conexão com o LLM.

Rode `python testar_llm.py` quando o chatbot não responder. Ele confere a configuração,
lista os modelos que a sua chave enxerga e faz uma pergunta de teste, mostrando o erro
exato do provedor se algo falhar.
"""
from llm import ConfigError, criar_cliente, ler_config, mensagem_de_erro
from openai import OpenAIError


def main():
    print("1) Configuração (.env)")
    try:
        config = ler_config()
    except ConfigError as erro:
        print(f"   ERRO: {erro}")
        return

    chave = config["chave"]
    print(f"   chave:  {len(chave)} caracteres, começa com '{chave[:4]}'")
    print(f"   modelo: {config['modelo']}")
    print(f"   url:    {config['url'] or '(padrão da OpenAI)'}")
    if " " in chave:
        print("   AVISO: a chave tem espaços. Copie de novo, sem sobras.")
    if config["url"] and "generativelanguage" in config["url"]:
        if not chave.startswith("AIza"):
            print("   AVISO: chaves do Gemini costumam começar com 'AIza'. Confira se copiou a chave certa.")
        if not config["url"].rstrip("/").endswith("/openai"):
            print("   AVISO: para o Gemini a URL deve terminar em /v1beta/openai/")

    cliente = criar_cliente(config)

    print("\n2) Modelos disponíveis para esta chave")
    try:
        ids = sorted(m.id.removeprefix("models/") for m in cliente.models.list())
        uteis = [i for i in ids if "embedding" not in i and "image" not in i]
        print("   " + ("\n   ".join(uteis[:25]) if uteis else "(lista vazia)"))
        if config["modelo"] not in ids:
            print(f"   AVISO: '{config['modelo']}' não está na lista. Troque LLM_MODEL por um dos nomes acima.")
        else:
            print(f"   OK: '{config['modelo']}' está na lista.")
    except OpenAIError as erro:
        print(f"   Não consegui listar os modelos: {mensagem_de_erro(erro)}")
        print(f"   Detalhe do provedor: {erro}")

    print("\n3) Pergunta de teste")
    try:
        parametros = {
            "model": config["modelo"],
            "messages": [{"role": "user", "content": "Responda apenas com a palavra: ok"}],
        }
        if config["temperatura"] is not None:
            parametros["temperature"] = config["temperatura"]
        resposta = cliente.chat.completions.create(**parametros)
        texto = (resposta.choices[0].message.content or "").strip()
        print(f"   Resposta do LLM: {texto!r}")
        print("   Tudo certo: o chatbot deve funcionar." if texto else "   AVISO: a resposta veio vazia.")
    except OpenAIError as erro:
        print(f"   FALHOU: {mensagem_de_erro(erro)}")
        print(f"   Detalhe do provedor: {erro}")


if __name__ == "__main__":
    main()
