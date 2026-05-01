# Dashboard Salários Tech — Data Science Jobs

Análise descritiva e dashboard de salários para profissionais de Data Science, com análise por cargo, experiência, modalidade remota e tendência anual.

## Dataset

**Data Science Job Salaries** — Kaggle (`ruchi798/data-science-job-salaries`)  
607 profissionais | 50 cargos | 50 países | 2020–2022

## Stack

| Camada | Tecnologia |
|---|---|
| Análise | pandas · scipy |
| Testes | Kruskal-Wallis (modalidade remota vs. salário) |
| Visualização | matplotlib |

## Pipeline

```
Carga → Limpeza → Análise (cargo/exp/remote/trend) → Testes → Dashboard
```

## Resultados

```
════════════════════════════════════════════════════════
  DASHBOARD — SALÁRIOS TECH (DATA SCIENCE)
  Profissionais: 607 | Mediana global: $101,570
════════════════════════════════════════════════════════
  Experiência     Mediana          P90
  Entry         $  56,500 $   106,511
  Mid           $  76,940 $   152,600
  Senior        $ 135,500 $   210,000
  Executive     $ 171,438 $   324,500

  Tendência YoY: +27.3% aa
  Remote vs Salary: Impacto significativo (p<0.001)
════════════════════════════════════════════════════════
```

**Insight**: Salários cresceram +27.3% ao ano de 2020 a 2022. Profissionais Senior ganham 2.4× mais que Entry-level.

## Estrutura

```
├── src/
│   ├── ingest.py    # Carga e limpeza
│   ├── analysis.py  # Análises descritivas + hipóteses
│   ├── report.py    # Painel CLI + 5 gráficos
│   └── main.py      # CLI argparse
├── data/
├── output/
├── tests/
└── requirements.txt
```
