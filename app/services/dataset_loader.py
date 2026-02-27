import pandas as pd
import os
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatasetLoader:
    _instance = None
    _df = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatasetLoader, cls).__new__(cls)
        return cls._instance

    def load_dataset(self) -> pd.DataFrame:
        """
        Loads the Titanic dataset into memory as a pandas DataFrame.
        Ensures the dataset is only loaded once (singleton pattern).
        """
        if self._df is not None:
            return self._df

        try:
            # We use an absolute path assuming the app runs from the project root
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            file_path = os.path.join(base_dir, settings.DATASET_PATH)
            
            logger.info(f"Loading Titanic dataset from {file_path}")
            df = pd.read_csv(file_path)
            
            # Basic validation
            expected_columns = [
                "PassengerId", "Survived", "Pclass", "Name", "Sex", "Age",
                "SibSp", "Parch", "Ticket", "Fare", "Cabin", "Embarked"
            ]
            missing_cols = [col for col in expected_columns if col not in df.columns]
            if missing_cols:
                raise ValueError(f"Dataset is missing required columns: {missing_cols}")

            # Safe handling of missing values for standard columns
            # Age: fill with median
            if "Age" in df.columns:
                df["Age"] = df["Age"].fillna(df["Age"].median())
            
            # Embarked: fill with mode
            if "Embarked" in df.columns:
                df["Embarked"] = df["Embarked"].fillna(df["Embarked"].mode()[0])

            # Cabin has many missing values, fill with 'Unknown'
            if "Cabin" in df.columns:
                df["Cabin"] = df["Cabin"].fillna("Unknown")

            # Fare missing val
            if "Fare" in df.columns:
                df["Fare"] = df["Fare"].fillna(df["Fare"].median())

            self._df = df
            logger.info(f"Successfully loaded dataset with shape {df.shape}")
            return self._df

        except Exception as e:
            logger.error(f"Error loading Titanic dataset: {e}")
            raise RuntimeError(f"Failed to load dataset: {e}")

# Global instance
dataset_loader = DatasetLoader()
