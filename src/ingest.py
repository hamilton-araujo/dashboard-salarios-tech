"""Carga e limpeza do Data Science Job Salaries dataset."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "salaries.csv"

EXP_MAP = {"EN": "Entry", "MI": "Mid", "SE": "Senior", "EX": "Executive"}
SIZE_MAP = {"S": "Small", "M": "Medium", "L": "Large"}
REMOTE_MAP = {0: "On-site", 50: "Hybrid", 100: "Remote"}

TOP_ROLES = [
    "Data Scientist", "Data Engineer", "Data Analyst",
    "Machine Learning Engineer", "Research Scientist",
]


def carregar() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado em {CSV_PATH}.\n"
            "Baixe via: kaggle datasets download -d ruchi798/data-science-job-salaries"
        )
    df = pd.read_csv(CSV_PATH)
    df = _limpar(df)
    logger.info("Dataset carregado: %d profissionais | %d cargos únicos",
                len(df), df["job_title"].nunique())
    return df


def _limpar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop(columns=["Unnamed: 0", "salary", "salary_currency"], errors="ignore")
    df = df.dropna(subset=["salary_in_usd"])
    df = df[df["salary_in_usd"] > 0]
    df["exp_label"]    = df["experience_level"].map(EXP_MAP)
    df["size_label"]   = df["company_size"].map(SIZE_MAP)
    df["remote_label"] = df["remote_ratio"].map(REMOTE_MAP).fillna("Hybrid")
    df["is_top_role"]  = df["job_title"].isin(TOP_ROLES)
    logger.info("Após limpeza: %d registros | salário médio: $%.0f",
                len(df), df["salary_in_usd"].mean())
    return df.reset_index(drop=True)


def resumo(df: pd.DataFrame) -> None:
    print(f"\n{'─'*54}")
    print(f"  Data Science Salaries — {len(df):,} profissionais")
    print(f"{'─'*54}")
    print(f"  Cargos únicos  : {df['job_title'].nunique()}")
    print(f"  Salário médio  : ${df['salary_in_usd'].mean():,.0f}")
    print(f"  Salário mediano: ${df['salary_in_usd'].median():,.0f}")
    print(f"  Período        : {df['work_year'].min()}–{df['work_year'].max()}")
    print(f"  Países (empresa): {df['company_location'].nunique()}")
    print(f"{'─'*54}\n")
