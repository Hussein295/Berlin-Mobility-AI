<div align="center">

# Berlin Mobility AI

### Hourly Bicycle Traffic Forecasting with Machine Learning

**2.2M observations · 35 counting stations · Berlin, 2017–2025**

[Dataset](https://daten.berlin.de/datensaetze/radzahldaten-in-berlin) · [Notebooks](notebooks/) · [Source Code](src/)

</div>

---

## Overview

Berlin Mobility AI is an end-to-end machine learning project that forecasts **hourly bicycle counts at automated counting stations in Berlin**. It combines multi-year public mobility data, time-based feature engineering, model benchmarking, and a chronological evaluation designed to reflect forecasting on future observations.

The project examines not only overall prediction accuracy but also **generalization to counting stations not represented in model training**—an important limitation for real-world deployment.

## Results at a glance

| Metric | Best validation model | Held-out test |
|:--|--:|--:|
| **Model** | Histogram-based Gradient Boosting | Histogram-based Gradient Boosting |
| **MAE** (bicycles / station-hour) | **30.94** | **33.24** |
| **RMSE** (bicycles / station-hour) | **53.03** | **57.95** |
| **R²** | **0.8003** | **0.7295** |

**24% lower validation MAE** than the historical-average baseline (40.74 → 30.94).

### Model comparison — validation set

| Model | MAE ↓ | RMSE ↓ | R² ↑ |
|:--|--:|--:|--:|
| Historical-average baseline | 40.74 | 68.64 | 0.6654 |
| Linear Regression | 58.22 | 86.04 | 0.4742 |
| Decision Tree | 43.30 | 74.33 | 0.6076 |
| Random Forest | 35.95 | 64.17 | 0.7075 |
| **Histogram-based Gradient Boosting** | **30.94** | **53.03** | **0.8003** |

*MAE and RMSE are measured in bicycles per station-hour. The final test set was reserved for evaluation after model selection.*

### Generalization to unseen stations — held-out test

| Station group | Stations | Observations | MAE | RMSE | WAPE |
|:--|--:|--:|--:|--:|--:|
| Seen during training | 30 | 352,779 | 28.38 | 50.04 | 29.76% |
| Unseen during training | 5 | 57,299 | 63.14 | 92.84 | 90.52% |

**Key finding:** Error at unseen stations is substantially higher. Station identity is useful for forecasting at known counters, but the model needs additional transferable spatial or contextual features to work reliably at new locations.

## Data

- **Source:** [Berlin Open Data — Radzähldaten in Berlin](https://daten.berlin.de/datensaetze/radzahldaten-in-berlin)
- **Modeling period:** January 2017 – December 2025
- **Observations:** 2,216,184 hourly records
- **Counting stations:** 35 station IDs
- **Target:** Hourly bicycle count

The workflow consolidates yearly files, checks missing values and unusual counts, and prepares time-ordered datasets for training and evaluation.

### Feature engineering

- Calendar signals: hour, weekday, month, day of year, year, weekend indicator
- Cyclical encodings: sine/cosine transforms for hour, weekday, and month
- Station identity: one-hot encoding, with unseen IDs handled during inference

### Evaluation design

| Split | Period | Observations |
|:--|:--|--:|
| Training | 2017-01-01 to 2023-04-19 | 1,426,327 |
| Validation | 2023-04-20 to 2024-08-24 | 379,779 |
| Test | 2024-08-25 to 2025-12-31 | 410,078 |

A **chronological split** avoids evaluating the model on historical observations that occur before its training data. Validation was used for model comparison; the later test period was held out for final reporting.

## Insights

- **Time of day and station identity** were the two most influential feature groups in grouped permutation importance on validation data.
- Gradient Boosting outperformed the historical-average baseline and other tested regression models on the validation set.
- The difference between known-station and unseen-station errors is a meaningful deployment risk, not just an overall metric to hide.

## Repository structure

```text
Berlin-Mobility-AI/
├── notebooks/
│   ├── 01_exploratory_analysis.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── machine_learning.ipynb
├── src/
│   ├── explore_data.py
│   ├── inspect_headers.py
│   └── preprocess.py
├── README.md
├── requirements.txt
└── .gitignore
```

*Large raw/processed datasets and local virtual environments are intentionally excluded from Git.*

## Getting started

1. Clone the repository and install dependencies:

   ```bash
   git clone https://github.com/Hussein295/Berlin-Mobility-AI.git
   cd Berlin-Mobility-AI
   python -m venv .venv
   ```

2. Activate the environment:

   **Windows (PowerShell):**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux:**
   ```bash
   source .venv/bin/activate
   ```

3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Obtain the original bicycle count files from the [Berlin Open Data portal](https://daten.berlin.de/datensaetze/radzahldaten-in-berlin). Review the ingestion scripts in `src/` and adjust the local input paths to match the downloaded files. Generate the processed data before running downstream notebooks.

5. Explore the notebooks in this order: `01_exploratory_analysis.ipynb`, `02_feature_engineering.ipynb`, then `machine_learning.ipynb`.

> **Reproducibility note:** The repository currently contains the analysis and modeling code, not the large datasets. Full end-to-end execution may require adjusting local paths and regenerating intermediate files; a fully automated setup is planned.

## Technology

**Python · pandas · NumPy · scikit-learn · Jupyter · Matplotlib**

## Roadmap

- [x] Data exploration and preprocessing
- [x] Feature engineering and chronological splitting
- [x] Model benchmarking and held-out evaluation
- [x] Known-vs-unseen station analysis and grouped feature importance
- [ ] Interactive forecasting application (Phase 6)
- [ ] Streamlined reproducibility and final portfolio polish (Phase 7)

---

**Project focus:** Practical machine learning, careful temporal evaluation, explainability, and honest reporting of model limitations.
