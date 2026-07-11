import type {
  ListarLivrosParams,
  Livro,
  LivroRecomendado,
  LivrosPaginados,
  RecomendacaoPayload
} from "@/types/livro";

const API_URL = (
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000/api/v1"
).replace(/\/$/, "");

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

export function listarLivros(
  params: ListarLivrosParams = {}
): Promise<LivrosPaginados> {
  const searchParams = new URLSearchParams({
    limite: String(params.limite ?? 12),
    offset: String(params.offset ?? 0)
  });

  if (params.busca) {
    searchParams.set("busca", params.busca);
  }

  if (params.genero) {
    searchParams.set("genero", params.genero);
  }

  return request<LivrosPaginados>(`/livros?${searchParams.toString()}`, {
    cache: "no-store"
  });
}

export function listarGeneros(): Promise<string[]> {
  return request<string[]>("/livros/generos", {
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
