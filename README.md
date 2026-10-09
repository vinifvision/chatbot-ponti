# Chatbot do Ponti (LLM + JSON + interface web)

Chatbot que responde perguntas sobre o **Ponti**, plataforma de match entre startups e mentores. Ele usa um LLM para interpretar a pergunta e gerar a resposta com base nas informações do arquivo `knowledge.json`.

## Como atende a atividade

| Etapa                   | Onde está                                                                            |
| ----------------------- | ------------------------------------------------------------------------------------ |
| 1. Tema                 | Ponti, definido em `knowledge.json` (campo `bot`)                                    |
| 2. Base de conhecimento | `knowledge.json`, com 20 entradas (título, perguntas parecidas e resposta)           |
| 3. Chatbot              | `app.py` e `llm.py`: recebem a pergunta, leem o JSON, montam o prompt e chamam o LLM |
| 4. Interface            | `static/index.html`: tela de chat na identidade visual do Ponti                      |

## Como funciona

1. A pessoa digita a pergunta na interface.
2. A interface envia a conversa para `POST /api/chat`.
3. O servidor lê o `knowledge.json` (a cada pergunta, então editar o arquivo não exige reiniciar).
4. O servidor monta um prompt com as regras do bot e toda a base de conhecimento, e envia ao LLM junto com o histórico.
5. O LLM interpreta a pergunta e responde usando só o que está na base. Se a informação não existir, ele avisa em vez de inventar.

A base inteira vai no prompt porque ela é pequena. Para uma base grande, o caminho seria buscar só as entradas mais parecidas com a pergunta antes de chamar o LLM.

## Como rodar

Requisitos: Python 3.9 ou mais novo.

```bash
cd chatbot-ponti
pip install -r requirements.txt
cp .env.example .env
```

Abra o arquivo `.env` e preencha `LLM_API_KEY` com a chave do provedor. Depois:

```bash
python testar_llm.py   # confere a chave, o modelo e faz uma pergunta de teste
python app.py          # sobe o chatbot na porta 5000
```

No GitHub Codespaces, abra a aba **Ports** e acesse a porta 5000.

## Se a conexão com o Gemini falhar

Rode `python testar_llm.py`. Ele mostra a configuração lida, os modelos que a sua chave enxerga e o erro exato do provedor. As causas mais comuns, segundo a documentação do Google:

- **Modelo desligado ou com acesso limitado.** O `gemini-2.0-flash` foi desligado e os modelos `gemini-2.5-*` têm acesso limitado. A documentação atual usa `gemini-3.8-flash`. Troque `LLM_MODEL` por um nome que apareça na lista do `testar_llm.py`. Erro típico: 404.
- **Chave com restrição.** Se a chave tem restrição de IP, site ou aplicativo, o servidor do Codespaces é bloqueado. Se foi criada no Google Cloud sem restrição de API, ela pode ser recusada. O caminho mais simples é criar a chave no Google AI Studio e deixar só a opção "Restrict to Gemini API only". Se a chave é compartilhada com outras APIs, a restrição não pode excluir a Generative Language API. Erro típico: 400, 401 ou 403.
- **Chave copiada com sobras.** O `.env` aceita a chave com ou sem aspas, mas não pode ter espaços no meio.
- **Limite do plano gratuito.** Erro 429: espere um pouco e tente de novo.
- **URL errada.** Para o Gemini ela deve ser exatamente `https://generativelanguage.googleapis.com/v1beta/openai/`.

O erro completo do provedor também aparece no terminal onde o `python app.py` está rodando.

## Qual LLM usar

O código usa a API no formato da OpenAI, que vários provedores aceitam. Para trocar de provedor, só mude `LLM_API_KEY`, `LLM_BASE_URL` e `LLM_MODEL` no `.env`. O `.env.example` traz exemplos para Gemini, Groq e OpenAI.

**Nunca envie o `.env` para o GitHub.** Ele guarda a sua chave e já está no `.gitignore`.

## Identidade visual

A interface segue a tela "Mentores recomendados" do app do Ponti: barra lateral lilás (`#C8A4FE`) com cantos arredondados, textos em azul-marinho (`#070161`), botões roxos (`#AF7AFE`), campos em `#F6F7FC`, cards brancos com borda cinza e a fonte Poppins. As cores foram medidas no print e a fonte foi identificada pelo desenho das letras. Confirme os valores finais com a equipe de design.

O arquivo `static/logo.png` foi recortado do print, então tem pouca resolução. Troque pelo logo oficial da equipe de design, mantendo o nome `logo.png` ou ajustando o `src` no `index.html`. Um SVG fica mais nítido.

## Trocar ou ampliar o tema

Edite o `knowledge.json`:

- `bot`: nome, tema, saudação e perguntas sugeridas.
- `entradas`: cada item tem `id`, `titulo`, `perguntas` (exemplos de como alguém perguntaria) e `resposta` (a informação que o bot pode usar).

## Estrutura

```
chatbot-ponti/
├── app.py              servidor Flask: lê o JSON, monta o prompt e responde
├── llm.py              configuração do LLM e mensagens de erro
├── testar_llm.py       diagnóstico da conexão com o LLM
├── knowledge.json      base de conhecimento
├── static/
│   ├── index.html      interface de chat
│   └── logo.png        logo (trocar pelo oficial)
├── requirements.txt
└── .env.example        modelo de configuração
```
