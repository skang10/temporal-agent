import pandas as pd


class TimeSeriesFeaturizer:
    def __init__(
        self,
        windows: list[int] | None = None,
        lags: list[int] | None = None,
    ):
        self.windows: list[int] = windows or [5, 20, 60]
        self.lags: list[int] = lags or [1, 5, 20]

    def align(self, series_dict: dict[str, pd.Series]) -> pd.DataFrame:
        """Align all series to a common daily index using forward-fill only.

        Uses ffill (not bfill) so no future values are introduced.
        """
        if not series_dict:
            return pd.DataFrame()

        all_dates = pd.DatetimeIndex(
            sorted({date for s in series_dict.values() for date in s.index})
        )
        daily_index = pd.date_range(start=all_dates.min(), end=all_dates.max(), freq="D")

        aligned = {
            name: series.reindex(daily_index, method="ffill")
            for name, series in series_dict.items()
        }
        return pd.DataFrame(aligned, index=daily_index)
