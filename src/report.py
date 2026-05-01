"""Painel CLI + dashboard de gráficos."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .analysis import ResultadoAnalise

logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"


def imprimir(resultado: ResultadoAnalise, n_total: int, sal_mediano: float,
             output_dir: Path = OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'═'*56}")
    print("  DASHBOARD — SALÁRIOS TECH (DATA SCIENCE)")
    print(f"  Profissionais: {n_total:,} | Mediana global: ${sal_mediano:,.0f}")
    print(f"{'═'*56}")
    print(f"\n  {'Cargo':<35} {'Mediana':>10} {'N':>5}")
    for _, r in resultado.por_cargo.head(8).iterrows():
        print(f"  {r['job_title']:<35} ${r['mediana']:>9,.0f} {int(r['contagem']):>5}")
    print()
    print(f"  {'Experiência':<15} {'Mediana':>10} {'P90':>12} {'N':>5}")
    for _, r in resultado.por_experiencia.iterrows():
        print(f"  {r['experiencia']:<15} ${r['mediana']:>9,.0f} ${r['p90']:>11,.0f} {int(r['contagem']):>5}")
    print()
    print(f"  Tendência YoY: {resultado.tendencia_anual['crescimento_yoy'].dropna().mean():+.1f}% aa")
    rem = resultado.test_remote
    print(f"  Remote vs Salary: {rem['conclusao']} (p={rem['p_value']:.4f})")
    print(f"{'═'*56}\n")

    _salary_by_role(resultado, output_dir)
    _salary_by_experience(resultado, output_dir)
    _trend_chart(resultado, output_dir)
    _remote_and_size(resultado, output_dir)
    _top_countries(resultado, output_dir)


def _salary_by_role(resultado: ResultadoAnalise, out: Path):
    df = resultado.por_cargo.head(12).sort_values("mediana")
    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(df["job_title"], df["mediana"] / 1000, color="steelblue")
    ax.set_xlabel("Salário Mediano (k USD)")
    ax.set_title("Salário Mediano por Cargo (Top 12)")
    ax.grid(alpha=0.3, axis="x")
    for bar, v in zip(bars, df["mediana"] / 1000):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f"${v:.0f}k", va="center", fontsize=8)
    plt.tight_layout()
    plt.savefig(out / "salary_by_role.png", dpi=150, bbox_inches="tight")
    plt.close()


def _salary_by_experience(resultado: ResultadoAnalise, out: Path):
    df = resultado.por_experiencia
    x = np.arange(len(df))
    width = 0.35
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width/2, df["mediana"] / 1000, width, label="Mediana", color="steelblue")
    ax.bar(x + width/2, df["p90"] / 1000, width, label="P90", color="darkorange", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(df["experiencia"])
    ax.set_ylabel("Salário (k USD)")
    ax.set_title("Salário por Nível de Experiência")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(out / "salary_by_experience.png", dpi=150, bbox_inches="tight")
    plt.close()


def _trend_chart(resultado: ResultadoAnalise, out: Path):
    df = resultado.tendencia_anual
    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax1.plot(df["work_year"], df["mediana"] / 1000, "o-", color="steelblue", lw=2)
    ax1.set_xlabel("Ano")
    ax1.set_ylabel("Salário Mediano (k USD)", color="steelblue")
    ax1.tick_params(axis="y", labelcolor="steelblue")
    ax2 = ax1.twinx()
    yoy = df["crescimento_yoy"].dropna()
    ax2.bar(df["work_year"].iloc[1:], yoy.values, alpha=0.4, color="green",
            label="Crescimento YoY (%)")
    ax2.set_ylabel("Crescimento YoY (%)", color="green")
    ax2.tick_params(axis="y", labelcolor="green")
    ax1.set_title("Tendência de Salários por Ano")
    ax1.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(out / "salary_trend.png", dpi=150, bbox_inches="tight")
    plt.close()


def _remote_and_size(resultado: ResultadoAnalise, out: Path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    for ax, df, col, title in [
        (ax1, resultado.por_remote, "remote_label", "Salário Mediano por Modalidade"),
        (ax2, resultado.por_tamanho, "size_label",  "Salário Mediano por Porte da Empresa"),
    ]:
        ax.bar(df[col], df["mediana"] / 1000, color="steelblue")
        ax.set_ylabel("Salário Mediano (k USD)")
        ax.set_title(title)
        ax.grid(alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(out / "remote_size.png", dpi=150, bbox_inches="tight")
    plt.close()


def _top_countries(resultado: ResultadoAnalise, out: Path):
    top = resultado.top_paises
    fig, ax = plt.subplots(figsize=(9, 6))
    top[::-1].plot(kind="barh", ax=ax, color="goldenrod")
    ax.set_xlabel("Salário Mediano (USD)")
    ax.set_title("Top 10 Países por Salário Mediano (mín. 5 registros)")
    ax.grid(alpha=0.3, axis="x")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x/1000:.0f}k"))
    plt.tight_layout()
    plt.savefig(out / "top_countries.png", dpi=150, bbox_inches="tight")
    plt.close()
