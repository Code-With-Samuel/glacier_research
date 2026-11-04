# HKH Glacier Mass-Change and ERA5-Land Research

Research code and data-processing notebooks for preparing a Hindu Kush Himalaya
(HKH) glacier mass-change dataset, integrating ERA5-Land climate predictors,
exploring the data, and evaluating spatially grouped classification models. The
repository also contains a local Streamlit dashboard and the scripts used to
generate the paper figures.

The research paper is in
[`research_paper/final_research_paper.tex`](research_paper/final_research_paper.tex).
The paper uses figures generated into `research_paper/figures/`.

**GitHub repository:** [Code-With-Samuel/glacier_research](https://github.com/Code-With-Samuel/glacier_research)

## Repository structure

```text
glacier_research/
├── README.md
├── requirements.txt
├── .gitignore
├── gridded_mass_change_data_cleanup.ipynb
├── era5_nepal_climate_data_cleanup.ipynb
├── corrected_era5_land_data.ipynb
├── hkh_glacier_mass_change_era5land_integration.ipynb
├── glacier_eda_hkh.ipynb
├── supervised_learning_for_classification.ipynb
├── datasets/                                   # raw inputs (gitignored)
│   ├── copernicus_wgms_gridded_mass_change/
│   ├── era5_land_nepal_climate_1990-2026/
│   ├── climatetrace_emissions_co2_ch4_global_month/
│   └── ICIMOD 1990-2020/
├── datasets_to_csv/                            # intermediate CSVs (gitignored)
│   ├── copernicus_wgms_gridded_mass_change_csv/
│   ├── era5_land_nepal_climate_1990-2026_csv/
│   └── corrected_era5_land_data/
├── processed_data/                             # integrated table and diagnostics
│   ├── hkh_glacier_mass_change_era5land_hydrological_year_eda.csv
│   └── ... diagnostic CSVs
├── spatial_cv_outputs/                         # model and evaluation artifacts
│   ├── hkh_glacier_spatial_cv_selected_model.joblib
│   └── spatial_cv_*.csv
├── hkh_glacier_application/                    # Streamlit dashboard
│   ├── app.py
│   ├── README.md
│   └── MODEL_NOTES.md
├── references/                                 # source papers and citations
└── research_paper/
    ├── final_research_paper.tex
    ├── final_research_paper.bib
    ├── final_research_paper.pdf
    ├── references.bib
    ├── figures/
    ├── paper_figures/
    ├── research_audit/
    └── scripts/
        ├── make_figs.py
        ├── make_diag.py
        └── make_results_figs.py
```

Generated data directories and a local `.venv/` are not shown in the tree. The
single root `.venv` is shared by the notebooks, figure scripts, and dashboard.
No separate environment or data copy is used inside `hkh_glacier_application/`.

## Setup on Windows

Use Python 3.12. From PowerShell, at the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name glacier-research --display-name "Python (glacier-research)"
```

`requirements.txt` pins scikit-learn 1.6.1 because the saved model artifact was
created with that version.

If PowerShell prevents environment activation, either adjust the user execution
policy according to your organization's guidance or invoke the environment's
Python directly as `.\.venv\Scripts\python.exe`.

Use this one environment for every notebook and script below. Open the
repository root as the VS Code workspace, select the
`Python (glacier-research)` kernel for each notebook, and run cells from top to
bottom. If you prefer JupyterLab, install it into the same environment and start
it from the repository root:

```powershell
python -m pip install jupyterlab
jupyter lab
```

The notebook working directory must be the repository root because the setup
cells and some outputs use project-relative paths.

## How to run the notebooks

The table summarizes the workflow. Detailed instructions for each notebook are
provided in the following subsections.

| Notebook | Purpose | Main output or prerequisite |
|---|---|---|
| `gridded_mass_change_data_cleanup.ipynb` | Convert the annual Copernicus/WGMS gridded glacier mass-change NetCDF files to CSV and combine the annual records. | `datasets_to_csv/copernicus_wgms_gridded_mass_change_csv/nepal_glacier_data_1990-2024.csv` |
| `era5_nepal_climate_data_cleanup.ipynb` | Read the ERA5-Land NetCDF inputs and export the climate, coordinate, and cell-area CSV files used by integration. | `datasets_to_csv/era5_land_nepal_climate_1990-2026_csv/` |
| `corrected_era5_land_data.ipynb` | Combine the three monthly ERA5-Land recovery NetCDF files for the affected 2022-2024 period. | `datasets_to_csv/corrected_era5_land_data/combined_corrected_data.csv` |
| `hkh_glacier_mass_change_era5land_integration.ipynb` | Perform source-data checks, conservative regridding, monthly and April-March hydrological-year aggregation, replacement auditing, integration, and exports. | `processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv` plus diagnostic CSVs |
| `glacier_eda_hkh.ipynb` | Explore the integrated HKH table, its quality, spatial/temporal patterns, and relationships. | Reads the integrated CSV; includes interactive Folium visualizations |
| `supervised_learning_for_classification.ipynb` | Build three mass-change classes and compare four classifiers with five-fold spatially grouped validation. | Reads the integrated CSV; writes model and evaluation artifacts to `spatial_cv_outputs/` |

The integration workflow streams the large ERA5-Land CSV in chunks. The source
CSV is about 9.5 GB in the current dataset; allow substantial free disk space
for it and the intermediate monthly table.

### 1. `gridded_mass_change_data_cleanup.ipynb`

**Prerequisite:** place the annual Copernicus/WGMS gridded mass-change `.nc4`
files in `datasets/copernicus_wgms_gridded_mass_change/`.

**Run:** open the notebook from the repository root, select the
`Python (glacier-research)` kernel, and run all cells from top to bottom.

**Outputs:** one CSV per annual source file plus the combined table
`datasets_to_csv/copernicus_wgms_gridded_mass_change_csv/nepal_glacier_data_1990-2024.csv`.
The setup cell defines `source_dir`, `output_dir`, and `csv_dir`; check them if
the project is stored outside `E:\glacier_research`.

### 2. `era5_nepal_climate_data_cleanup.ipynb`

**Prerequisite:** place the ERA5-Land NetCDF files and coordinate/area files in
`datasets/era5_land_nepal_climate_1990-2026/`.

**Run:** open the notebook from the repository root and run all cells.

**Outputs:** the converted CSV files expected by the integration notebook,
including `data_stream-moda.csv`, `geo.csv`, and `cicecap.csv`, under
`datasets_to_csv/era5_land_nepal_climate_1990-2026_csv/`. Review the setup cell
variables `DATA_DIR`, `OUTPUT_DIR`, and any configured source-file paths.

### 3. `corrected_era5_land_data.ipynb`

**Prerequisite:** place the monthly recovery file `data_stream-mnth.nc` in each
of these folders:

- `datasets/era5_land_nepal_climate_1990-2026/corrected_data_2022_SeptoDec/`
- `datasets/era5_land_nepal_climate_1990-2026/corrected_data_2023_JantoDec/`
- `datasets/era5_land_nepal_climate_1990-2026/corrected_data_2024_JantoFeb/`

Create the output folder if it does not exist:

```powershell
New-Item -ItemType Directory -Force datasets_to_csv\corrected_era5_land_data | Out-Null
```

**Run:** open the notebook from the repository root and run all cells.

**Output:** `datasets_to_csv/corrected_era5_land_data/combined_corrected_data.csv`.
The setup cell contains the three `folders` entries and `output_path`.

### 4. `hkh_glacier_mass_change_era5land_integration.ipynb`

**Prerequisites:** confirm that these three files exist:

- `datasets_to_csv/copernicus_wgms_gridded_mass_change_csv/nepal_glacier_data_1990-2024.csv`
- `datasets_to_csv/era5_land_nepal_climate_1990-2026_csv/data_stream-moda.csv`
- `datasets_to_csv/corrected_era5_land_data/combined_corrected_data.csv`

**Run:** open the notebook from the repository root and run all cells. This step
streams and regrids the large ERA5-Land table and can take substantial time.

**Outputs:** the main annual table
`processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`
plus diagnostic CSVs in `processed_data/`. Review the overlap, missingness,
replacement, and monthly-completeness diagnostics before using the annual table.

The notebook avoids overwriting existing outputs by adding a timestamp to a
repeated filename. If rerunning, check its printed save paths and explicitly
point downstream notebooks at the intended current annual table. The setup cell
contains `TARGET_PATH`, `ERA5_PATH`, `CORRECTED_PATH`, and `OUTPUT_DIR`.

### 5. `glacier_eda_hkh.ipynb`

**Prerequisite:** the integrated table
`processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`.

**Run:** open the notebook from the repository root and run all cells. It uses
`DATA_PATH` in its setup cell.

**Outputs:** interactive plots, summary tables, and Folium maps displayed in the
notebook. No downstream file is required; Folium basemap tiles require an
internet connection.

### 6. `supervised_learning_for_classification.ipynb`

**Prerequisite:** the integrated table
`processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`.

**Run:** open the notebook from the repository root with `DATA_PATH` pointing at
that file, then run all cells. The full hyperparameter search and spatial
cross-validation can take substantial time.

**Outputs:** in `spatial_cv_outputs/`:

- `hkh_glacier_spatial_cv_selected_model.joblib`
- `spatial_cv_candidate_results.csv`
- `spatial_cv_fold_metrics.csv`
- `spatial_cv_oof_summary.csv`
- `spatial_cv_roc_auc.csv`
- `spatial_fold_assignments_summary.csv`

The notebook performs K-means clustering on unique locations and spatial
`StratifiedGroupKFold` validation. Its 25 clusters are groups for validation,
not a strict geographic buffer. The final model refitted on all observations is
an export artifact, not an independent performance evaluation.

## How to run the paper figure scripts

Run the scripts from the repository root after preparing the integrated CSV.
Activate the shared environment first if it is not already active:

```powershell
.\.venv\Scripts\Activate.ps1
python research_paper\scripts\make_figs.py
python research_paper\scripts\make_diag.py
```

`make_figs.py` generates the main paper figures and `correlation_matrix.csv` in
`research_paper/figures/`. Fig. 2's heatmap annotates each square with its
signed Pearson correlation coefficient, rounded to two decimals. The existing
color scale and `Pearson r` color bar indicate sign and magnitude; larger
absolute coefficients indicate stronger linear associations.

`make_diag.py` generates the ERA5-Land discontinuity diagnostic.

`make_results_figs.py` generates the model-result figures. Run
`supervised_learning_for_classification.ipynb` first with the notebook working
directory set to the repository root; it writes the candidate and fold tables
to `spatial_cv_outputs/`. The figure script selects each model's best
configuration using the notebook's macro-F1, balanced-accuracy, and accuracy
ranking, then uses its five validation-fold macro-F1 values. Alternatively,
provide `research_paper/figures/fold_f1.json` with this shape:

```json
{
  "Gradient Boosting": [0.0, 0.0, 0.0, 0.0, 0.0],
  "Random Forest": [0.0, 0.0, 0.0, 0.0, 0.0],
  "SVM (RBF)": [0.0, 0.0, 0.0, 0.0, 0.0],
  "Logistic Regression": [0.0, 0.0, 0.0, 0.0, 0.0]
}
```

Replace the example zeroes with actual per-fold results; never use the
placeholder values. The remaining aggregate metrics and confusion-matrix counts
in `make_results_figs.py` are reported-result constants; update them from the
experiment outputs if you change or rerun the analysis. Then run:

```powershell
python research_paper\scripts\make_results_figs.py
```

The descriptive figure scripts use GeoPandas and download the Natural Earth land
boundary dataset through `geodatasets` on first use, so internet access may be
required.

## How to run the dashboard

`hkh_glacier_application/` contains a local Streamlit research dashboard for
exploring the integrated table, mapping grid records, and running the selected
Gradient Boosting classifier. It reads the shared project artifacts directly
and keeps no copy under the application folder:

- `processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`
- `spatial_cv_outputs/hkh_glacier_spatial_cv_selected_model.joblib`

Both files must exist before starting the app. The integration notebook produces
the dataset, and the modeling notebook produces the model artifact.

From the repository root, using the shared project environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run hkh_glacier_application\app.py
```

You can also invoke the environment directly without activating it:

```powershell
.\.venv\Scripts\python.exe -m streamlit run hkh_glacier_application\app.py
```

Open the local URL printed in the terminal, normally
`http://localhost:8501`. There is no launcher script and no application-specific
virtual environment; the root `.venv` is used for everything. See
[`hkh_glacier_application/README.md`](hkh_glacier_application/README.md) for
dashboard details and shared interpretation caveats.

## Data requirements

Raw datasets, intermediate CSVs, and most processed outputs are ignored by
`.gitignore`. The annual integrated table
`processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv` is
explicitly exempted so it can be committed; it will appear in a clone only after
it has been added and pushed. Other data files and directories may not be
present in a GitHub clone. Obtain missing data from the original sources and
follow their citation and attribution terms.

| Input | Expected location in this project |
|---|---|
| Annual Copernicus/WGMS gridded mass-change NetCDF files ([dataset page](https://cds.climate.copernicus.eu/datasets/derived-gridded-glacier-mass-change?tab=overview)) | `datasets/copernicus_wgms_gridded_mass_change/` |
| ERA5-Land NetCDF and coordinate/area files ([dataset page](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview)) | `datasets/era5_land_nepal_climate_1990-2026/` |
| ERA5-Land monthly recovery NetCDFs for the affected months | `datasets/era5_land_nepal_climate_1990-2026/corrected_data_2022_SeptoDec/`, `corrected_data_2023_JantoDec/`, and `corrected_data_2024_JantoFeb/` |
| Converted ERA5-Land CSVs used by integration | `datasets_to_csv/era5_land_nepal_climate_1990-2026_csv/` |
| Combined corrected monthly ERA5-Land CSV | `datasets_to_csv/corrected_era5_land_data/combined_corrected_data.csv` |
| Combined gridded mass-change CSV | `datasets_to_csv/copernicus_wgms_gridded_mass_change_csv/nepal_glacier_data_1990-2024.csv` |
| Selected model artifact for the dashboard (generated by the modeling notebook) | `spatial_cv_outputs/hkh_glacier_spatial_cv_selected_model.joblib` |

### Path configuration

The notebooks currently use the project location `E:\glacier_research` in their
configuration cells. If the repository is elsewhere, update those path constants
to the corresponding local folders before running:

- `gridded_mass_change_data_cleanup.ipynb`: `source_dir`, `output_dir`, and
  `csv_dir`.
- `era5_nepal_climate_data_cleanup.ipynb`: `DATA_DIR`, `OUTPUT_DIR`, and any
  configured source-file paths.
- `corrected_era5_land_data.ipynb`: the three `folders` entries and
  `output_path`.
- `hkh_glacier_mass_change_era5land_integration.ipynb`: `TARGET_PATH`,
  `ERA5_PATH`, `CORRECTED_PATH`, and `OUTPUT_DIR`.
- `glacier_eda_hkh.ipynb` and `supervised_learning_for_classification.ipynb`:
  `DATA_PATH`.
- `hkh_glacier_application/app.py`: paths are derived from the script location,
  so no edits are needed as long as `hkh_glacier_application/` remains inside the
  repository and the two input files stay in `processed_data/` and
  `spatial_cv_outputs/`.

The integrated table expected by the EDA, modeling, paper figure scripts, and
dashboard is
`processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`. If
this file already exists and is current, you can start at the EDA or modeling
notebook without rerunning the large data-preparation steps.

The Climate TRACE files under
`datasets/climatetrace_emissions_co2_ch4_global_month/` are an additional dataset
and are not an input to the glacier mass-change pipeline described here.

## End-to-end rebuild order

1. **Prepare the target table.** Run
   `gridded_mass_change_data_cleanup.ipynb` after placing the annual `.nc4`
   files. Confirm the combined CSV exists.
2. **Prepare ERA5-Land exports.** Run
   `era5_nepal_climate_data_cleanup.ipynb` after placing the source NetCDFs and
   coordinate/area files. Verify the CSV outputs and names expected by the
   integration notebook.
3. **Prepare the recovery data.** Place `data_stream-mnth.nc` in each recovery
   folder, create `datasets_to_csv/corrected_era5_land_data/` if needed, and run
   `corrected_era5_land_data.ipynb`.
4. **Integrate and audit.** Run
   `hkh_glacier_mass_change_era5land_integration.ipynb` and review its
   diagnostics before using the exported annual table.
5. **Explore and model.** Run `glacier_eda_hkh.ipynb`, then
   `supervised_learning_for_classification.ipynb`.
6. **Regenerate paper graphics.** Run `make_figs.py`, `make_diag.py`, and, after
   the modeling notebook has produced `spatial_cv_outputs/`,
   `make_results_figs.py`.
7. **Launch the dashboard (optional).** Confirm the integrated CSV and model
   artifact exist, then run the Streamlit command in
   [How to run the dashboard](#how-to-run-the-dashboard).
8. **Compile the paper.** Use the LaTeX commands in
   [Compile the paper](#compile-the-paper).

Do not rerun an upstream conversion if its existing output is the intended input
and is already audited. Some notebooks write large files or refuse to overwrite
existing outputs; inspect the configured output path before reruns.

## Compile the paper

Install a LaTeX distribution that includes IEEEtran, `pdflatex`, and BibTeX (for
example, MiKTeX on Windows). From the paper directory:

```powershell
Set-Location research_paper
pdflatex -interaction=nonstopmode final_research_paper.tex
bibtex final_research_paper
pdflatex -interaction=nonstopmode final_research_paper.tex
pdflatex -interaction=nonstopmode final_research_paper.tex
Set-Location ..
```

The paper's `\graphicspath` points to `research_paper/figures/`; keep generated
figure filenames in that directory. Check the LaTeX log for missing figures,
references, or bibliography entries.

## Reproducibility and interpretation notes

- The classification target uses fixed thresholds of `+0.1` and `-0.1` m water
  equivalent. See the notebook and paper for the class definitions and
  uncertainty caveats.
- Spatial validation keeps each K-means location cluster in one fold. This
  evaluates transfer across clusters, not forecasting future years at known
  locations; cluster boundaries are not a distance buffer.
- The final model refitted on all observations is an export artifact, not an
  independent performance evaluation.
- The paper documents unresolved ERA5-Land recovery semantics and other
  methodological limitations. Review those caveats before interpreting or
  reusing reported scores.
- Source data citations and attribution details are in
  `references/data_papers_and_citations_references.txt`.
