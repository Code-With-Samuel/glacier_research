# HKH Glacier Mass-Change and ERA5-Land Research

Research code and data-processing notebooks for preparing a Hindu Kush Himalaya
(HKH) glacier mass-change dataset, integrating ERA5-Land climate predictors,
exploring the data, and evaluating spatially grouped classification models.

The research paper is in [`research_paper/final_research_paper.tex`](research_paper/final_research_paper.tex).
The paper uses figures generated into `research_paper/figures/`.

**GitHub repository:** [Code-With-Samuel/glacier_research](https://github.com/Code-With-Samuel/glacier_research)

## What is in this repository

### Notebooks

Run notebooks from top to bottom, in the order below when rebuilding the data.
The preprocessing and modeling notebooks use local paths configured in their
setup cells; see [Path configuration](#path-configuration).

| Notebook | Purpose | Main output or prerequisite |
|---|---|---|
| `gridded_mass_change_data_cleanup.ipynb` | Convert the annual Copernicus/WGMS gridded glacier mass-change NetCDF files to CSV and combine the annual records. | `datasets_to_csv/copernicus_wgms_gridded_mass_change_csv/nepal_glacier_data_1990-2024.csv` |
| `era5_nepal_climate_data_cleanup.ipynb` | Read the ERA5-Land NetCDF inputs and export the climate, coordinate, and cell-area CSV files used by integration. | `datasets_to_csv/era5_land_nepal_climate_1990-2026_csv/` |
| `corrected_era5_land_data.ipynb` | Combine the three monthly ERA5-Land recovery NetCDF files for the affected 2022–2024 period. | `datasets_to_csv/corrected_era5_land_data/combined_corrected_data.csv` |
| `hkh_glacier_mass_change_era5land_integration.ipynb` | Perform source-data checks, conservative regridding, monthly and April–March hydrological-year aggregation, replacement auditing, integration, and exports. | `processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv` plus diagnostic CSVs |
| `glacier_eda_hkh.ipynb` | Explore the integrated HKH table, its quality, spatial/temporal patterns, and relationships. | Reads the integrated CSV; includes interactive Folium visualizations |
| `supervised_learning_for_classification.ipynb` | Build three mass-change classes and compare four classifiers with five-fold spatially grouped validation. | Reads the integrated CSV; writes model and evaluation artifacts to `spatial_cv_outputs/` |

The integration workflow streams the large ERA5-Land CSV in chunks. The source
CSV is about 9.5 GB in the current dataset; allow substantial free disk space
for it and the intermediate monthly table.

### Paper figure scripts

Run the descriptive figure scripts from the repository root after preparing
the integrated CSV:

```powershell
python research_paper\scripts\make_figs.py
python research_paper\scripts\make_diag.py
```

`make_figs.py` generates the main paper figures and `correlation_matrix.csv` in
`research_paper/figures/`. Fig. 2's heatmap annotates each square with its
signed Pearson correlation coefficient, rounded to two decimals. The existing
color scale and `Pearson r` color bar indicate sign and magnitude; larger
absolute coefficients indicate stronger linear associations.

`make_diag.py` generates the ERA5-Land discontinuity diagnostic.
`make_results_figs.py` generates the model-result figures. First run
`supervised_learning_for_classification.ipynb` with the notebook working
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
placeholder values. The remaining aggregate metrics and confusion-matrix
counts in `make_results_figs.py` are reported-result constants; update them
from the experiment outputs if you change or rerun the analysis. Then run:

```powershell
python research_paper\scripts\make_results_figs.py
```

## Data requirements

Raw datasets, intermediate CSVs, and most processed outputs are ignored by
`.gitignore`. The annual integrated table
`processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`
is explicitly exempted so it can be committed; it will appear in a clone only
after it has been added and pushed. Other data files and directories may not be
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

### Path configuration

The notebooks currently use the project location `E:\glacier_research` in
their configuration cells. If the repository is elsewhere, update those path
constants to the corresponding local folders before running:

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

The integrated table expected by the EDA, modeling, and paper figure scripts
is `processed_data/hkh_glacier_mass_change_era5land_hydrological_year_eda.csv`.
If this file already exists and is current, you can start at the EDA or
modeling notebook without rerunning the large data-preparation steps.

The Climate TRACE files under `datasets/climatetrace_emissions_co2_ch4_global_month/`
are an additional dataset and are not an input to the glacier mass-change
pipeline described here.

## Setup on Windows

Use Python 3.12 or another Python version supported by the installed scientific
Python packages. From PowerShell, at the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name glacier-research --display-name "Python (glacier-research)"
```

If PowerShell prevents environment activation, either adjust the user execution
policy according to your organization's guidance or invoke the environment's
Python directly as `.\.venv\Scripts\python.exe`.

Open the repository root as the VS Code workspace, select the
`Python (glacier-research)` kernel for each notebook, and run cells from top to
bottom. The paper figure script uses GeoPandas and downloads its Natural Earth
land boundary dataset through `geodatasets` on first use, so internet access
may be required. Folium basemap tiles also require internet access.

## Rebuild the research table and results

1. **Prepare the target table.** Put all annual mass-change `.nc4` files in
   `datasets/copernicus_wgms_gridded_mass_change/`. Run
   `gridded_mass_change_data_cleanup.ipynb`; confirm that the combined CSV
   exists at the target path listed above.
2. **Prepare ERA5-Land exports.** Put the source NetCDFs and coordinate/area
   files in `datasets/era5_land_nepal_climate_1990-2026/`. Run
   `era5_nepal_climate_data_cleanup.ipynb`; verify the CSV outputs and names
   expected by the integration notebook.
3. **Prepare the recovery data.** Place `data_stream-mnth.nc` in each of the
   three recovery folders. Create the converted-output folder if it does not
   exist, then run `corrected_era5_land_data.ipynb`:

   ```powershell
   New-Item -ItemType Directory -Force datasets_to_csv\corrected_era5_land_data | Out-Null
   ```

   Verify that `combined_corrected_data.csv` was written there.
4. **Integrate and audit.** Run
   `hkh_glacier_mass_change_era5land_integration.ipynb` from its first cell.
   Review its overlap, missingness, replacement, and monthly-completeness
   diagnostics before using the exported annual table. The notebook avoids
   overwriting existing outputs by adding a timestamp to a repeated filename;
   if rerunning, check its printed save paths and explicitly point downstream
   notebooks at the intended current annual table.
5. **Explore and model.** Run `glacier_eda_hkh.ipynb`, then
   `supervised_learning_for_classification.ipynb`. The modeling notebook
   performs K-means clustering on unique locations and spatial
   `StratifiedGroupKFold` validation; the full search can take substantial
   time. Its 25 clusters are groups for validation, not a strict geographic
   buffer.
6. **Regenerate paper graphics.** Run `make_figs.py` and `make_diag.py` using
   the commands above. After the modeling notebook has produced
   `spatial_cv_outputs/` (step 5), run `make_results_figs.py` as documented in
   the paper-figure section. Compile the paper as described below.

Do not rerun an upstream conversion if its existing output is the intended
input and is already audited. Some notebooks write large files or refuse to
overwrite existing outputs; inspect the configured output path before reruns.

## Compile the paper

Install a LaTeX distribution that includes IEEEtran, `pdflatex`, and BibTeX
(for example, MiKTeX on Windows). From the paper directory:

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

- The classification target uses fixed thresholds of `+0.1` and `-0.1` m
  water equivalent. See the notebook and paper for the class definitions and
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
