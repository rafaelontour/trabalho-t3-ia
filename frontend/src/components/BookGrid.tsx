import { BookCard } from "@/components/BookCard";
import type { Livro, LivroRecomendado } from "@/types/livro";

type Props = {
  livros: Array<Livro | LivroRecomendado>;
  mensagemVazia: string;
};

export function BookGrid({ livros, mensagemVazia }: Props) {
  if (livros.length === 0) {
    return <p className="empty-state">{mensagemVazia}</p>;
  }

  return (
    <div className="book-grid">
      {livros.map((livro, index) => (
        <BookCard
          key={livro.id ?? `${livro.titulo}-${index}`}
          livro={livro}
        />
      ))}
    </div>
  );
}
