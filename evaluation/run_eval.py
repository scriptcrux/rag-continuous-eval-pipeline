"""Standalone CLI runner for the CloudPulse Ragas evaluation suite."""

import sys
import argparse
import asyncio
from pathlib import Path

# Force UTF-8 encoding on standard streams if needed
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from app.config import settings
from app.services.rag_engine import RAGEngine
from app.services.ingestion import DocumentIngestionService
from evaluation.dataset import BenchmarkDataset
from evaluation.thresholds import DEFAULT_THRESHOLDS
from evaluation.evaluator import RagasEvaluator
from evaluation.report_generator import ReportGenerator

console = Console(safe_box=True)


async def main():
    parser = argparse.ArgumentParser(description="CloudPulse RAG Benchmark Evaluation Suite")
    parser.add_argument(
        "--provider",
        choices=["mock", "openai", "ollama"],
        default="mock",
        help="LLM provider for RAG answering and evaluation (default: mock)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(settings.BASE_DIR / "evaluation" / "artifacts"),
        help="Directory to export report artifacts",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=True,
        help="Exit with non-zero status code if quality gates fail (CI/CD mode)",
    )
    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold cyan]CloudPulse Enterprise RAG & Ragas Evaluation Pipeline[/bold cyan]\n"
            f"[dim]Provider: [bold yellow]{args.provider}[/bold yellow] | "
            f"Knowledge Base: [bold green]{settings.DATA_DIR.name}[/bold green][/dim]",
            border_style="cyan",
        )
    )

    # 1. Initialize Engine & Ingest Knowledge Base
    console.print("[dim]-> Initializing RAG Engine and indexing documents...[/dim]")
    engine = RAGEngine()
    ingest_svc = DocumentIngestionService(chunk_size=settings.CHUNK_SIZE, chunk_overlap=settings.CHUNK_OVERLAP)
    ingest_res = ingest_svc.ingest_directory(
        directory_path=settings.DATA_DIR,
        vector_store=engine.vector_store,
        force_reindex=True,
    )
    console.print(
        f"[green][OK] Ingested {ingest_res.documents_indexed} documents ({ingest_res.total_chunks} chunks) in {ingest_res.duration_seconds}s[/green]"
    )

    # 2. Run Evaluation
    dataset = BenchmarkDataset()
    evaluator = RagasEvaluator(
        rag_engine=engine,
        thresholds=DEFAULT_THRESHOLDS,
        provider=args.provider,
    )

    console.print(f"[dim]-> Evaluating benchmark cases ({len(dataset.single_turn_cases)} single-turn, {len(dataset.multi_turn_cases)} multi-turn)...[/dim]")
    report = await evaluator.run_benchmark(dataset)

    # 3. Print Rich Results Table
    table = Table(title="[bold]Ragas Benchmark Evaluation Scorecard[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="bold white", width=24)
    table.add_column("Score", justify="center", width=12)
    table.add_column("Threshold", justify="center", width=12)
    table.add_column("Status", justify="center", width=10)

    for metric in report.metrics_summary.values():
        status_text = "[green]PASS[/green]" if metric.passed else "[red]FAIL[/red]"
        score_color = "green" if metric.passed else "red"
        table.add_row(
            metric.name,
            f"[{score_color}]{metric.score:.3f}[/{score_color}]",
            f">= {metric.threshold:.2f}",
            status_text,
        )

    console.print()
    console.print(table)
    console.print()

    # Latency & Operational Stats
    console.print(
        f"[bold]Operational Metrics:[/bold] "
        f"p50: [cyan]{report.latency_p50_ms}ms[/cyan] | "
        f"p95: [cyan]{report.latency_p95_ms}ms[/cyan] | "
        f"Multi-Turn Topic Adherence: [cyan]{report.multi_turn_score:.3f}[/cyan] | "
        f"Total Duration: [cyan]{report.duration_seconds}s[/cyan]"
    )

    # 4. Save Artifacts
    out_dir = Path(args.output_dir)
    md_path, json_path = ReportGenerator.save_reports(report, out_dir)
    console.print(f"[green][OK] Evaluation Markdown report saved to: [underline]{md_path}[/underline][/green]")
    console.print(f"[green][OK] JSON results scorecard saved to: [underline]{json_path}[/underline][/green]")

    # 5. Check Quality Gates
    if report.all_passed:
        console.print(Panel("[bold green]ALL QUALITY GATES PASSED! READY FOR PRODUCTION DEPLOYMENT.[/bold green]", border_style="green"))
        return 0
    else:
        console.print(Panel("[bold red]QUALITY GATES FAILED! Pipeline breached required quality thresholds.[/bold red]", border_style="red"))
        if args.strict:
            return 1
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
