from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class DataPaths:
    root: Path

    @property
    def preferred_raw_dir(self) -> Path:
        return self.root / "data" / "raw"

    @property
    def legacy_csv_dir(self) -> Path:
        return self.root / "csv"

    def effective_raw_dir(self) -> Path:
        """
        Opción B: preferir data/raw, con fallback a csv/ para compatibilidad.
        """
        if self.preferred_raw_dir.exists() and any(self.preferred_raw_dir.glob("*.csv")):
            return self.preferred_raw_dir
        return self.legacy_csv_dir


REQUIRED_FILES = {
    "Dim_Proyecto.csv",
    "Dim_TipoEnergia.csv",
    "Dim_Regulacion.csv",
    "Fact_Generacion_1000.csv",
    "Fact_Costos.csv",
    "Fact_Cobertura.csv",
    "Fact_ImpactoAmbiental.csv",
}


def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def _coerce_types(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    # Dimensiones
    if "Dim_Proyecto.csv" in tables:
        df = tables["Dim_Proyecto.csv"].copy()
        df["id_proyecto"] = df["id_proyecto"].astype("int64")
        df["id_tipo"] = df["id_tipo"].astype("int64")
        df["capacidad_mw"] = pd.to_numeric(df["capacidad_mw"], errors="coerce")
        tables["Dim_Proyecto.csv"] = df

    if "Dim_TipoEnergia.csv" in tables:
        df = tables["Dim_TipoEnergia.csv"].copy()
        df["id_tipo_energia"] = df["id_tipo_energia"].astype("int64")
        df["es_convencional"] = df["es_convencional"].astype("int64")
        tables["Dim_TipoEnergia.csv"] = df

    if "Dim_Regulacion.csv" in tables:
        df = tables["Dim_Regulacion.csv"].copy()
        df["id_regulacion"] = df["id_regulacion"].astype("int64")
        df["pct_ahorro"] = pd.to_numeric(df["pct_ahorro"], errors="coerce")
        tables["Dim_Regulacion.csv"] = df

    # Hechos
    if "Fact_Generacion_1000.csv" in tables:
        df = tables["Fact_Generacion_1000.csv"].copy()
        df["id_proyecto"] = df["id_proyecto"].astype("int64")
        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
        df["generacion_gwh"] = pd.to_numeric(df["generacion_gwh"], errors="coerce")
        df["factor_planta_pct"] = pd.to_numeric(df["factor_planta_pct"], errors="coerce")
        tables["Fact_Generacion_1000.csv"] = df

    if "Fact_Costos.csv" in tables:
        df = tables["Fact_Costos.csv"].copy()
        df["id_proyecto"] = df["id_proyecto"].astype("int64")
        df["anio"] = df["anio"].astype("int64")
        for col in ["lcoe_usd_mwh", "capex_musd", "opex_musd"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        tables["Fact_Costos.csv"] = df

    if "Fact_Cobertura.csv" in tables:
        df = tables["Fact_Cobertura.csv"].copy()
        df["id_proyecto"] = df["id_proyecto"].astype("int64")
        # En el CSV la columna se llama id_reg (no id_regulacion)
        df["id_reg"] = df["id_reg"].astype("int64")
        df["usuarios"] = pd.to_numeric(df["usuarios"], errors="coerce")
        df["disponibilidad_pct"] = pd.to_numeric(df["disponibilidad_pct"], errors="coerce")
        tables["Fact_Cobertura.csv"] = df

    if "Fact_ImpactoAmbiental.csv" in tables:
        df = tables["Fact_ImpactoAmbiental.csv"].copy()
        df["id_proyecto"] = df["id_proyecto"].astype("int64")
        df["co2_evitado_ton"] = pd.to_numeric(df["co2_evitado_ton"], errors="coerce")
        df["ahorro_agua_m3"] = pd.to_numeric(df["ahorro_agua_m3"], errors="coerce")
        tables["Fact_ImpactoAmbiental.csv"] = df

    return tables


def validate_tables(tables: dict[str, pd.DataFrame]) -> list[str]:
    issues: list[str] = []

    missing = sorted(REQUIRED_FILES - set(tables.keys()))
    if missing:
        issues.append(f"Faltan archivos requeridos: {', '.join(missing)}")

    # Validaciones de llaves
    if "Dim_Proyecto.csv" in tables:
        d = tables["Dim_Proyecto.csv"]
        if d["id_proyecto"].duplicated().any():
            issues.append("`Dim_Proyecto.id_proyecto` no es único.")
        if d["id_tipo"].isna().any():
            issues.append("`Dim_Proyecto.id_tipo` tiene nulos.")

    if "Fact_Generacion_1000.csv" in tables:
        f = tables["Fact_Generacion_1000.csv"]
        if f["fecha"].isna().any():
            issues.append("`Fact_Generacion.fecha` tiene fechas inválidas/nulas.")

    # Anti-join básico
    if "Fact_Generacion_1000.csv" in tables and "Dim_Proyecto.csv" in tables:
        f = tables["Fact_Generacion_1000.csv"]
        d = tables["Dim_Proyecto.csv"][["id_proyecto"]]
        missing_proj = f.loc[~f["id_proyecto"].isin(d["id_proyecto"]), "id_proyecto"].nunique()
        if missing_proj:
            issues.append(f"`Fact_Generacion.id_proyecto` tiene {missing_proj} proyectos sin dimensión.")

    return issues


def load_tables(repo_root: Path) -> tuple[dict[str, pd.DataFrame], Path, list[str]]:
    paths = DataPaths(root=repo_root)
    raw_dir = paths.effective_raw_dir()

    tables: dict[str, pd.DataFrame] = {}
    for fname in sorted(REQUIRED_FILES):
        fpath = raw_dir / fname
        if fpath.exists():
            tables[fname] = _read_csv(fpath)

    tables = _coerce_types(tables)
    issues = validate_tables(tables)
    return tables, raw_dir, issues


def build_consolidated_dataset(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Dataset a nivel diario por proyecto, enriquecido con dimensiones y hechos estáticos.
    """
    gen = tables["Fact_Generacion_1000.csv"].copy()
    proj = tables["Dim_Proyecto.csv"].copy()
    tipo = tables["Dim_TipoEnergia.csv"].copy()
    costos = tables["Fact_Costos.csv"].copy()
    cob = tables["Fact_Cobertura.csv"].copy()
    impacto = tables["Fact_ImpactoAmbiental.csv"].copy()
    reg = tables["Dim_Regulacion.csv"].copy()

    proj = proj.merge(
        tipo,
        left_on="id_tipo",
        right_on="id_tipo_energia",
        how="left",
        validate="many_to_one",
    )

    out = (
        gen.merge(proj, on="id_proyecto", how="left", validate="many_to_one")
        .merge(costos, on="id_proyecto", how="left", validate="many_to_one")
        .merge(impacto, on="id_proyecto", how="left", validate="many_to_one")
        .merge(cob, on="id_proyecto", how="left", validate="many_to_one")
    )

    out = out.merge(
        reg,
        left_on="id_reg",
        right_on="id_regulacion",
        how="left",
        validate="many_to_one",
    )

    return out

