import { BookGrid } from "@/components/BookGrid";
import { RecommendationSearch } from "@/components/RecommendationSearch";
import { listarLivros } from "@/services/api";
import type { Livro } from "@/types/livro";

export default async function Home() {
  let livros: Livro[] = [];
  let erro: string | null = null;

  try {
    livros = await listarLivros();
  } catch (error) {
    erro =
      error instanceof Error
        ? error.message
        : "Não foi possível carregar os livros.";
  }

  return (
    <main>
      <header className="site-header">
        <div className="container site-header__content">
          <a href="/" className="brand">
            Recomenda Livros
          </a>

          <span>Descubra histórias pelo que você gosta</span>
        </div>
      </header>

      <div className="container">
        <RecommendationSearch />

        <section className="catalog-section">
          <div className="section-heading">
            <div>
              <span className="eyebrow">Catálogo</span>
              <h2>Todos os livros</h2>
            </div>

            {!erro && (
              <span className="book-count">
                {livros.length} livros
              </span>
            )}
          </div>

          {erro ? (
            <p className="error-message">{erro}</p>
          ) : (
            <BookGrid
              livros={livros}
              mensagemVazia="Nenhum livro cadastrado."
            />
          )}
        </section>
      </div>
    </main>
  );
}
