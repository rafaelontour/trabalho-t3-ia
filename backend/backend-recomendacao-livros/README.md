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

## Pré-requisitos

- Python 3.12
- Docker e Docker Compose, para subir o PostgreSQL com pgvector
- Node.js, se também for rodar o frontend
- Uma chave de provedor LLM, caso use a rota de recomendação com resposta gerada
  pelo modelo (`OPENAI_API_KEY` ou `GEMINI_API_KEY`)

## Rodar o backend localmente

### 1. Subir o banco de dados

Na raiz do projeto, suba o PostgreSQL com pgvector:

```bash
cd backend
docker compose up -d
```

Esse compose cria:

- PostgreSQL em `localhost:5432`
- banco `trabalho-t3`
- usuário `postgres`
- senha `postgres`
- pgAdmin em `http://localhost:5050`

O arquivo `database/01-init.sql` é executado automaticamente na primeira criação
do volume do banco.

### 2. Criar o ambiente Python

Em outro terminal:

```bash
cd backend/backend-recomendacao-livros
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 3. Configurar o `.env`

Ajuste a conexão do banco no arquivo `.env`:

```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/trabalho-t3
```

Se for usar OpenAI:

```env
OPENAI_API_KEY=sua_chave
OPENAI_MODEL=gpt-4o-mini
```

Se for usar Gemini:

```env
GEMINI_API_KEY=sua_chave
GEMINI_MODEL=gemini-2.0-flash
```

### 4. Gerar os embeddings

Os livros do `01-init.sql` entram no banco com `embedding = NULL`. Depois de
subir o banco, gere os vetores:

```bash
python -m app.scripts.generate_embeddings
```

Esse passo precisa ser repetido quando novos livros forem inseridos sem
embedding ou quando o modelo de embedding for alterado.

### 5. Iniciar a API

```bash
uvicorn app.main:app --reload
```

A API ficará disponível em:

```text
http://localhost:8000/docs
```

## Rodar a API pelo Docker

O projeto também tem um compose específico para a API em
`backend/backend-recomendacao-livros/docker-compose.yml`.

Primeiro suba o banco pela pasta `backend`, como mostrado acima. Depois, na pasta
do backend da API:

```bash
cd backend/backend-recomendacao-livros
docker compose up --build -d
```

Depois gere os embeddings dentro do container:

```bash
docker compose exec api python -m app.scripts.generate_embeddings
```

## Rodar o frontend

Em outro terminal, a partir da raiz do projeto:

```bash
cd frontend
npm install
npm run dev
```

Abra:

```text
http://localhost:3000
```

O frontend espera que a API esteja em:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Scripts úteis

### Testar similaridade dos embeddings

```bash
cd backend/backend-recomendacao-livros
source .venv/bin/activate
python -m app.scripts.teste_embeddings
```

Também é possível passar uma consulta específica:

```bash
python -m app.scripts.teste_embeddings "quero um livro da ali hazelwood"
```

Esse script mostra o ranking por distância de cosseno no pgvector e ajuda a
verificar se o RAG está recuperando os livros esperados.

### Rodar testes

```bash
cd backend/backend-recomendacao-livros
source .venv/bin/activate
python -m pytest
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

Resposta atual da rota de recomendação:

```json
{
  "response": "Texto gerado pelo modelo com a recomendação.",
  "retrieved_books": [
    {
      "title": "Harry Potter e a Pedra Filosofal",
      "author": "J.K. Rowling",
      "year": 1997,
      "number_of_pages": 208,
      "book_description": "...",
      "category": "FANTASIA"
    }
  ]
}
```

O campo `retrieved_books` contém os livros recuperados pelo RAG e enviados como
contexto para o prompt.

## Observações

- A primeira inicialização baixa o modelo de embeddings.
- Use sempre o mesmo modelo para indexar livros e pesquisar.
- O modelo configurado gera vetores de 384 dimensões, compatíveis com
  `VECTOR(384)`.
- Ao mudar o modelo, apague ou regenere todos os embeddings.
- A busca vetorial funciona bem para tema, gênero e estilo, mas nomes próprios
  como autores e títulos podem exigir busca textual complementar.
- A rota de recomendação recupera livros por embeddings e usa um provider LLM
  para formatar a resposta final.
