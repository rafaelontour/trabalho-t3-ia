from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt

from app.api.providers.factory import create_provider
from app.api.recommendation_agent.book_recommendation_builder import (
    BookRecommendationBuilder,
)
from app.prompts.book_recommendation_without_rag import (
    BOOK_RECOMMENDATION_WITHOUT_RAG,
)

REFUSAL_OUT_OF_DOMAIN = (
    "Desculpe, sou um sistema especializado em recomendação de livros "
    "e só posso ajudar com esse tema."
)
REFUSAL_NO_CONTEXT = (
    "Desculpe, não encontrei opções correspondentes no catálogo atual."
)


@dataclass
class ExperimentResult:
    test_id: str
    categoria: str
    consulta: str
    versao: str
    provider: str
    deve_recusar: bool
    generos_esperados: str
    resposta: str
    livros_recuperados: str
    generos_recuperados: str
    quantidade_recuperada: int
    recusou: bool
    acerto_recusa: bool
    acerto_genero_recuperacao: bool | None
    sucesso_tecnico: bool
    tempo_ms: float
    erro: str


class ExperimentRunner:
    def __init__(
        self,
        provider_name: str,
        top_k: int,
        temperature: float,
        token_limit: int,
    ) -> None:
        self.provider_name = provider_name
        self.top_k = top_k
        self.model_config = {
            "temperature": temperature,
            "token_limit": token_limit,
        }

    def _new_provider(self):
        return create_provider(
            self.provider_name,
            model_config=self.model_config,
        )

    @staticmethod
    def _collect_stream(provider: Any, prompt: str) -> str:
        chunks: list[str] = []
        for chunk in provider.generate_response_stream(prompt=prompt):
            if chunk:
                chunks.append(str(chunk))
        return "".join(chunks).strip()

    @staticmethod
    def _is_refusal(response: str) -> bool:
        normalized = " ".join(response.split()).lower()
        return (
            REFUSAL_OUT_OF_DOMAIN.lower() in normalized
            or REFUSAL_NO_CONTEXT.lower() in normalized
        )

    @staticmethod
    def _serialize_books(books: list[Any]) -> tuple[str, str]:
        titles: list[str] = []
        categories: list[str] = []

        for book in books:
            title = getattr(book, "title", None)
            category = getattr(book, "category", None)

            if title:
                titles.append(str(title))

            if category:
                categories.append(str(category).upper())

        return " | ".join(titles), " | ".join(categories)

    @staticmethod
    def _genre_hit(
        expected_genres: list[str],
        recovered_genres: str,
    ) -> bool | None:
        if not expected_genres:
            return None

        recovered = {
            value.strip().upper()
            for value in recovered_genres.split("|")
            if value.strip()
        }
        expected = {value.upper() for value in expected_genres}

        return bool(expected & recovered)

    async def run_without_rag(self, case: dict[str, Any]) -> ExperimentResult:
        started_at = time.perf_counter()
        response = ""
        error = ""

        try:
            provider = self._new_provider()
            prompt = BOOK_RECOMMENDATION_WITHOUT_RAG.format(
                pergunta_usuario=case["consulta"].strip()
            )
            response = self._collect_stream(provider, prompt)

            if not response:
                raise RuntimeError("O provider retornou uma resposta vazia.")
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        refused = self._is_refusal(response)
        should_refuse = bool(case["deve_recusar"])

        return ExperimentResult(
            test_id=case["id"],
            categoria=case["categoria"],
            consulta=case["consulta"],
            versao="sem_rag",
            provider=self.provider_name,
            deve_recusar=should_refuse,
            generos_esperados=" | ".join(case["generos_esperados"]),
            resposta=response,
            livros_recuperados="",
            generos_recuperados="",
            quantidade_recuperada=0,
            recusou=refused,
            acerto_recusa=(refused == should_refuse) if not error else False,
            acerto_genero_recuperacao=None,
            sucesso_tecnico=not bool(error),
            tempo_ms=round(elapsed_ms, 2),
            erro=error,
        )

    async def run_with_rag(self, case: dict[str, Any]) -> ExperimentResult:
        started_at = time.perf_counter()
        response = ""
        books: list[Any] = []
        error = ""

        try:
            provider = self._new_provider()
            builder = BookRecommendationBuilder(provider=provider)
            result = await builder.stream_build(
                user_message=case["consulta"],
                top_k=self.top_k,
            )
            response = (result.response or "").strip()
            books = result.retrieved_books or []

            if not response:
                raise RuntimeError("O fluxo com RAG retornou resposta vazia.")
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        elapsed_ms = (time.perf_counter() - started_at) * 1000
        titles, recovered_genres = self._serialize_books(books)
        refused = self._is_refusal(response)
        should_refuse = bool(case["deve_recusar"])

        return ExperimentResult(
            test_id=case["id"],
            categoria=case["categoria"],
            consulta=case["consulta"],
            versao="com_rag",
            provider=self.provider_name,
            deve_recusar=should_refuse,
            generos_esperados=" | ".join(case["generos_esperados"]),
            resposta=response,
            livros_recuperados=titles,
            generos_recuperados=recovered_genres,
            quantidade_recuperada=len(books),
            recusou=refused,
            acerto_recusa=(refused == should_refuse) if not error else False,
            acerto_genero_recuperacao=self._genre_hit(
                case["generos_esperados"],
                recovered_genres,
            ),
            sucesso_tecnico=not bool(error),
            tempo_ms=round(elapsed_ms, 2),
            erro=error,
        )

    async def run_all(
        self,
        cases: list[dict[str, Any]],
    ) -> list[ExperimentResult]:
        results: list[ExperimentResult] = []

        for index, case in enumerate(cases, start=1):
            print(f"[{index}/{len(cases)}] {case['id']} - sem RAG")
            results.append(await self.run_without_rag(case))

            print(f"[{index}/{len(cases)}] {case['id']} - com RAG")
            results.append(await self.run_with_rag(case))

        return results


def load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    if len(cases) < 30:
        raise ValueError("A especificação exige pelo menos 30 casos de teste.")

    required_fields = {
        "id",
        "categoria",
        "consulta",
        "deve_recusar",
        "generos_esperados",
    }

    for case in cases:
        missing = required_fields - set(case)
        if missing:
            raise ValueError(
                f"Caso {case.get('id', '<sem id>')} sem campos: "
                f"{sorted(missing)}"
            )

    return cases


def save_json(results: list[ExperimentResult], output_dir: Path) -> None:
    path = output_dir / "resultados_completos.json"
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            [asdict(result) for result in results],
            file,
            ensure_ascii=False,
            indent=2,
        )


def save_csv(results: list[ExperimentResult], output_dir: Path) -> None:
    path = output_dir / "resultados_completos.csv"
    rows = [asdict(result) for result in results]

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def percentage(values: list[bool]) -> float:
    if not values:
        return 0.0

    return round(sum(values) / len(values) * 100, 2)


def summarize(results: list[ExperimentResult]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []

    for version in ("sem_rag", "com_rag"):
        version_results = [r for r in results if r.versao == version]
        technical = [r.sucesso_tecnico for r in version_results]
        refusal_hits = [r.acerto_recusa for r in version_results]
        genre_hits = [
            r.acerto_genero_recuperacao
            for r in version_results
            if r.acerto_genero_recuperacao is not None
        ]
        times = [r.tempo_ms for r in version_results if r.sucesso_tecnico]

        summary.append(
            {
                "versao": version,
                "execucoes": len(version_results),
                "sucesso_tecnico_percentual": percentage(technical),
                "acerto_recusa_percentual": percentage(refusal_hits),
                "acerto_genero_recuperacao_percentual": (
                    percentage([bool(value) for value in genre_hits])
                    if genre_hits
                    else "não aplicável"
                ),
                "tempo_medio_ms": (
                    round(statistics.mean(times), 2) if times else 0.0
                ),
                "tempo_mediano_ms": (
                    round(statistics.median(times), 2) if times else 0.0
                ),
                "erros_tecnicos": sum(1 for r in version_results if r.erro),
            }
        )

    return summary


def save_summary(summary: list[dict[str, Any]], output_dir: Path) -> None:
    path = output_dir / "resumo_metricas.csv"

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(summary[0].keys()))
        writer.writeheader()
        writer.writerows(summary)


def save_failures(results: list[ExperimentResult], output_dir: Path) -> None:
    failures: list[dict[str, Any]] = []

    for result in results:
        if result.erro:
            failure_type = "ERRO_TECNICO"
        elif not result.acerto_recusa:
            failure_type = "ERRO_DE_RECUSA"
        elif result.acerto_genero_recuperacao is False:
            failure_type = "GENERO_NAO_RECUPERADO"
        else:
            continue

        failures.append(
            {
                "test_id": result.test_id,
                "categoria": result.categoria,
                "versao": result.versao,
                "tipo_falha": failure_type,
                "consulta": result.consulta,
                "resposta": result.resposta,
                "livros_recuperados": result.livros_recuperados,
                "erro": result.erro,
            }
        )

    path = output_dir / "falhas_encontradas.csv"
    fields = [
        "test_id",
        "categoria",
        "versao",
        "tipo_falha",
        "consulta",
        "resposta",
        "livros_recuperados",
        "erro",
    ]

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(failures)


def save_human_evaluation_template(
    results: list[ExperimentResult],
    output_dir: Path,
) -> None:
    path = output_dir / "avaliacao_humana.csv"
    fields = [
        "test_id",
        "categoria",
        "versao",
        "consulta",
        "resposta",
        "relevancia_0_a_4",
        "coerencia_0_a_4",
        "utilidade_0_a_4",
        "alucinou_sim_nao",
        "observacoes",
    ]

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()

        for result in results:
            writer.writerow(
                {
                    "test_id": result.test_id,
                    "categoria": result.categoria,
                    "versao": result.versao,
                    "consulta": result.consulta,
                    "resposta": result.resposta,
                    "relevancia_0_a_4": "",
                    "coerencia_0_a_4": "",
                    "utilidade_0_a_4": "",
                    "alucinou_sim_nao": "",
                    "observacoes": "",
                }
            )


def _bar_chart(
    labels: list[str],
    values: list[float],
    title: str,
    ylabel: str,
    destination: Path,
) -> None:
    figure = plt.figure(figsize=(8, 5))
    axis = figure.add_subplot(111)
    bars = axis.bar(labels, values)
    axis.set_title(title)
    axis.set_ylabel(ylabel)
    axis.set_ylim(0, max(100, max(values, default=0) * 1.15))

    for bar, value in zip(bars, values):
        axis.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{value:.1f}",
            ha="center",
            va="bottom",
        )

    figure.tight_layout()
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def generate_charts(
    results: list[ExperimentResult],
    summary: list[dict[str, Any]],
    output_dir: Path,
) -> None:
    chart_dir = output_dir / "graficos"
    chart_dir.mkdir(parents=True, exist_ok=True)

    labels = [row["versao"].replace("_", " ") for row in summary]

    _bar_chart(
        labels,
        [float(row["sucesso_tecnico_percentual"]) for row in summary],
        "Sucesso técnico por versão",
        "Percentual (%)",
        chart_dir / "01_sucesso_tecnico.png",
    )
    _bar_chart(
        labels,
        [float(row["acerto_recusa_percentual"]) for row in summary],
        "Acerto de recusa por versão",
        "Percentual (%)",
        chart_dir / "02_acerto_recusa.png",
    )
    _bar_chart(
        labels,
        [float(row["tempo_medio_ms"]) for row in summary],
        "Tempo médio de resposta por versão",
        "Milissegundos",
        chart_dir / "03_tempo_medio.png",
    )

    categories = sorted({result.categoria for result in results})
    versions = ["sem_rag", "com_rag"]
    figure = plt.figure(figsize=(11, 6))
    axis = figure.add_subplot(111)
    x_positions = list(range(len(categories)))
    width = 0.35

    for index, version in enumerate(versions):
        values: list[float] = []

        for category in categories:
            subset = [
                result
                for result in results
                if result.versao == version and result.categoria == category
            ]
            values.append(percentage([r.acerto_recusa for r in subset]))

        positions = [
            position + (index - 0.5) * width for position in x_positions
        ]
        axis.bar(
            positions,
            values,
            width=width,
            label=version.replace("_", " "),
        )

    axis.set_title("Acerto de recusa por categoria")
    axis.set_ylabel("Percentual (%)")
    axis.set_xticks(x_positions)
    axis.set_xticklabels(categories, rotation=25, ha="right")
    axis.set_ylim(0, 100)
    axis.legend()
    figure.tight_layout()
    figure.savefig(chart_dir / "04_resultado_por_categoria.png", dpi=180)
    plt.close(figure)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Executa os 30 casos nas versões com e sem RAG."
    )
    parser.add_argument(
        "--provider",
        choices=["openai", "gemini", "ollama"],
        default="openai",
    )
    parser.add_argument("--top-k", type=int, default=6)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--token-limit", type=int, default=300)
    parser.add_argument(
        "--cases",
        type=Path,
        default=Path(__file__).with_name("casos_teste.json"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).with_name("results"),
    )

    return parser.parse_args()


async def main() -> None:
    args = parse_arguments()
    cases = load_cases(args.cases)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = args.output_root / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    runner = ExperimentRunner(
        provider_name=args.provider,
        top_k=args.top_k,
        temperature=args.temperature,
        token_limit=args.token_limit,
    )
    results = await runner.run_all(cases)
    summary = summarize(results)

    save_json(results, output_dir)
    save_csv(results, output_dir)
    save_summary(summary, output_dir)
    save_failures(results, output_dir)
    save_human_evaluation_template(results, output_dir)
    generate_charts(results, summary, output_dir)

    print(f"\nExperimento concluído. Resultados em: {output_dir}")


if __name__ == "__main__":
    asyncio.run(main())
