Berlin Mobility AI
Forecasting hourly bicycle traffic at Berlin’s automated counting stations using calendar features and station identity. The project covers 2.2 million hourly observations from 2017 to 2025. Histogram-based gradient boosting reduced validation MAE by 24% against a historical-average baseline and achieved a test MAE of 33.24 bicycles per station-hour.
Results
Models were selected on a chronological validation split and evaluated on a later, held-out test split. MAE and RMSE are measured in bicycles per station-hour.
Model	Split	MAE ↓	RMSE ↓	R² ↑
Historical-average baseline	Validation	40.74	68.64	0.6654
Linear regression	Validation	58.22	86.04	0.4742
Decision tree	Validation	43.30	74.33	0.6076
Random forest	Validation	35.95	64.17	0.7075
Gradient boosting	Validation	30.94	53.03	0.8003
Gradient boosting	Held-out test	33.24	57.95	0.7295


Test MAE was 28.38 at 30 stations seen during training and 63.14 at five unseen stations. The error at unseen stations was more than twice as high, which limits the model’s usefulness for newly added counters. Grouped permutation importance on a validation sample ranked hour of day and station identity as the two most influential feature groups.
Data and modeling
- Data · 2,216,184 observations across 35 station IDs. The pipeline combines annual sheets, examines missing values and outliers, and uses the 2017–2025 subset for modeling. Berlin Open Data · Radzähldaten in Berlin
- Features · Calendar variables, cyclical encodings for hour, day of week and month, and one-hot-encoded station IDs.
- Baseline · Historical mean for each station, weekday and hour, with fallbacks to the weekday-hour mean and then the overall training mean.
- Evaluation · Chronological training, validation and test splits with approximately 1.43 million, 380,000 and 410,000 observations, respectively.
Run locally
1. Open the project folder and install dependencies in your Python environment.
   python -m pip install -r requirements.txt
2. Download the Excel workbook from Berlin Open Data. The ingestion setup uses data/raw/berlin_bicycle_counts.xlsx.
3. Select that Python environment as your notebook kernel. Run the workflow in this order: data ingestion → exploratory analysis → feature engineering and chronological split → model training → held-out evaluation. The model training notebook reads train.parquet, validation.parquet, and test.parquet from data/processed/.
Project status
The modeling and evaluation notebooks are complete. An interactive forecasting app is planned.