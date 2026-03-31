from __future__ import annotations

import pandas as pd
import plotly.express as px


def kpi_card_value(value, decimals: int = 2) -> str:
    if value is None:
        return "—"
    try:
        v = float(value)
    except Exception:
        return "—"
    if abs(v) >= 1_000_000:
        return f"{v/1_000_000:.{decimals}f} M"
    if abs(v) >= 1_000:
        return f"{v/1_000:.{decimals}f} K"
    return f"{v:.{decimals}f}"


def fig_generacion_time(df: pd.DataFrame, freq: str = "M"):
    d = df.dropna(subset=["fecha", "generacion_gwh"]).copy()
    if d.empty:
        return px.line(title="Generación (GWh)")
    d = d.set_index("fecha").sort_index()
    agg = d["generacion_gwh"].resample(freq).sum().reset_index()
    return px.line(agg, x="fecha", y="generacion_gwh", title="Generación agregada (GWh)")


def fig_generacion_por_fuente(df: pd.DataFrame):
    d = df.dropna(subset=["fuente", "generacion_gwh"]).copy()
    if d.empty:
        return px.bar(title="Generación por fuente")
    agg = d.groupby("fuente", as_index=False)["generacion_gwh"].sum().sort_values("generacion_gwh", ascending=False)
    return px.bar(agg, x="fuente", y="generacion_gwh", title="Generación total por fuente (GWh)")


def fig_factor_planta_box(df: pd.DataFrame):
    d = df.dropna(subset=["fuente", "factor_planta_pct"]).copy()
    if d.empty:
        return px.box(title="Factor planta")
    return px.box(d, x="fuente", y="factor_planta_pct", points="outliers", title="Distribución de factor de planta (%)")


def fig_costos_scatter(df: pd.DataFrame):
    d = df.dropna(subset=["lcoe_usd_mwh", "capex_musd", "capacidad_mw", "fuente"]).copy()
    if d.empty:
        return px.scatter(title="Costos: LCOE vs CAPEX")
    # Una fila por proyecto (costos son estáticos por proyecto)
    d = d.sort_values(["id_proyecto", "anio"]).drop_duplicates("id_proyecto", keep="last")
    return px.scatter(
        d,
        x="capex_musd",
        y="lcoe_usd_mwh",
        size="capacidad_mw",
        color="fuente",
        hover_name="nombre",
        title="LCOE vs CAPEX (tamaño = capacidad MW)",
        labels={"capex_musd": "CAPEX (MUSD)", "lcoe_usd_mwh": "LCOE (USD/MWh)"},
    )


def fig_cobertura_regulacion(df: pd.DataFrame):
    d = df.dropna(subset=["ley", "usuarios"]).copy()
    if d.empty:
        return px.bar(title="Cobertura por regulación")
    agg = d.groupby("ley", as_index=False)["usuarios"].sum().sort_values("usuarios", ascending=False)
    return px.bar(agg, x="ley", y="usuarios", title="Usuarios atendidos por regulación")


def fig_impacto_rank(df: pd.DataFrame, metric: str):
    if metric not in {"co2_evitado_ton", "ahorro_agua_m3"}:
        raise ValueError("metric inválida")
    cols = ["id_proyecto", "nombre", "fuente", metric]
    d = df[cols].dropna(subset=[metric]).copy()
    if d.empty:
        return px.bar(title="Impacto")
    d = d.drop_duplicates("id_proyecto")
    d = d.sort_values(metric, ascending=False).head(10)
    title = "Top 10 por CO₂ evitado (ton)" if metric == "co2_evitado_ton" else "Top 10 por ahorro de agua (m³)"
    return px.bar(d, x="nombre", y=metric, color="fuente", title=title)

