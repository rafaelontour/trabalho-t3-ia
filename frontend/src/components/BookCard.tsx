import type { Livro, LivroRecomendado } from "@/types/livro";

type Props = {
  livro: Livro | LivroRecomendado;
};

function possuiSimilaridade(
  livro: Livro | LivroRecomendado
): livro is LivroRecomendado {
  return "similaridade" in livro;
}

export function BookCard({ livro }: Props) {
  return (
    <article className="book-card">
      <div className="book-card__header">
        <div>
          <span className="book-card__genre">
            {livro.genero ?? "OUTRO"}
          </span>

          <h2>{livro.titulo ?? "Título não informado"}</h2>

          <p className="book-card__author">
            {livro.autor ?? "Autor não informado"}
          </p>
        </div>

        {possuiSimilaridade(livro) && (
          <span className="book-card__score">
            {(livro.similaridade * 100).toFixed(1)}%
          </span>
        )}
      </div>

      <p className="book-card__description">
        {livro.descricao ?? "Descrição não disponível."}
      </p>

      <footer className="book-card__footer">
        <span>{livro.ano ?? "Ano desconhecido"}</span>
        <span>
          {livro.numero_paginas
            ? `${livro.numero_paginas} páginas`
            : "Número de páginas não informado"}
        </span>
      </footer>
    </article>
  );
}
