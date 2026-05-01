"""Análises descritivas de salários tech."""

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)


@dataclass
class ResultadoAnalise:
    por_cargo: pd.DataFrame          # job_title | median | mean | std | count
    por_experiencia: pd.DataFrame    # exp_label | median | mean | percentile_90
    por_remote: pd.DataFrame         # remote_label | median | count
    tendencia_anual: pd.DataFrame    # work_year | median_salary | yoy_growth
    por_tamanho: pd.DataFrame        # size_label | median | count
    top_paises: pd.Series            # top 10 países por mediana
    test_remote: dict                # Kruskal-Wallis remote vs salary


def analisar(df: pd.DataFrame) -> ResultadoAnalise:
    por_cargo = (
        df.groupby("job_title")["salary_in_usd"]
        .agg(mediana="median", media="mean", desvio="std", contagem="count")
        .sort_values("mediana", ascending=False)
        .head(15)
        .reset_index()
    )

    exp_order = ["Entry", "Mid", "Senior", "Executive"]
    por_exp = []
    for exp in exp_order:
        sub = df.loc[df["exp_label"] == exp, "salary_in_usd"]
        if len(sub) == 0:
            continue
        por_exp.append({
            "experiencia": exp,
            "mediana": sub.median(),
            "media": sub.mean(),
            "p90": sub.quantile(0.9),
            "contagem": len(sub),
        })
    por_experiencia = pd.DataFrame(por_exp)

    por_remote = (
        df.groupby("remote_label")["salary_in_usd"]
        .agg(mediana="median", contagem="count")
        .reset_index()
    )

    tendencia = (
        df.groupby("work_year")["salary_in_usd"]
        .median()
        .reset_index()
        .rename(columns={"salary_in_usd": "mediana"})
        .sort_values("work_year")
    )
    tendencia["crescimento_yoy"] = tendencia["mediana"].pct_change() * 100

    por_tamanho = (
        df.groupby("size_label")["salary_in_usd"]
        .agg(mediana="median", contagem="count")
        .reset_index()
    )

    top_paises = (
        df.groupby("company_location")["salary_in_usd"]
        .agg(mediana="median", contagem="count")
        .query("contagem >= 5")
        .sort_values("mediana", ascending=False)
        .head(10)["mediana"]
    )

    grupos_remote = [
        df.loc[df["remote_label"] == r, "salary_in_usd"].values
        for r in df["remote_label"].unique()
        if len(df[df["remote_label"] == r]) >= 5
    ]
    stat, p = stats.kruskal(*grupos_remote)
    test_remote = {
        "statistic": float(stat), "p_value": float(p),
        "conclusao": "Modalidade remota impacta salário" if p < 0.05 else "Sem diferença significativa",
    }

    logger.info("Análise concluída — mediana global: $%.0f", df["salary_in_usd"].median())
    return ResultadoAnalise(
        por_cargo=por_cargo,
        por_experiencia=por_experiencia,
        por_remote=por_remote,
        tendencia_anual=tendencia,
        por_tamanho=por_tamanho,
        top_paises=top_paises,
        test_remote=test_remote,
    )
