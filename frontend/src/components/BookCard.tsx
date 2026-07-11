"use client";

import { useEffect, useState } from "react";

import type { Livro, LivroRecomendado } from "@/types/livro";

type Props = {
  livro: Livro | LivroRecomendado;
};

function possuiSimilaridade(
  livro: Livro | LivroRecomendado
): livro is LivroRecomendado {
  return "similaridade" in livro;
}

function getImagemLivro(livro: Livro | LivroRecomendado): string | null {
  return (
    livro.imagem_url ??
    livro.imagem ??
    livro.capa_url ??
    livro.capa ??
    null
  );
}

function getImagemFallback(imagem: string | null): string | null {
  if (!imagem) {
    return null;
  }

  if (imagem.endsWith("/capa")) {
    return `${imagem}.svg`;
  }

  return null;
}

export function BookCard({ livro }: Props) {
  const imagem = getImagemLivro(livro);
  const [imagemAtual, setImagemAtual] = useState(imagem);
  const [imagemCarregada, setImagemCarregada] = useState(false);

  useEffect(() => {
    setImagemAtual(imagem);
    setImagemCarregada(false);
  }, [imagem]);

  function handleImagemErro() {
    const fallback = getImagemFallback(imagemAtual);

    if (fallback && fallback !== imagemAtual) {
      setImagemAtual(fallback);
      setImagemCarregada(false);
      return;
    }

    setImagemCarregada(true);
  }

  return (
    <article className="book-card">
      {imagemAtual && (
        <div className="book-card__cover-frame">
          {!imagemCarregada && (
            <div
              className="book-card__cover-loading"
              aria-label="Carregando capa"
            />
          )}

          <img
            className={`book-card__cover${
              imagemCarregada ? " book-card__cover--loaded" : ""
            }`}
            src={imagemAtual}
            alt={livro.titulo ?? "Capa do livro"}
            onLoad={() => setImagemCarregada(true)}
            onError={handleImagemErro}
          />
        </div>
      )}

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
