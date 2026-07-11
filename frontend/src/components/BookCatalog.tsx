"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";

import { BookGrid } from "@/components/BookGrid";
import { listarGeneros, listarLivros } from "@/services/api";
import type { Livro } from "@/types/livro";

const PAGE_SIZE = 12;

export function BookCatalog() {
  const [livros, setLivros] = useState<Livro[]>([]);
  const [generos, setGeneros] = useState<string[]>([]);
  const [buscaInput, setBuscaInput] = useState("");
  const [busca, setBusca] = useState("");
  const [genero, setGenero] = useState("");
  const [pagina, setPagina] = useState(1);
  const [total, setTotal] = useState(0);
  const [carregando, setCarregando] = useState(true);
  const [carregamentoInicial, setCarregamentoInicial] = useState(true);
  const [erro, setErro] = useState<string | null>(null);

  const totalPaginas = useMemo(
    () => Math.max(1, Math.ceil(total / PAGE_SIZE)),
    [total]
  );

  useEffect(() => {
    let ativo = true;

    listarGeneros()
      .then((dados) => {
        if (ativo) {
          setGeneros(dados);
        }
      })
      .catch(() => {
        if (ativo) {
          setGeneros([]);
        }
      });

    return () => {
      ativo = false;
    };
  }, []);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      setBusca(buscaInput.trim());
      setPagina(1);
    }, 350);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [buscaInput]);

  useEffect(() => {
    let ativo = true;

    setCarregando(true);
    setErro(null);

    listarLivros({
      limite: PAGE_SIZE,
      offset: (pagina - 1) * PAGE_SIZE,
      busca,
      genero
    })
      .then((dados) => {
        if (!ativo) {
          return;
        }

        setLivros(dados.items);
        setTotal(dados.total);
      })
      .catch((error) => {
        if (!ativo) {
          return;
        }

        setLivros([]);
        setTotal(0);
        setErro(
          error instanceof Error
            ? error.message
            : "Não foi possível carregar os livros."
        );
      })
      .finally(() => {
        if (ativo) {
          setCarregando(false);
          setCarregamentoInicial(false);
        }
      });

    return () => {
      ativo = false;
    };
  }, [busca, genero, pagina]);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusca(buscaInput.trim());
    setPagina(1);
  }

  function handleGeneroChange(value: string) {
    setGenero(value);
    setPagina(1);
  }

  function limparFiltros() {
    setBuscaInput("");
    setBusca("");
    setGenero("");
    setPagina(1);
  }

  const inicio = total === 0 ? 0 : (pagina - 1) * PAGE_SIZE + 1;
  const fim = Math.min(pagina * PAGE_SIZE, total);

  return (
    <section className="catalog-section">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Catálogo</span>
          <h2>Todos os livros</h2>
        </div>

        {!erro && (
          <span className="book-count">
            {inicio}-{fim} de {total} livros
          </span>
        )}
      </div>

      <form className="catalog-filters" onSubmit={handleSubmit}>
        <label>
          <span>Buscar por nome</span>
          <input
            type="search"
            value={buscaInput}
            onChange={(event) => setBuscaInput(event.target.value)}
            placeholder="Digite o título do livro"
          />
        </label>

        <label>
          <span>Gênero</span>
          <select
            value={genero}
            onChange={(event) => handleGeneroChange(event.target.value)}
          >
            <option value="">Todos</option>
            {generos.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        </label>

        <div className="catalog-filters__actions">
          <button type="submit">Buscar</button>
          <button type="button" onClick={limparFiltros}>
            Limpar
          </button>
        </div>
      </form>

      {erro ? (
        <p className="error-message">{erro}</p>
      ) : carregamentoInicial ? (
        <p className="loading-message">Carregando livros...</p>
      ) : (
        <>
          {carregando && (
            <p className="loading-message loading-message--compact">
              Atualizando livros...
            </p>
          )}

          <BookGrid
            livros={livros}
            mensagemVazia="Nenhum livro encontrado."
          />

          <div className="pagination">
            <button
              type="button"
              onClick={() => setPagina((valor) => Math.max(1, valor - 1))}
              disabled={pagina === 1 || carregando}
            >
              Anterior
            </button>

            <span>
              Página {pagina} de {totalPaginas}
            </span>

            <button
              type="button"
              onClick={() =>
                setPagina((valor) => Math.min(totalPaginas, valor + 1))
              }
              disabled={pagina >= totalPaginas || carregando}
            >
              Próxima
            </button>
          </div>
        </>
      )}
    </section>
  );
}
