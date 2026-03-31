from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from app.data_loader import build_consolidated_dataset, load_tables
from app.viz import (
    fig_cobertura_regulacion,
    fig_costos_scatter,
    fig_factor_planta_box,
    fig_generacion_por_fuente,
    fig_generacion_time,
    fig_impacto_rank,
    kpi_card_value,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


@st.cache_data(show_spinner=False)
def get_data():
    tables, raw_dir, issues = load_tables(REPO_ROOT)
    df = build_consolidated_dataset(tables)
    return df, tables, raw_dir, issues


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()

    with st.sidebar:
        st.header("Filtros")

        fuente_opts = sorted([x for x in d["fuente"].dropna().unique().tolist()])
        fuente_sel = st.multiselect("Fuente", fuente_opts, default=fuente_opts)
        if fuente_sel:
            d = d[d["fuente"].isin(fuente_sel)]

        depto_opts = sorted([x for x in d["depto"].dropna().unique().tolist()])
        depto_sel = st.multiselect("Departamento", depto_opts, default=depto_opts)
        if depto_sel:
            d = d[d["depto"].isin(depto_sel)]

        proj_opts = (
            d[["id_proyecto", "nombre"]]
            .dropna()
            .drop_duplicates()
            .sort_values("nombre")["nombre"]
            .tolist()
        )
        proj_sel = st.multiselect("Proyecto", proj_opts, default=proj_opts)
        if proj_sel:
            d = d[d["nombre"].isin(proj_sel)]

        if "fecha" in d.columns and d["fecha"].notna().any():
            min_dt = pd.to_datetime(d["fecha"].min()).date()
            max_dt = pd.to_datetime(d["fecha"].max()).date()
            start, end = st.date_input("Rango de fechas", value=(min_dt, max_dt), min_value=min_dt, max_value=max_dt)
            d = d[(d["fecha"].dt.date >= start) & (d["fecha"].dt.date <= end)]

    return d


def page_resumen(df: pd.DataFrame, raw_dir: Path, issues: list[str]):
    st.subheader("Resumen ejecutivo")
    st.caption(f"Datos cargados desde: `{raw_dir}`")

    if issues:
        with st.expander("Calidad de datos (advertencias)", expanded=True):
            for i in issues:
                st.warning(i)

    total_gwh = df["generacion_gwh"].sum(skipna=True)
    n_proyectos = df["id_proyecto"].nunique(dropna=True)
    total_usuarios = df.drop_duplicates("id_proyecto")["usuarios"].sum(skipna=True)
    total_co2 = df.drop_duplicates("id_proyecto")["co2_evitado_ton"].sum(skipna=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Generación total (GWh)", kpi_card_value(total_gwh, 2))
    c2.metric("Proyectos", f"{n_proyectos:,}")
    c3.metric("Usuarios atendidos", kpi_card_value(total_usuarios, 0))
    c4.metric("CO₂ evitado (ton)", kpi_card_value(total_co2, 0))

    st.plotly_chart(fig_generacion_time(df, freq="M"), use_container_width=True, key="resumen_gen_m")

    a, b = st.columns(2)
    with a:
        st.plotly_chart(fig_generacion_por_fuente(df), use_container_width=True, key="resumen_gen_fuente")
    with b:
        st.plotly_chart(fig_factor_planta_box(df), use_container_width=True, key="resumen_factor_box")


def page_costos(df: pd.DataFrame):
    st.subheader("Costos")
    st.plotly_chart(fig_costos_scatter(df), use_container_width=True, key="costos_scatter")

    st.divider()
    st.subheader("Tabla (último año de costos por proyecto)")
    t = (
        df.sort_values(["id_proyecto", "anio"])
        .drop_duplicates("id_proyecto", keep="last")[
            ["id_proyecto", "nombre", "fuente", "capacidad_mw", "anio", "lcoe_usd_mwh", "capex_musd", "opex_musd"]
        ]
        .sort_values("lcoe_usd_mwh", ascending=True)
    )
    st.dataframe(t, use_container_width=True, hide_index=True)


def page_cobertura(df: pd.DataFrame):
    st.subheader("Cobertura y regulación")
    st.plotly_chart(fig_cobertura_regulacion(df), use_container_width=True, key="cobertura_reg_bar")

    st.divider()
    st.subheader("Disponibilidad (%) por fuente")
    d = df.drop_duplicates("id_proyecto").dropna(subset=["disponibilidad_pct", "fuente"])
    if d.empty:
        st.info("No hay datos suficientes para graficar disponibilidad.")
    else:
        import plotly.express as px

        st.plotly_chart(
            px.bar(
                d.groupby("fuente", as_index=False)["disponibilidad_pct"].mean(),
                x="fuente",
                y="disponibilidad_pct",
                title="Disponibilidad promedio por fuente (%)",
            ),
            use_container_width=True,
            key="cobertura_disp_bar",
        )


def page_impacto(df: pd.DataFrame):
    st.subheader("Impacto ambiental")
    a, b = st.columns(2)
    with a:
        st.plotly_chart(fig_impacto_rank(df, "co2_evitado_ton"), use_container_width=True, key="impacto_top_co2")
    with b:
        st.plotly_chart(fig_impacto_rank(df, "ahorro_agua_m3"), use_container_width=True, key="impacto_top_agua")

    st.divider()
    st.subheader("Relación: CO₂ evitado vs capacidad")
    d = df.drop_duplicates("id_proyecto").dropna(subset=["co2_evitado_ton", "capacidad_mw", "fuente", "nombre"])
    if d.empty:
        st.info("No hay datos suficientes para el scatter.")
    else:
        import plotly.express as px

        st.plotly_chart(
            px.scatter(
                d,
                x="capacidad_mw",
                y="co2_evitado_ton",
                color="fuente",
                hover_name="nombre",
                title="CO₂ evitado (ton) vs capacidad (MW)",
            ),
            use_container_width=True,
            key="impacto_scatter_cap_co2",
        )


def page_proyectos(df: pd.DataFrame):
    st.subheader("Explorador de proyectos")
    projs = df[["id_proyecto", "nombre"]].dropna().drop_duplicates().sort_values("nombre")
    name = st.selectbox("Proyecto", projs["nombre"].tolist())
    d = df[df["nombre"] == name].copy()
    if d.empty:
        st.info("No hay datos para ese proyecto.")
        return

    base = d.drop_duplicates("id_proyecto").iloc[0]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Fuente", str(base.get("fuente", "—")))
    c2.metric("Capacidad (MW)", kpi_card_value(base.get("capacidad_mw"), 1))
    c3.metric("LCOE (USD/MWh)", kpi_card_value(base.get("lcoe_usd_mwh"), 2))
    c4.metric("CO₂ evitado (ton)", kpi_card_value(base.get("co2_evitado_ton"), 0))

    st.plotly_chart(fig_generacion_time(d, freq="M"), use_container_width=True, key=f"proyecto_gen_m_{int(base['id_proyecto'])}")
    st.dataframe(
        d.sort_values("fecha")[["fecha", "generacion_gwh", "factor_planta_pct"]].dropna(),
        use_container_width=True,
        hide_index=True,
    )


def page_landing(raw_dir: Path):
    st.subheader("Análisis de la Matriz Energética de Colombia (2020–2025)")
    st.caption("Dashboard interactivo construido en Streamlit a partir de un modelo tipo estrella (dimensiones + hechos).")

    c1, c2 = st.columns([1.3, 1])
    with c1:
        st.markdown(
            """
Este proyecto explora la **diversificación de la matriz eléctrica colombiana**, comparando fuentes **convencionales**
(ej. hidráulica) vs **no convencionales** (FNCER como solar/eólica) y sus implicaciones en:

- **Generación** (GWh) y **factor de planta** (%)
- **Costos** (LCOE, CAPEX, OPEX)
- **Cobertura** (usuarios atendidos, disponibilidad) y **regulación** (leyes/incentivos)
- **Impacto ambiental** (CO₂ evitado, ahorro de agua)

Usa filtros globales para segmentar por **fuente**, **departamento**, **proyecto** y **rango de fechas**.
"""
        )

    with c2:
        st.markdown("### Datos")
        st.markdown(f"- **Fuente cargada desde**: `{raw_dir}`")
        st.markdown(
            """
- **Dim_Proyecto**: ubicación, capacidad (MW), tipo de energía  
- **Dim_TipoEnergia**: fuente, convencional/no convencional  
- **Dim_Regulacion**: leyes e incentivos  
- **Fact_Generacion**: serie temporal diaria (GWh, factor de planta)  
- **Fact_Costos**: costos por proyecto/año (LCOE, CAPEX, OPEX)  
- **Fact_Cobertura**: usuarios, disponibilidad, regulación aplicada  
- **Fact_ImpactoAmbiental**: CO₂ evitado, ahorro de agua  
"""
        )

    st.divider()
    st.markdown("### Cómo leer este dashboard")

    a, b, c = st.columns(3)
    with a:
        st.markdown(
            """
**Generación**
- Observa tendencias por día/mes.
- Compara fuentes y proyectos.
- Revisa la variabilidad del **factor de planta**.
"""
        )
    with b:
        st.markdown(
            """
**Costos**
- Relación **CAPEX vs LCOE** (tamaño = capacidad).
- Ranking por LCOE para comparar tecnologías.
"""
        )
    with c:
        st.markdown(
            """
**Cobertura & Impacto**
- Usuarios atendidos por regulación.
- Top proyectos por **CO₂ evitado** y **ahorro de agua**.
"""
        )

    st.info(
        "Sugerencia: empieza aquí, luego visita **Resumen** para KPIs globales, y después profundiza en cada pestaña.",
        icon="ℹ️",
    )


def main():
    st.set_page_config(page_title="Matriz Energética Colombia", layout="wide")
    st.title("Matriz Energética de Colombia (app Streamlit)")

    df, _tables, raw_dir, issues = get_data()
    filtered = apply_filters(df)

    tabs = st.tabs(["Inicio", "Resumen", "Generación", "Costos", "Cobertura", "Impacto", "Proyectos"])

    with tabs[0]:
        page_landing(raw_dir)

    with tabs[1]:
        page_resumen(filtered, raw_dir, issues)

    with tabs[2]:
        st.subheader("Generación")
        st.plotly_chart(fig_generacion_time(filtered, freq="D"), use_container_width=True, key="gen_d")
        st.plotly_chart(fig_generacion_time(filtered, freq="M"), use_container_width=True, key="gen_m")
        st.plotly_chart(fig_generacion_por_fuente(filtered), use_container_width=True, key="gen_fuente")

    with tabs[3]:
        page_costos(filtered)

    with tabs[4]:
        page_cobertura(filtered)

    with tabs[5]:
        page_impacto(filtered)

    with tabs[6]:
        page_proyectos(filtered)


if __name__ == "__main__":
    main()

