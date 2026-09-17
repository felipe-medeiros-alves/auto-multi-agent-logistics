from pathlib import Path

import typer

from logistics_crew.config import DEFAULT_DB_PATH
from logistics_crew.runner import ConfigurationError, ensure_database, run_instruction


def execute(
    instruction: str,
    *,
    output: Path | None = None,
    verbose: bool = False,
    db_path: Path = DEFAULT_DB_PATH,
) -> str:
    repo = ensure_database(db_path)
    report = run_instruction(instruction, repo, verbose=verbose)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    return report


def main() -> None:
    def _cli(
        instruction: str = typer.Argument(
            ...,
            help="Natural language shipping request.",
        ),
        output: Path | None = typer.Option(
            None,
            "--output",
            "-o",
            help="Write markdown report to this file.",
        ),
        verbose: bool = typer.Option(
            False,
            "--verbose",
            "-v",
            help="Verbose crew logging.",
        ),
        db_path: Path = typer.Option(
            DEFAULT_DB_PATH,
            "--db",
            help="Path to mock shipping SQLite database.",
        ),
    ) -> None:
        try:
            report = execute(
                instruction,
                output=output,
                verbose=verbose,
                db_path=db_path,
            )
        except ConfigurationError as exc:
            typer.secho(str(exc), fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1) from exc
        except Exception as exc:
            typer.secho(f"Crew run failed: {exc}", fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1) from exc
        typer.echo(report)

    typer.run(_cli)


if __name__ == "__main__":
    main()
