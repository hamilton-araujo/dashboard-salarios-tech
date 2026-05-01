"""Testes unitários do pipeline de salários."""

import numpy as np
import pandas as pd
import pytest

from src.ingest import _limpar, EXP_MAP, SIZE_MAP
from src.analysis import analisar


def _df_sintetico(n=200, seed=42):
    rng = np.random.default_rng(seed)
    return pd.DataFrame({
        "work_year":         rng.choice([2020, 2021, 2022], n),
        "experience_level":  rng.choice(list(EXP_MAP.keys()), n),
        "employment_type":   rng.choice(["FT", "PT", "CT"], n),
        "job_title":         rng.choice(["Data Scientist", "Data Engineer", "Analyst",
                                          "ML Engineer", "Research Scientist"], n),
        "salary":            rng.integers(50000, 200000, n),
        "salary_currency":   ["USD"] * n,
        "salary_in_usd":     rng.integers(50000, 200000, n).astype(float),
        "employee_residence":rng.choice(["US", "GB", "DE", "FR"], n),
        "remote_ratio":      rng.choice([0, 50, 100], n),
        "company_location":  rng.choice(["US", "GB", "DE", "FR", "CA"], n),
        "company_size":      rng.choice(list(SIZE_MAP.keys()), n),
    })


class TestIngest:
    def test_labels_criados(self):
        df = _limpar(_df_sintetico())
        assert "exp_label" in df.columns
        assert "size_label" in df.columns
        assert "remote_label" in df.columns

    def test_remove_salario_zero(self):
        df0 = _df_sintetico()
        df0.loc[0, "salary_in_usd"] = 0
        df_clean = _limpar(df0)
        assert (df_clean["salary_in_usd"] > 0).all()

    def test_is_top_role(self):
        df = _limpar(_df_sintetico())
        assert "is_top_role" in df.columns
        assert df["is_top_role"].dtype == bool


class TestAnalysis:
    def setup_method(self):
        self.df = _limpar(_df_sintetico())

    def test_por_cargo_nao_vazio(self):
        r = analisar(self.df)
        assert len(r.por_cargo) > 0

    def test_experiencia_ordenada(self):
        r = analisar(self.df)
        exp_order = ["Entry", "Mid", "Senior", "Executive"]
        found = [e for e in exp_order if e in r.por_experiencia["experiencia"].values]
        assert len(found) >= 2

    def test_tendencia_sorted(self):
        r = analisar(self.df)
        anos = r.tendencia_anual["work_year"].tolist()
        assert anos == sorted(anos)

    def test_remote_pvalue_valido(self):
        r = analisar(self.df)
        assert 0 <= r.test_remote["p_value"] <= 1
