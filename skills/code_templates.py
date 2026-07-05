"""
Code Templates Skill — Template-based ML code generation.

Provides tested building blocks for generating baseline competition code.
Templates are parameterized with competition-specific values (target column,
features, model type, etc.) to produce runnable Python scripts.

Concept demonstrated: Agent Skills — Modular, reusable capability
that encapsulates code generation patterns.
"""

from typing import Any


def generate_imports(model_family: str = "tree_based") -> str:
    """Generates import statements based on the model family."""
    base_imports = """\"\"\"
Auto-generated baseline by KaggleBot.
Competition analysis and code generation powered by Google ADK.
\"\"\"

import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')
"""

    if model_family == "tree_based":
        base_imports += """
# Tree-based models
try:
    import lightgbm as lgb
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False
    print("LightGBM not installed. Using sklearn GradientBoosting instead.")

from sklearn.ensemble import GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
"""
    elif model_family == "linear":
        base_imports += """
# Linear models
from sklearn.linear_model import LogisticRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler
"""
    elif model_family == "ensemble":
        base_imports += """
# Ensemble models
try:
    import lightgbm as lgb
    HAS_LGBM = True
except ImportError:
    HAS_LGBM = False

from sklearn.ensemble import (
    GradientBoostingClassifier, GradientBoostingRegressor,
    RandomForestClassifier, RandomForestRegressor,
    StackingClassifier, StackingRegressor,
)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.preprocessing import StandardScaler
"""

    return base_imports


def generate_data_loading(
    train_path: str = "train.csv",
    test_path: str | None = "test.csv",
    target_column: str = "target",
    id_column: str | None = "id",
) -> str:
    """Generates data loading and basic preprocessing code."""
    code = f"""
# ============================================================
# 1. DATA LOADING
# ============================================================
print("Loading data...")
train = pd.read_csv("{train_path}")
"""
    if test_path:
        code += f'test = pd.read_csv("{test_path}")\n'

    code += f"""
TARGET = "{target_column}"
"""
    if id_column:
        code += f'ID_COL = "{id_column}"\n'

    code += f"""
print(f"Train shape: {{train.shape}}")
"""
    if test_path:
        code += 'print(f"Test shape: {test.shape}")\n'

    code += f'print(f"Target distribution:\\n{{train[TARGET].value_counts()}}")\n'

    return code


def generate_preprocessing(
    numeric_features: list[str] | None = None,
    categorical_features: list[str] | None = None,
    drop_columns: list[str] | None = None,
    target_column: str = "target",
) -> str:
    """Generates preprocessing code for numeric and categorical features."""
    code = """
# ============================================================
# 2. PREPROCESSING
# ============================================================
print("Preprocessing...")

"""
    if drop_columns:
        cols_str = ", ".join(f'"{c}"' for c in drop_columns)
        code += f"drop_cols = [{cols_str}]\n"
        code += "train = train.drop(columns=[c for c in drop_cols if c in train.columns], errors='ignore')\n"
        code += "if 'test' in dir():\n"
        code += "    test = test.drop(columns=[c for c in drop_cols if c in test.columns], errors='ignore')\n\n"

    code += f"""# Separate target
y_train = train[TARGET]
X_train = train.drop(columns=[TARGET])
"""

    code += """
# Identify feature types
numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
categorical_cols = X_train.select_dtypes(exclude=[np.number]).columns.tolist()

print(f"Numeric features: {len(numeric_cols)}")
print(f"Categorical features: {len(categorical_cols)}")

# Handle missing values
for col in numeric_cols:
    median_val = X_train[col].median()
    X_train[col] = X_train[col].fillna(median_val)
    if 'test' in dir():
        test[col] = test[col].fillna(median_val)

for col in categorical_cols:
    mode_val = X_train[col].mode()[0] if not X_train[col].mode().empty else "Unknown"
    X_train[col] = X_train[col].fillna(mode_val)
    if 'test' in dir():
        test[col] = test[col].fillna(mode_val)

# Encode categorical features
label_encoders = {}
for col in categorical_cols:
    le = LabelEncoder()
    X_train[col] = le.fit_transform(X_train[col].astype(str))
    if 'test' in dir():
        test[col] = test[col].apply(lambda x: x if x in le.classes_ else "Unknown")
        le_classes = list(le.classes_) + ["Unknown"]
        le.classes_ = np.array(le_classes)
        test[col] = le.transform(test[col].astype(str))
    label_encoders[col] = le

print("Preprocessing complete!")
"""
    return code


def generate_feature_engineering(
    feature_hints: list[str] | None = None,
) -> str:
    """Generates feature engineering code based on hints."""
    code = """
# ============================================================
# 3. FEATURE ENGINEERING
# ============================================================
print("Feature engineering...")

"""
    if feature_hints:
        code += "# Feature engineering suggestions from competition analysis:\n"
        for hint in feature_hints:
            code += f"# - {hint}\n"
        code += "\n"

    code += """# Add your custom features here
# Example: X_train['new_feature'] = X_train['col1'] * X_train['col2']

print(f"Final feature count: {X_train.shape[1]}")
"""
    return code


def generate_model_training(
    task_type: str = "binary_classification",
    model_family: str = "tree_based",
    metric: str = "accuracy",
    n_folds: int = 5,
) -> str:
    """Generates model training code with cross-validation."""

    if task_type in ("binary_classification", "classification"):
        if model_family == "tree_based":
            code = f"""
# ============================================================
# 4. MODEL TRAINING
# ============================================================
print("Training model...")

# Model selection
if HAS_LGBM:
    model = lgb.LGBMClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=6,
        num_leaves=31,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbose=-1,
    )
    model_name = "LightGBM"
else:
    model = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=5,
        random_state=42,
    )
    model_name = "GradientBoosting (sklearn)"

# Cross-validation
skf = StratifiedKFold(n_splits={n_folds}, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring="{metric}")

print(f"\\n{{model_name}} CV Results:")
print(f"  Mean {metric}: {{cv_scores.mean():.4f}} (+/- {{cv_scores.std():.4f}})")
print(f"  Per-fold: {{[f'{{s:.4f}}' for s in cv_scores]}}")

# Train on full data
model.fit(X_train, y_train)
print("\\nModel trained on full dataset!")
"""
        elif model_family == "linear":
            code = f"""
# ============================================================
# 4. MODEL TRAINING
# ============================================================
print("Training model...")

# Scale features for linear model
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

model = LogisticRegression(
    C=1.0,
    max_iter=1000,
    random_state=42,
)
model_name = "Logistic Regression"

# Cross-validation
skf = StratifiedKFold(n_splits={n_folds}, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=skf, scoring="{metric}")

print(f"\\n{{model_name}} CV Results:")
print(f"  Mean {metric}: {{cv_scores.mean():.4f}} (+/- {{cv_scores.std():.4f}})")

# Train on full data
model.fit(X_train_scaled, y_train)
print("Model trained on full dataset!")
"""
        else:  # ensemble
            code = f"""
# ============================================================
# 4. MODEL TRAINING
# ============================================================
print("Training model...")

model = StackingClassifier(
    estimators=[
        ('rf', RandomForestClassifier(n_estimators=200, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=200, random_state=42)),
    ],
    final_estimator=LogisticRegression(max_iter=1000),
    cv={n_folds},
)
model_name = "Stacking Ensemble"

skf = StratifiedKFold(n_splits={n_folds}, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train, y_train, cv=skf, scoring="{metric}")

print(f"\\n{{model_name}} CV Results:")
print(f"  Mean {metric}: {{cv_scores.mean():.4f}} (+/- {{cv_scores.std():.4f}})")

model.fit(X_train, y_train)
print("Model trained on full dataset!")
"""
    else:  # regression
        code = f"""
# ============================================================
# 4. MODEL TRAINING
# ============================================================
print("Training model...")

if HAS_LGBM:
    model = lgb.LGBMRegressor(
        n_estimators=500, learning_rate=0.05,
        max_depth=6, random_state=42, verbose=-1,
    )
    model_name = "LightGBM Regressor"
else:
    model = GradientBoostingRegressor(
        n_estimators=200, learning_rate=0.1,
        max_depth=5, random_state=42,
    )
    model_name = "GradientBoosting Regressor"

from sklearn.model_selection import KFold
kf = KFold(n_splits={n_folds}, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train, y_train, cv=kf, scoring="neg_root_mean_squared_error")
print(f"\\n{{model_name}} CV RMSE: {{-cv_scores.mean():.4f}} (+/- {{cv_scores.std():.4f}})")

model.fit(X_train, y_train)
print("Model trained!")
"""
    return code


def generate_prediction_and_submission(
    task_type: str = "binary_classification",
    id_column: str = "Id",
    target_column: str = "target",
    submission_filename: str = "submission.csv",
) -> str:
    """Generates prediction and submission file code."""
    code = f"""
# ============================================================
# 5. PREDICTION & SUBMISSION
# ============================================================
print("Generating predictions...")

if 'test' in dir():
    # Prepare test features (apply same preprocessing)
    test_features = test[X_train.columns] if all(c in test.columns for c in X_train.columns) else test

    predictions = model.predict(test_features)

    submission = pd.DataFrame({{
        "{id_column}": range(len(predictions)),  # Adjust based on test IDs
        "{target_column}": predictions,
    }})
    submission.to_csv("{submission_filename}", index=False)
    print(f"Submission saved to {submission_filename}")
    print(f"Submission shape: {{submission.shape}}")
    print(f"Preview:\\n{{submission.head()}}")
else:
    print("No test set available. Skipping submission generation.")

print("\\n" + "=" * 60)
print("  BASELINE COMPLETE!")
print("=" * 60)
"""
    return code


def generate_full_baseline(
    train_path: str = "train.csv",
    test_path: str | None = "test.csv",
    target_column: str = "target",
    id_column: str | None = "Id",
    task_type: str = "binary_classification",
    model_family: str = "tree_based",
    metric: str = "accuracy",
    drop_columns: list[str] | None = None,
    feature_hints: list[str] | None = None,
) -> str:
    """
    Generates a complete baseline script by combining all templates.

    This is the primary skill function — produces a full, runnable
    Python script ready for a Kaggle competition.
    """
    parts = [
        generate_imports(model_family),
        generate_data_loading(train_path, test_path, target_column, id_column),
        generate_preprocessing(
            drop_columns=drop_columns, target_column=target_column
        ),
        generate_feature_engineering(feature_hints),
        generate_model_training(task_type, model_family, metric),
        generate_prediction_and_submission(
            task_type,
            id_column or "Id",
            target_column,
        ),
    ]
    return "\n".join(parts)
