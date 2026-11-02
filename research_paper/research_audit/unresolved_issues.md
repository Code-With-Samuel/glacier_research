# Unresolved issues (as of this draft)
1. ERA5-Land t2m/u10/v10 for Sep 2022-Feb 2024 were replaced from the 00:00 hour-of-day recovery product although ECMWF lists only *accumulated* variables as affected. Grid-mean t2m is -2.85 SD (HY2023) and -7.79 SD (HY2024) vs 1991-2021. Needs: keep original moda values for non-accumulated variables, verify accumulated recovery semantics, rerun table + models.
2. Tuning and reporting share the same folds (no nested CV, no locked test, no chronological holdout).
3. Fixed +/-0.1 m w.e. thresholds vs median uncertainty 0.186; uncertainty definition (1 sigma / 1.96 sigma) unconfirmed.
4. K-means/fold assignment is library-version dependent: re-running the notebook logic in a different sklearn version gave different fold sizes, so the paper uses the notebook's own saved outputs only. Export cluster IDs and fold IDs to CSV for reproducibility.
5. Confusion-matrix counts were read from the notebook's rendered figure (each matrix verified to sum to class supports). Export them as CSV.
6. Timings come from one hosted run with unrecorded hardware; no memory profile.
7. No official ICIMOD HKH boundary used (map shows envelope of occupied cells).
8. Library versions not recorded in the paper; add environment file.
9. Local E:\ project tree, IEEEtran_HOWTO.pdf and the coursework brief were not accessible; only the 7 uploaded files and 3 project files were audited.
10. Target conference page limit unknown (draft is 18 pages).
