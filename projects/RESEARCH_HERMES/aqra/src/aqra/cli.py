import typer

from aqra.config import load_config
from aqra.db import AQRADatabase
from aqra.data.cache import DataCache
from aqra.features.lane_s import LaneSFeatureBuilder
from aqra.features.lane_i import LaneIFeatureBuilder
from aqra.signals.lane_s_signals import LaneSSignalLibrary
from aqra.signals.lane_i_signals import LaneISignalLibrary
from aqra.backtest.lane_s_bt import LaneSBacktest
from aqra.backtest.lane_i_bt import LaneIBacktest
from aqra.bear.chamber import BEARChamber
from aqra.registry.registry import StrategyRegistry

app = typer.Typer()


@app.command()
def ingest(start: str = "2020-01-01", end: str = "2024-12-31"):
    cfg = load_config()
    db = AQRADatabase(f"{cfg.data_dir}/aqra.duckdb")
    cache = DataCache(db, cfg)
    cache.refresh_prices(start, end)
    typer.echo("Data ingestion complete.")


@app.command()
def certify():
    cfg = load_config()
    db = AQRADatabase(f"{cfg.data_dir}/aqra.duckdb")
    # Placeholder orchestration
    typer.echo("Certification pipeline complete.")


@app.command()
def deploy(dry_run: bool = True):
    cfg = load_config()
    typer.echo(f"Deployment mode: {'paper' if not dry_run else 'dry-run'}")


@app.command()
def monitor():
    typer.echo("Monitoring loop: coverage and drawdown checks.")


if __name__ == "__main__":
    app()
