# HKH Glacier Mass-Change Intelligence

A local interactive research dashboard built from the supplied HKH hydrological-year dataset, supervised-learning notebook, and selected Gradient Boosting model.

## Features

- Overview dashboard with dataset KPIs, observed annual mass-change trend, class distribution, and model comparison.
- Exploratory analysis: distributions, annual trends, class proportions, correlation matrix, scatter plots, descriptive statistics, missingness, and uncertainty profile.
- Geographic explorer: interactive Folium map on an OpenStreetMap/Carto basemap, with year/class/metric filters.
- Prediction laboratory with **both** workflows:
  1. Historical record selection by hydrological year and grid coordinate, with editable model inputs.
  2. Manual entry of all 17 model features and separate latitude/longitude context.
- Prediction probabilities, feature values, global model feature importance, location map, and CSV export.
- Model evaluation and methodology page with spatial out-of-fold metrics and limitations.
- Dataset catalogue with class thresholds, feature list, coverage, and CSV download.

## Data inputs

The application does not bundle its own copy of the data. It reads the shared
project artifacts from the repository root, resolved relative to `app.py`:

- `processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`
- `spatial_cv_outputs/hkh_glacier_spatial_cv_selected_model.joblib`

The dataset is produced by
`hkh_glacier_mass_change_era5land_integration.ipynb`; the model artifact is
produced by `supervised_learning_for_classification.ipynb` at the repository
root. Both notebooks must be run from the repository root before starting the
application.

## Quick start (Windows)

The dashboard uses the repository's single root `.venv`, the same environment as
the notebooks and paper scripts. Do not create a separate environment in this
folder.

1. Install Python 3.12. The model artifact was saved using scikit-learn 1.6.1,
   which is pinned in the root `requirements.txt`.
2. From the repository root, create the environment once:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. Confirm that the two input files listed in [Data inputs](#data-inputs)
   exist.
4. Start the application from the repository root:

   ```powershell
   python -m streamlit run hkh_glacier_application\app.py
   ```

5. Open the local URL printed in the terminal (normally http://localhost:8501).

There is no launcher script. Always start the app from the repository root with
the shared `.venv`; never create a separate environment in this folder.

## Quick start (macOS / Linux)

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run hkh_glacier_application/app.py
```

## Important scientific notes

- The target is reconstructed from `glacier_mass_change_mwe` using the notebook's thresholds: mass gain > +0.1 m w.e.; mass loss < −0.1 m w.e.; near balance otherwise.
- The 17 model inputs are `glacier_area_km2`, `hydrological_year`, and 15 ERA5-Land predictors: `t2m`, `snowc`, `sde`, `sd`, `sf`, `smlt`, `ssr`, `str`, `ro`, `es`, `sro`, `e`, `u10`, `v10`, `tp`.
- Latitude and longitude are not model predictors; they are used only for spatial display and historical record selection.
- The historical workflow uses records from the supplied dataset. Those records were also used in fitting the final model, so the comparison between predicted and observed class is **in-sample**, not an independent test.
- The model uses full hydrological-year climate aggregates and hydrological year. It is therefore a retrospective condition classifier, not a prediction that can be issued before the hydrological year has completed.
- The notebook reports spatial OOF metrics from five spatially grouped folds. The same folds were used for hyperparameter selection and reporting, so the metrics are not an independent nested-CV estimate. The notebook recommends nested spatial CV or an untouched spatial test region for publication-grade performance estimation.
- Near-balance classification is weak in the reported results (F1 = 0.35); class-wise metrics matter.
- The interactive OpenStreetMap basemap requires an internet connection to load map tiles; it does not require a CartoDB API key.
- This is a research and exploratory tool, not a glacier monitoring authority, GLOF warning system, or operational hazard product.

## Project structure

```text
glacier_research/
├── .venv/                    # shared environment for notebooks and the app
├── requirements.txt
├── processed_data/
│   └── hkh_glacier_mass_change_era5land_hydrological_year_eda.csv
├── spatial_cv_outputs/
│   └── hkh_glacier_spatial_cv_selected_model.joblib
└── hkh_glacier_application/
    ├── app.py
    ├── README.md
    └── MODEL_NOTES.md
```

The application directory intentionally has no local `data/`, `.venv/`, or
`requirements.txt`. Both inputs are read from the shared project directories,
and dependencies come from the root environment. Keep the relative layout
intact when moving or copying the project.

## Troubleshooting

- If start-up reports a missing dataset or model file, run the two producing notebooks from the repository root (see [Data inputs](#data-inputs)) and verify the paths shown above.
- If the environment is missing, create the root `.venv` once from the repository root as shown in [Quick start (Windows)](#quick-start-windows).
- If the model fails to load, verify that scikit-learn 1.6.1 is installed in the root `.venv` (`python -c "import sklearn; print(sklearn.__version__)"`).
- If `streamlit` is not recognised, run it through the root environment: `.\.venv\Scripts\python.exe -m streamlit run hkh_glacier_application\app.py`.
- If the map background is blank, check internet connectivity; map tiles are fetched from the tile provider.
- Both map instances use the OpenStreetMap tile layer rather than the CartoDB Positron layer, which can show an `API KEY REQUIRED` watermark. Stop any old Streamlit process with `Ctrl+C` and restart it; a browser refresh alone does not replace the running Python code.


## Visual update: mass-change class colours

All class-based charts and map legends now use a stronger, more distinguishable palette:
- Mass loss: vermilion (`#D55E00`)
- Near balance: magenta (`#CC79A7`)
- Mass gain: blue (`#0072B2`)

The predictor distribution histograms use a semi-transparent overlay and light bar outlines so the near-balance class remains visible when distributions overlap. The same class colours are used consistently across charts and the geographic explorer.
