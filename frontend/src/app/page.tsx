import { BookCatalog } from "@/components/BookCatalog";
import { RecommendationSearch } from "@/components/RecommendationSearch";

export default function Home() {
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
        <BookCatalog />
      </div>
    </main>
  );
}
