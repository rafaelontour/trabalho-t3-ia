import type {
  Livro,
  LivroRecomendado,
  RecomendacaoPayload
} from "@/types/livro";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1";

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers
    }
  });

  if (!response.ok) {
    let message = "Erro ao comunicar com a API.";

    try {
      const data = await response.json();

      if (typeof data?.detail === "string") {
        message = data.detail;
      }
    } catch {
      // Mantém a mensagem padrão.
    }

    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export function listarLivros(): Promise<Livro[]> {
  return request<Livro[]>("/livros?limite=200&offset=0", {
    cache: "no-store"
  });
}

export function recomendarLivros(
  payload: RecomendacaoPayload
): Promise<LivroRecomendado[]> {
  return request<LivroRecomendado[]>("/recomendacoes", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
