# Backend de recomendação de livros

Backend em FastAPI para:

- listar os livros da página inicial;
- buscar um livro pelo ID;
- receber uma preferência em linguagem natural;
- gerar um embedding da preferência;
- consultar no PostgreSQL/pgvector os livros semanticamente mais próximos.

## Como funciona

O texto do livro é formado por título, autor, gênero e descrição. O script de
indexação transforma esse texto em um vetor de 384 posições e salva na coluna
`embedding`.

Quando o usuário escreve:

> Gosto de histórias de magia, aventura, criaturas fantásticas e mundos
> imaginários.

A API gera outro vetor com o mesmo modelo e ordena os livros pela distância de
cosseno no pgvector.

## Estrutura

```text
app/
├── api/routes/
├── core/
├── db/
├── models/
├── repositories/
├── schemas/
├── scripts/
├── services/
└── main.py
```

## Executar usando o PostgreSQL que já existe

Crie o ambiente:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Ajuste a conexão no `.env`:

```env
DATABASE_URL=postgresql+asyncpg://USUARIO:SENHA@localhost:5432/BANCO
```

Como a API está rodando no seu computador e o PostgreSQL está publicado na
porta `5432`, o host é `localhost`.

Depois de importar seus livros, preencha os embeddings:

```bash
python -m app.scripts.generate_embeddings
```

Inicie a API:

```bash
uvicorn app.main:app --reload
```

Documentação:

```text
http://localhost:8000/docs
```

## Executar tudo pelo Docker Compose

```bash
docker compose up --build -d
```

Quando a API e o PostgreSQL estão no Docker Compose, o host interno do banco é
`postgres`, que é o nome do serviço.

Depois, gere os embeddings:

```bash
docker compose exec api python -m app.scripts.generate_embeddings
```

## Endpoints

### Listar livros

```http
GET /api/v1/livros?limite=50&offset=0
```

### Buscar livro

```http
GET /api/v1/livros/L0001
```

### Recomendar

```http
POST /api/v1/recomendacoes
Content-Type: application/json

{
  "preferencia": "Quero fantasia com magia, aventura e criaturas mitológicas",
  "limite": 5
}
```

Resposta:

```json
[
  {
    "id": "L0025",
    "titulo": "Harry Potter e a Pedra Filosofal",
    "autor": "J.K. Rowling",
    "genero": "OUTRO",
    "ano": 1997,
    "numero_paginas": 208,
    "descricao": "...",
    "similaridade": 0.7342
  }
]
```

Quanto maior a similaridade, mais próximo semanticamente o livro está do texto
digitado.

## Observações

- A primeira inicialização baixa o modelo de embeddings.
- Use sempre o mesmo modelo para indexar livros e pesquisar.
- O modelo configurado gera vetores de 384 dimensões, compatíveis com
  `VECTOR(384)`.
- Ao mudar o modelo, apague ou regenere todos os embeddings.
- O endpoint não usa um LLM para decidir os resultados; a comparação é feita
  por embeddings e distância vetorial.
