"""
Relatório executivo Head of Talent — Bandas salariais 2025 + estratégia.
"""

import io
import logging
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.ingest import carregar
from src.analysis import analisar
from src.benchmark_calculator import grade_salarial
from src.salary_bands import construir as construir_bandas, estrategia_por_cargo

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def _grafico_bandas(df_bandas: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(13, 7))
    df_senior = df_bandas[df_bandas["experiencia"] == "Senior"].sort_values("midpoint")

    y = np.arange(len(df_senior))
    ax.barh(y, df_senior["maximo"] - df_senior["minimo"], left=df_senior["minimo"],
            color="#3498db", alpha=0.5, label="Banda P25–P75")
    ax.scatter(df_senior["midpoint"], y, s=80, color="red", zorder=5, label="Midpoint (P50)")
    ax.set_yticks(y)
    ax.set_yticklabels(df_senior["cargo"])
    ax.set_xlabel("Salário Anual (USD)")
    ax.set_title("Bandas Salariais — Senior (P25 / P50 / P75)")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    ax.legend()
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _grafico_estrategia(df_estr: pd.DataFrame, out: Path):
    fig, ax = plt.subplots(figsize=(11, 6))
    cores = {"PAGAR_P75": "#27ae60", "PAGAR_P50": "#3498db",
             "PAGAR_P50_RECONHECER_DADO_RASO": "#f39c12"}
    cs = [cores.get(e, "#bdc3c7") for e in df_estr["estrategia"]]
    df_sorted = df_estr.sort_values("target_oferta", ascending=True)
    cs_sorted = [cores.get(e, "#bdc3c7") for e in df_sorted["estrategia"]]
    ax.barh(df_sorted["cargo"], df_sorted["target_oferta"], color=cs_sorted, alpha=0.85)
    ax.set_xlabel("Target de oferta (USD)")
    ax.set_title("Estratégia de Pagamento por Cargo")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    ax.grid(alpha=0.3, axis="x")
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    logger.info("Carregando dataset...")
    df = carregar()

    res = analisar(df)

    # Top 10 cargos com maior volume
    top_cargos = (
        df.groupby("job_title")["salary_in_usd"].count()
        .sort_values(ascending=False).head(10).index.tolist()
    )

    df_bandas = construir_bandas(df, top_cargos)
    df_bandas.to_csv(OUTPUT_DIR / "bandas_salariais.csv", index=False)

    df_estr = estrategia_por_cargo(df, cargos=top_cargos)
    df_estr.to_csv(OUTPUT_DIR / "estrategia_pagamento.csv", index=False)

    _grafico_bandas(df_bandas, OUTPUT_DIR / "bandas_senior.png")
    _grafico_estrategia(df_estr, OUTPUT_DIR / "estrategia_pagamento.png")

    # Markdown
    lines = [
        "# Compensation Strategy 2025 — Tabela Salarial Tech",
        "",
        "## Sumário Executivo",
        "",
        f"- **Universo benchmark:** {len(df):,} profissionais",
        f"- **Mediana global:** USD {df['salary_in_usd'].median():,.0f}",
        f"- **Cargos mapeados:** {len(top_cargos)}",
        f"- **Tendência YoY:** {res.tendencia_anual['yoy_growth'].iloc[-1] if 'yoy_growth' in res.tendencia_anual else 0:.1f}%",
        "",
        "---",
        "",
        "## 1. Bandas Salariais (P25 / P50 / P75) — Senior",
        "",
        "![Bandas](bandas_senior.png)",
        "",
        "## 2. Estratégia de Pagamento por Cargo",
        "",
        "![Estratégia](estrategia_pagamento.png)",
        "",
        "| Cargo | n | P25 | P50 | P75 | Estratégia | Target |",
        "|---|---|---|---|---|---|---|",
    ]
    for _, r in df_estr.iterrows():
        lines.append(f"| {r['cargo']} | {int(r['n_amostra'])} | "
                     f"${r['p25']:,.0f} | ${r['p50']:,.0f} | ${r['p75']:,.0f} | "
                     f"{r['estrategia']} | ${r['target_oferta']:,.0f} |")

    lines += [
        "",
        "## 3. Tabela Salarial Completa (Senior)",
        "",
        "| Cargo | Mín (P25) | Mid (P50) | Máx (P75) | Spread | n |",
        "|---|---|---|---|---|---|",
    ]
    df_sr = df_bandas[df_bandas["experiencia"] == "Senior"].sort_values("midpoint", ascending=False)
    for _, r in df_sr.iterrows():
        lines.append(
            f"| {r['cargo']} | ${r['minimo']:,.0f} | ${r['midpoint']:,.0f} | "
            f"${r['maximo']:,.0f} | {r['spread']*100:.0f}% | {int(r['n_amostra'])} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Metodologia",
        "",
        "- **Bandas**: P25 (mín) / P50 (mid) / P75 (máx) — convenção HR.",
        "- **Spread = (Máx − Mín) / Mid**: tipicamente 35-50% em tech.",
        "- **Estratégia PAGAR_P75**: cargos críticos / hard-to-fill (ML Engineers, Data Scientists).",
        "- **Estratégia PAGAR_P50**: maioria dos cargos com pipeline saudável.",
        "- **Comp Ratio**: oferta / P50 do mercado (UNDERPAID < 0.85 < MARKET < 1.15 < PREMIUM < 1.30 < OUTLIER).",
    ]
    (OUTPUT_DIR / "relatorio_talent.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"\n{'═'*60}")
    print("  COMPENSATION STRATEGY 2025 — TECH")
    print(f"{'═'*60}")
    print(f"  Profissionais benchmark    {len(df):,}")
    print(f"  Mediana global             USD {df['salary_in_usd'].median():,.0f}")
    print(f"  Cargos mapeados            {len(top_cargos)}")
    print(f"  Cargos PAGAR_P75 (críticos) {(df_estr['estrategia'] == 'PAGAR_P75').sum()}")
    print(f"  Cargos PAGAR_P50 (market)   {(df_estr['estrategia'] == 'PAGAR_P50').sum()}")
    print(f"{'═'*60}\n")
    print(f"Relatório: {OUTPUT_DIR}/relatorio_talent.md\n")


if __name__ == "__main__":
    main()
