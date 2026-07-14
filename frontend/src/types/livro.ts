export type Livro = {
  id: string;
  titulo: string | null;
  autor: string | null;
  genero: string | null;
  ano: number | null;
  numero_paginas: number | null;
  descricao: string | null;
  imagem_url?: string | null;
  imagem?: string | null;
  capa_url?: string | null;
  capa?: string | null;
};

export type LivrosPaginados = {
  items: Livro[];
  total: number;
  limite: number;
  offset: number;
};

export type ListarLivrosParams = {
  limite?: number;
  offset?: number;
  busca?: string;
  genero?: string;
};

export type LivroRecomendado = Livro & {
  similaridade: number;
};

export type RecomendacaoPayload = {
  preferencia: string;
  limite: number;
};

export type BookFromAPI = {
  title: string | null;
  author: string | null;
  year: number | null;
  number_of_pages: number | null;
  book_description: string | null;
  category: string | null;
};

export type RecommendationResponse = {
  response: string;
  retrieved_books: BookFromAPI[];
};
