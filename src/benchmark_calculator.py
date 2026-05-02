"""
Salary Benchmark Calculator — P10/P50/P75/P90 por (cargo, experiência, país).

Por que existe:
    Tabela salarial só com mediana esconde dispersão. Talent Acquisition
    precisa de range completo + comp ratio do candidato vs. mercado.

    Comp Ratio = oferta_atual / mediana_mercado
        < 0.85 → underpaid (risco de turnover)
        0.85-1.15 → market
        1.15-1.30 → premium (top performer)
        > 1.30 → outlier (executivo)
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BenchmarkRange:
    cargo:        str
    experiencia:  str
    pais:         str
    n_amostra:    int
    p10:          float
    p25:          float
    p50:          float
    p75:          float
    p90:          float
    p99:          float


def calcular(
    df: pd.DataFrame,
    cargo: str | None = None,
    experiencia: str | None = None,
    pais: str | None = None,
    coluna_salario: str = "salary_in_usd",
) -> BenchmarkRange:
    """Devolve range salarial filtrado pelos critérios fornecidos."""
    sub = df.copy()
    if cargo:
        sub = sub[sub["job_title"].str.contains(cargo, case=False, na=False)]
    if experiencia:
        sub = sub[sub["exp_label"] == experiencia]
    if pais:
        sub = sub[sub["company_location"] == pais]

    if len(sub) < 5:
        # Fallback: relaxa filtros
        sub = df[df["exp_label"] == experiencia] if experiencia else df

    sal = sub[coluna_salario]
    return BenchmarkRange(
        cargo=cargo or "all",
        experiencia=experiencia or "all",
        pais=pais or "all",
        n_amostra=len(sub),
        p10=float(sal.quantile(0.10)),
        p25=float(sal.quantile(0.25)),
        p50=float(sal.quantile(0.50)),
        p75=float(sal.quantile(0.75)),
        p90=float(sal.quantile(0.90)),
        p99=float(sal.quantile(0.99)),
    )


def comp_ratio(salario_atual: float, p50_mercado: float) -> tuple[float, str]:
    """Devolve comp ratio + classificação."""
    ratio = salario_atual / p50_mercado if p50_mercado > 0 else 0
    if ratio < 0.85:
        clas = "UNDERPAID"
    elif ratio < 1.15:
        clas = "MARKET"
    elif ratio < 1.30:
        clas = "PREMIUM"
    else:
        clas = "OUTLIER"
    return float(ratio), clas


def grade_salarial(
    df: pd.DataFrame,
    cargos_alvo: list[str] | None = None,
    experiencias: list[str] = ("Entry", "Mid", "Senior", "Executive"),
) -> pd.DataFrame:
    """Tabela salarial multi-cargo × multi-experiência (P50)."""
    if cargos_alvo is None:
        cargos_alvo = (
            df.groupby("job_title")["salary_in_usd"].count()
            .sort_values(ascending=False).head(10).index.tolist()
        )

    rows = []
    for cargo in cargos_alvo:
        row = {"cargo": cargo}
        for exp in experiencias:
            b = calcular(df, cargo=cargo, experiencia=exp)
            row[f"{exp}_p50"] = b.p50
            row[f"{exp}_n"] = b.n_amostra
        rows.append(row)
    return pd.DataFrame(rows)
