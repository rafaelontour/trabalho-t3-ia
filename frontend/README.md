# Frontend Next.js — Recomendação de livros

Frontend em Next.js para consumir o backend FastAPI de recomendação semântica
de livros.

## Recursos

- lista todos os livros da API;
- recebe uma preferência em linguagem natural;
- envia a preferência para o endpoint de recomendações;
- exibe os livros ordenados por similaridade;
- tratamento de carregamento e erros;
- layout responsivo.

## Configuração

Instale as dependências:

```bash
pnpm install
```

Crie o arquivo de ambiente:

```bash
cp .env.example .env.local
```

Conteúdo:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

Execute:

```bash
pnpm dev
```

Abra:

```text
http://localhost:3000
```

## Backend esperado

### Listagem

```http
GET http://localhost:8000/api/v1/livros?limite=200&offset=0
```

### Recomendação

```http
POST http://localhost:8000/api/v1/recomendacoes
Content-Type: application/json

{
  "preferencia": "Gosto de fantasia, magia e aventura",
  "limite": 6
}
```

## CORS no FastAPI

O backend precisa permitir a origem do frontend:

```env
CORS_ORIGINS=http://localhost:3000
```
