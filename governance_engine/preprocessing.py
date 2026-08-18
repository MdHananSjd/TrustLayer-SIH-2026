import pandas as pd


def add_age_group(dataframe: pd.DataFrame) -> pd.DataFrame:
    """
    Add a categorical age_group column for fairness analysis.

    Age buckets:
        18-29
        30-44
        45-59
        60+
    """

    if "age" not in dataframe.columns:
        raise ValueError(
            "Cannot create age_group because 'age' is missing."
        )

    dataframe = dataframe.copy()

    dataframe["age_group"] = pd.cut(
        dataframe["age"],
        bins=[
            17,
            29,
            44,
            59,
            float("inf"),
        ],
        labels=[
            "18-29",
            "30-44",
            "45-59",
            "60+",
        ],
        include_lowest=True,
    )

    return dataframe