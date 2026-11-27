# LandGuard AI Backend

LandGuard is a Flask API that estimates whether an infrastructure project was overdue as of July 2026, based on project cost, expenditure, and physical progress. The current model is trained on project information extracted from the Government of India's MoSPI PAIMANA July 2026 Flash Report.

> **Scope:** This version predicts observed overdue status against the original project schedule. It does not determine why a project was delayed and is not a forecast of future land-acquisition delay.

## How it works

The API loads the trained scikit-learn model from `landguard_model.pkl`. The `/predict-delay` endpoint requires a valid Supabase access token, validates the input values, and returns an overdue probability, risk level, and binary prediction.

The model uses these four numeric inputs:

| Field | Description | Validation |
| --- | --- | --- |
| `original_cost_crore` | Original project cost in crore rupees | Greater than 0 |
| `revised_cost_crore` | Revised project cost in crore rupees | 0 or greater |
| `cumulative_expenditure_crore` | Cumulative expenditure in crore rupees | 0 or greater |
| `physical_progress_percent` | Physical progress percentage | 0–100 |

The response includes `overdue_probability`, `risk_level` (`Low`, `Medium`, or `High`), `prediction` (`Overdue` or `Not Overdue`), `model_version`, and `target_definition`.

## Requirements

- Python 3.10 or newer
- pip
- Supabase project URL and anon key for API authentication

## Setup

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root with your Supabase settings:

```dotenv
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-supabase-anon-key
```

Keep `.env` private. It is excluded from Git by `.gitignore`.

## Run the API

```powershell
python app.py
```

The development server listens on `http://localhost:5000`. The root endpoint can be used to check that the API is running:

```powershell
curl http://localhost:5000/
```

## Predict overdue status

Send a `POST` request to `/predict-delay` with a Supabase access token and JSON body:

```powershell
$token = "your-supabase-access-token"
$body = @{
  original_cost_crore = 1200
  revised_cost_crore = 1350
  cumulative_expenditure_crore = 780
  physical_progress_percent = 58
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:5000/predict-delay" `
  -Method Post `
  -Headers @{ Authorization = "Bearer $token" } `
  -ContentType "application/json" `
  -Body $body
```

The API checks the bearer token with Supabase Auth before processing the prediction. It returns HTTP 401 for missing or invalid sessions and HTTP 400 for invalid input.

## Data and model

- `data/paimana_project_delay_data.csv` contains the prepared July 2026 PAIMANA project data used for training.
- `data/raw/FlashReport_July_2026.pdf` is the source report referenced by the prepared dataset.
- `prepare_paimana_dataset.py` prepares the dataset from the source report.
- `train_model.py` trains the model and saves it to `landguard_model.pkl`.
- `DATA_SOURCES.md` documents the data, label definition, and limitations.

To prepare the dataset and retrain the model:

```powershell
python prepare_paimana_dataset.py
python train_model.py
```

The target column, `delayed_vs_original_target_as_of_2026_07`, marks an ongoing project as overdue when its original target completion month was before July 2026. Schedule dates are retained for auditability but excluded from the model inputs because the original target date defines the label.

## Project files

- `app.py` — Flask API and Supabase authentication
- `landguard_model.pkl` — trained prediction pipeline used by the API
- `train_model.py` — model training script
- `prepare_paimana_dataset.py` — PAIMANA data preparation script
- `DATA_SOURCES.md` — source and target documentation
- `requirements.txt` — Python dependencies

## Notes

The frontend must submit the four PAIMANA model inputs listed above. The API's CORS settings currently allow the frontend origins configured in `app.py`; update those origins when deploying a different frontend.
