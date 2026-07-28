"""Aureum CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import click
import yaml

from .strategy import Strategy


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Aureum — self-proving semantic kernel for finance."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def validate(path: Path) -> None:
    """Validate a strategy YAML file."""
    strategy = Strategy.from_file(path)
    errors = strategy.validate()
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        raise click.Abort()
    print(f"Strategy '{strategy.metadata['name']}' is valid.")


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--data", type=click.Path(path_type=Path), help="Path to price data")
@click.option("--output", type=click.Path(path_type=Path), help="Output report path")
def backtest(path: Path, data: Path | None, output: Path | None) -> None:
    """Run a deterministic backtest for a strategy."""
    strategy = Strategy.from_file(path)
    errors = strategy.validate()
    if errors:
        click.echo("Validation failed:")
        for error in errors:
            click.echo(f"  - {error}")
        raise click.Abort()

    print(f"Running backtest for '{strategy.metadata['name']}'...")
    print(f"Data source: {data if data else 'synthetic'}")

    # Placeholder: full backtest engine to be implemented.
    report = {
        "strategy": strategy.metadata["name"],
        "status": "completed",
        "data_source": str(data) if data else "synthetic",
        "constraints": strategy.constraints(),
        "trades": 0,
        "sharpe": None,
        "max_drawdown": None,
    }

    report_json = json.dumps(report, indent=2)
    if output:
        output = Path(output)
        try:
            output.write_text(report_json, encoding="utf-8")
            print(f"Report written to {output.resolve()}")
        except Exception as e:
            print(f"Failed to write report: {e}")
            raise click.Abort()
    else:
        print(report_json)


def main() -> None:
    cli()
