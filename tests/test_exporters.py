from __future__ import annotations

from pathlib import Path

from deepscraper.exporters.csv_exporter import export_to_csv
from deepscraper.exporters.json_exporter import export_to_json


def test_export_to_csv(tmp_path: Path) -> None:
    rows = [{"name": "Item1", "price": "10"}]
    output = export_to_csv(rows, filename="test.csv")
    assert output.exists()
    assert output.read_text().strip().splitlines()[1] == "Item1,10"


def test_export_to_json(tmp_path: Path) -> None:
    rows = [{"name": "Item1", "price": "10"}]
    output = export_to_json(rows, filename="test.json")
    assert output.exists()
    assert "Item1" in output.read_text()
