# Model artifact notes

- Selected estimator: `GradientBoostingClassifier`
- Input count: 17
- Class encoding from the notebook's `LabelEncoder`: 0 = mass gain, 1 = mass loss, 2 = near balance.
- Training artifact: `hkh_glacier_spatial_cv_selected_model.joblib`
- Model persistence compatibility: artifact reports scikit-learn 1.6.1; the root `requirements.txt` pins 1.6.1 in the shared `.venv`.
- Do not treat `feature_importances_` as local explanations or causal effects.
