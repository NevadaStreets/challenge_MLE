from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from typing import Tuple, Union, List

# Bundled dataset shipped with the repository, resolved relative to this file so
# it works regardless of the current working directory.
DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "data.csv"


class DelayModel:

    # Top 10 features selected from the XGBoost feature importance analysis in
    # the exploration notebook. The model is trained exclusively on these.
    FEATURES_COLS = [
        "OPERA_Latin American Wings",
        "MES_7",
        "MES_10",
        "OPERA_Grupo LATAM",
        "MES_12",
        "TIPOVUELO_I",
        "MES_4",
        "MES_11",
        "OPERA_Sky Airline",
        "OPERA_Copa Air",
    ]

    TARGET_COL = "delay"
    THRESHOLD_IN_MINUTES = 15

    def __init__(
        self
    ):
        self._model = None  # Model should be saved in this attribute.

    @staticmethod
    def _get_min_diff(row: pd.Series) -> float:
        """Difference in minutes between operated and scheduled times."""
        fecha_o = datetime.strptime(row['Fecha-O'], '%Y-%m-%d %H:%M:%S')
        fecha_i = datetime.strptime(row['Fecha-I'], '%Y-%m-%d %H:%M:%S')
        return ((fecha_o - fecha_i).total_seconds()) / 60

    def preprocess(
        self,
        data: pd.DataFrame,
        target_column: str = None
    ) -> Union[Tuple[pd.DataFrame, pd.DataFrame], pd.DataFrame]:
        """
        Prepare raw data for training or predict.

        Args:
            data (pd.DataFrame): raw data.
            target_column (str, optional): if set, the target is returned.

        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: features and target.
            or
            pd.DataFrame: features.
        """
        features = pd.concat(
            [
                pd.get_dummies(data['OPERA'], prefix='OPERA'),
                pd.get_dummies(data['TIPOVUELO'], prefix='TIPOVUELO'),
                pd.get_dummies(data['MES'], prefix='MES'),
            ],
            axis=1
        )

        # Guarantee the exact set of columns the model expects, filling any
        # category absent from the incoming data with zeros.
        features = features.reindex(columns=self.FEATURES_COLS, fill_value=0)

        if target_column is not None:
            min_diff = data.apply(self._get_min_diff, axis=1)
            target = np.where(min_diff > self.THRESHOLD_IN_MINUTES, 1, 0)
            target = pd.DataFrame(target, columns=[target_column])
            return features, target

        return features

    def fit(
        self,
        features: pd.DataFrame,
        target: pd.DataFrame
    ) -> None:
        """
        Fit model with preprocessed data.

        Args:
            features (pd.DataFrame): preprocessed data.
            target (pd.DataFrame): target.
        """
        target_series = target[self.TARGET_COL] if isinstance(target, pd.DataFrame) else target

        # Balance the classes: delayed flights are the minority (~1:4.4 ratio).
        n_y0 = int((target_series == 0).sum())
        n_y1 = int((target_series == 1).sum())
        total = n_y0 + n_y1
        class_weight = {1: n_y0 / total, 0: n_y1 / total}

        self._model = LogisticRegression(class_weight=class_weight)
        self._model.fit(features, target_series)

    def predict(
        self,
        features: pd.DataFrame
    ) -> List[int]:
        """
        Predict delays for new flights.

        Args:
            features (pd.DataFrame): preprocessed data.

        Returns:
            (List[int]): predicted targets.
        """
        if self._model is None:
            self._fit_from_bundled_data()

        predictions = self._model.predict(features)
        return [int(prediction) for prediction in predictions]

    def _fit_from_bundled_data(self) -> None:
        """
        Train the model on the dataset bundled with the repository.

        This makes the model usable for prediction even when ``fit`` was not
        explicitly called beforehand (e.g. a freshly instantiated model used
        only for serving), avoiding the need to ship a version-specific
        serialized artifact.
        """
        if not DEFAULT_DATA_PATH.exists():
            raise RuntimeError(
                "Model has not been fitted and the bundled training dataset was "
                f"not found at '{DEFAULT_DATA_PATH}'. Call `fit` before `predict`."
            )

        data = pd.read_csv(filepath_or_buffer=DEFAULT_DATA_PATH, low_memory=False)
        features, target = self.preprocess(data=data, target_column=self.TARGET_COL)
        self.fit(features=features, target=target)
