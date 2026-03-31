from __future__ import annotations

from pathlib import Path

from app.data_loader import build_consolidated_dataset, load_tables


def test_tables_load_and_join():
    repo_root = Path(__file__).resolve().parents[1]
    tables, _raw_dir, issues = load_tables(repo_root)

    assert "Faltan archivos requeridos" not in "\n".join(issues)

    df = build_consolidated_dataset(tables)
    # debe tener filas (generación diaria)
    assert len(df) > 0
    # columnas clave esperadas tras joins
    for col in ["fecha", "generacion_gwh", "nombre", "fuente", "capacidad_mw"]:
        assert col in df.columns


def test_no_missing_project_dim_for_generation():
    repo_root = Path(__file__).resolve().parents[1]
    tables, _raw_dir, issues = load_tables(repo_root)
    assert "proyectos sin dimensión" not in "\n".join(issues)

