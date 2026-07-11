export type Livro = {
  id: string;
  titulo: string | null;
  autor: string | null;
  genero: string | null;
  ano: number | null;
  numero_paginas: number | null;
  descricao: string | null;
};

export type LivroRecomendado = Livro & {
  similaridade: number;
};

export type RecomendacaoPayload = {
  preferencia: string;
  limite: number;
};
