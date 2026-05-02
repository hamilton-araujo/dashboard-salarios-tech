"""
Bandas salariais sugeridas (mín/mid/máx) por cargo × experiência.

Por que existe:
    Tabela salarial corporativa precisa de bandas, não pontos:
        Mín = P25 mercado
        Mid = P50 mercado
        Máx = P75 mercado
    Spread = (Máx - Mín) / Mid → tipicamente 35-50% para tech.

Estratégia de pagamento:
    PAGAR_P75 (premium)  : roles críticos / hard-to-fill
    PAGAR_P50 (market)   : maioria dos cargos
    PAGAR_P25 (lag)      : cargos júnior com pipeline interno robusto
"""

from dataclasses import dataclass

import pandas as pd

from src.benchmark_calculator import calcular


@dataclass
class BandaSalarial:
    cargo:       str
    experiencia: str
    minimo:      float
    midpoint:    float
    maximo:      float
    spread:      float
    n_amostra:   int


def construir(df: pd.DataFrame, cargos: list[str],
              experiencias: tuple = ("Entry", "Mid", "Senior", "Executive")
              ) -> pd.DataFrame:
    """Constrói tabela completa de bandas."""
    rows = []
    for cargo in cargos:
        for exp in experiencias:
            b = calcular(df, cargo=cargo, experiencia=exp)
            spread = (b.p75 - b.p25) / b.p50 if b.p50 > 0 else 0
            rows.append(BandaSalarial(
                cargo=cargo, experiencia=exp,
                minimo=b.p25, midpoint=b.p50, maximo=b.p75,
                spread=spread, n_amostra=b.n_amostra,
            ).__dict__)
    return pd.DataFrame(rows)


def estrategia_por_cargo(
    df: pd.DataFrame,
    cargos_criticos: list[str] | None = None,
    cargos: list[str] | None = None,
) -> pd.DataFrame:
    """
    Define estratégia de pagamento por cargo.

    Heurística:
        Cargo crítico (lista explícita) → PAGAR_P75
        Cargo com baixa amostra (n<20)  → PAGAR_P50 + sinalizar dado raso
        Senior/Executive geral          → PAGAR_P50
        Entry/Mid                       → PAGAR_P50 (com possibilidade de P25)
    """
    if cargos_criticos is None:
        cargos_criticos = ["Machine Learning Engineer", "Data Scientist", "ML Engineer"]
    if cargos is None:
        cargos = (
            df.groupby("job_title")["salary_in_usd"].count()
            .sort_values(ascending=False).head(15).index.tolist()
        )

    rows = []
    for cargo in cargos:
        b = calcular(df, cargo=cargo)
        critical = any(c.lower() in cargo.lower() for c in cargos_criticos)
        if critical:
            estrategia = "PAGAR_P75"
            target = b.p75
        elif b.n_amostra < 20:
            estrategia = "PAGAR_P50_RECONHECER_DADO_RASO"
            target = b.p50
        else:
            estrategia = "PAGAR_P50"
            target = b.p50

        rows.append({
            "cargo": cargo,
            "n_amostra": b.n_amostra,
            "p25": b.p25, "p50": b.p50, "p75": b.p75, "p90": b.p90,
            "estrategia": estrategia,
            "target_oferta": target,
        })
    return pd.DataFrame(rows)
