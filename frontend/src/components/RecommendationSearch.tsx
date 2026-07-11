"use client";

import { FormEvent, useState } from "react";

import { BookGrid } from "@/components/BookGrid";
import { recomendarLivros } from "@/services/api";
import type { LivroRecomendado } from "@/types/livro";

export function RecommendationSearch() {
  const [preferencia, setPreferencia] = useState("");
  const [resultados, setResultados] = useState<LivroRecomendado[]>([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [pesquisou, setPesquisou] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const texto = preferencia.trim();

    if (texto.length < 3) {
      setErro("Descreva melhor o tipo de livro que você procura.");
      return;
    }

    setCarregando(true);
    setErro(null);
    setPesquisou(true);

    try {
      const livros = await recomendarLivros({
        preferencia: texto,
        limite: 6
      });

      setResultados(livros);
    } catch (error) {
      setResultados([]);
      setErro(
        error instanceof Error
          ? error.message
          : "Não foi possível buscar recomendações."
      );
    } finally {
      setCarregando(false);
    }
  }

  return (
    <section className="recommendation-section">
      <div className="recommendation-panel">
        <div>
          <span className="eyebrow">Busca semântica</span>
          <h1>Encontre sua próxima leitura</h1>
          <p>
            Descreva em linguagem natural o tipo de história,
            tema ou estilo de livro que você gosta.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="search-form">
          <label htmlFor="preferencia">
            O que você gostaria de ler?
          </label>

          <textarea
            id="preferencia"
            value={preferencia}
            onChange={(event) => setPreferencia(event.target.value)}
            placeholder="Ex.: Gosto de fantasia com magia, aventura, criaturas mitológicas e protagonistas jovens."
            rows={5}
            maxLength={1000}
          />

          <div className="search-form__footer">
            <span>{preferencia.length}/1000</span>

            <button type="submit" disabled={carregando}>
              {carregando
                ? "Buscando..."
                : "Receber recomendações"}
            </button>
          </div>
        </form>

        {erro && <p className="error-message">{erro}</p>}
      </div>

      {pesquisou && !erro && (
        <div className="results">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Resultados</span>
              <h2>Livros recomendados para você</h2>
            </div>
          </div>

          {carregando ? (
            <p className="loading-message">
              Comparando sua preferência com os livros...
            </p>
          ) : (
            <BookGrid
              livros={resultados}
              mensagemVazia="Nenhum livro semelhante foi encontrado."
            />
          )}
        </div>
      )}
    </section>
  );
}
