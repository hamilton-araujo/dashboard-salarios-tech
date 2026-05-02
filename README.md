# Compensation Strategy 2025 — Bandas Salariais Tech

> **A pergunta do Head of Talent:** *Onde estamos vs P50/P75 do mercado? Quais cargos pagar acima da mediana para atrair? Como construir a tabela salarial competitiva 2025?*

Análise de 607 profissionais de Data Science (Kaggle) transformada em **tabela salarial corporativa**: bandas P25/P50/P75 por cargo × experiência, classificação de comp ratio (UNDERPAID/MARKET/PREMIUM) e estratégia de pagamento (PAGAR_P75 para roles críticos, PAGAR_P50 para mainstream).

---

## Por que existe

Dashboard descritivo (mediana global, top países, tendência YoY) é informacional. HR/Talent precisa de três respostas operacionais:

| Pergunta | Sinal técnico |
|---|---|
| Qual a banda salarial do cargo X? | P25/P50/P75 com IC + n_amostra |
| Estamos pagando market? | Comp Ratio = oferta / P50 mercado |
| Em quais cargos pagar premium? | Estratégia PAGAR_P75 vs PAGAR_P50 |

`output/relatorio_talent.md` consolida tudo em uma tabela acionável para o Comitê de Remuneração.

---

## A história em três atos

### Ato 1 — A revisão anual
Q4. CFO aprovou orçamento de RH 2025 com aumento de 8%. Head of Talent precisa decidir como distribuir entre cargos. Você roda:
```bash
python -m src.exec_report
```

### Ato 2 — A tabela
3 segundos depois:
```
Profissionais benchmark    607
Mediana global             USD 101,570
Cargos PAGAR_P75 (críticos) 2  (ML Engineers, Data Scientists)
Cargos PAGAR_P50 (market)   2
```

### Ato 3 — A defesa
Diretoria pergunta: *"Por que pagar 30% acima da mediana para ML Engineers?"* Resposta documentada: cargo crítico + spread de mercado 50% + tendência YoY +27% indicam pressão competitiva — pagar P75 reduz custo de recrutamento (1.5× salário) e turnover.

---

## Modelos

### Salary Benchmark Calculator
Filtra dataset por (cargo, experiência, país) e devolve P10/P25/P50/P75/P90/P99.

### Comp Ratio Classification
```
ratio = salário_atual / P50_mercado
```

| Faixa | Classificação |
|---|---|
| < 0.85 | UNDERPAID (alto risco turnover) |
| 0.85–1.15 | MARKET |
| 1.15–1.30 | PREMIUM (top performer) |
| > 1.30 | OUTLIER (executivo) |

### Bandas Salariais (P25/P50/P75)
```
Mín     = P25 (entrada na banda)
Mid     = P50 (target padrão)
Máx     = P75 (top performers / promoção)
Spread  = (Máx − Mín) / Mid    → 35-50% em tech
```

### Estratégia de Pagamento
| Estratégia | Quando aplicar |
|---|---|
| **PAGAR_P75** | Roles críticos (ML/Data Engineers, Data Scientists) |
| **PAGAR_P50** | Cargos com pipeline saudável |
| **PAGAR_P50_RECONHECER_DADO_RASO** | Amostra n < 20 — sinalizar incerteza |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Dados | Kaggle Data Science Job Salaries · Pandas |
| Estatística | scipy (Kruskal-Wallis remote × salário) |
| Bandas | NumPy quantis · agregação |
| Visualização | matplotlib (bandas P25-P75 + scatter midpoint) |

---

## Como rodar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Pipeline executivo (recomendado)
python -m src.exec_report

# Dashboard original
python -m src.main
```

---

## Outputs

```
output/
├── relatorio_talent.md           # ⭐ Tabela salarial 2025 + estratégia
├── bandas_senior.png             # ⭐ P25/P50/P75 por cargo Senior
├── bandas_salariais.csv          # ⭐ Cargo × experiência × banda
├── estrategia_pagamento.png      # ⭐ Target por cargo
├── estrategia_pagamento.csv      # ⭐ PAGAR_P75 / PAGAR_P50 por cargo
├── salary_by_role.png            # Original
├── salary_by_experience.png
├── salary_trend.png
├── remote_size.png
└── top_countries.png
```

⭐ = adicionado nesta versão.

---

## Estrutura

```
├── src/
│   ├── exec_report.py             # ⭐ Pipeline executivo Talent
│   ├── benchmark_calculator.py    # ⭐ P10/P50/P75/P90 + comp ratio
│   ├── salary_bands.py            # ⭐ Bandas + estratégia PAGAR_P75/P50
│   ├── ingest.py
│   ├── analysis.py
│   ├── report.py
│   └── main.py
├── data/
├── output/
├── tests/
└── requirements.txt
```
