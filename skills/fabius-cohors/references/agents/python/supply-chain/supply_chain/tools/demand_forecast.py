# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tool for demand forecasting"""

import json
import logging
from datetime import datetime

import google.api_core.exceptions
import google.auth.exceptions
import pandas as pd
from google.cloud import bigquery
from statsmodels.tsa.api import ExponentialSmoothing

from ..config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    bigquery_client = bigquery.Client(
        project=config.project_id
    )  # Initialize client once
except google.auth.exceptions.DefaultCredentialsError as e:
    logger.error(f"Error initializing BigQuery client: {e}")
    bigquery_client = None
except google.api_core.exceptions.GoogleAPICallError as e:
    logger.error(f"BigQuery API error initializing client: {e}")
    bigquery_client = None

MIN_HISTORY_DAYS = 14  # 2 weeks


class DemandForecast:
    """
    A class to handle demand forecasting using data from BigQuery.

    This class connects to a BigQuery table, fetches historical data,
    and uses a Triple Exponential Smoothing model to generate forecasts.
    """

    def __init__(
        self, project_id: str, dataset_id: str, table_id: str, **kwargs
    ):
        """
        Initializes the DemandForecaster.

        Args:
            project_id (str): Your Google Cloud project ID.
            dataset_id (str): Your BQ dataset ID.
            table_id (str): Your BQ table ID.
        """
        self.project_id = project_id
        self.table_id = f"{project_id}.{dataset_id}.{table_id}"

    def forecast(
        self,
        period: int,
        state: str | None = None,
        region: str | None = None,
        power_supplier: str | None = None,
        history_days: int | None = 90,
    ) -> str:
        """
        Generates a demand forecast based on the provided filters.

        Args:
            period (int): The number of future days to forecast.
            state (Optional[str]): A state to filter by.
            region (Optional[str]): A region to filter by.
            power_supplier (Optional[str]): A power supplier to filter by.
            history_days (int): Number of most recent days of data to use.

        Returns:
            str: A JSON string containing the detailed forecast.
        """
        # 1. Dynamically build the query based on optional filters
        logger.info("Building dynamic BigQuery query...")
        where_clauses = []
        params = [
            bigquery.ScalarQueryParameter("history_days", "INT64", history_days)
        ]

        if state:
            where_clauses.append("state = @state")
            params.append(
                bigquery.ScalarQueryParameter("state", "STRING", state)
            )
        if region:
            where_clauses.append("region = @region")
            params.append(
                bigquery.ScalarQueryParameter("region", "STRING", region)
            )
        if power_supplier:
            where_clauses.append("power_supplier = @power_supplier")
            params.append(
                bigquery.ScalarQueryParameter(
                    "power_supplier", "STRING", power_supplier
                )
            )

        where_clauses.append("date <= @current_date")
        current_date = str(datetime.now().strftime("%Y-%m-%d"))
        params.append(
            bigquery.ScalarQueryParameter("current_date", "DATE", current_date)
        )

        where_sql = (
            f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
        )

        query = f"""
            SELECT
                date,
                SUM(consumption_mega_units) as consumption_mega_units
            FROM
                `{self.table_id}`
            {where_sql}
            GROUP BY date
            ORDER BY date DESC
            LIMIT @history_days
        """
        logger.info(f"SQL query: {query}")

        # 2. Execute the query
        logger.info(f"Fetching {history_days} most recent data points...")
        job_config = bigquery.QueryJobConfig(query_parameters=params)
        try:
            df = bigquery_client.query(
                query, job_config=job_config
            ).to_dataframe()
        except google.api_core.exceptions.GoogleAPICallError as e:
            raise ConnectionError(
                f"Failed to query BigQuery. Error: {e}"
            ) from e

        if len(df) < MIN_HISTORY_DAYS:
            raise ValueError(
                f"Insufficient data for forecast. Need at least {MIN_HISTORY_DAYS} days, but found {len(df)}."
            )

        # 3. Prepare the time-series and fit the model
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        time_series = pd.Series(
            df["consumption_mega_units"].values, index=df["date"]
        )

        logger.info("Fitting Holt-Winters model...")
        model = ExponentialSmoothing(
            time_series, trend="add", seasonal="add", seasonal_periods=7
        ).fit()

        # 4. Generate forecast and format output
        forecast_values = model.forecast(steps=period)
        last_date = time_series.index.max()
        forecast_dates = pd.date_range(
            start=last_date + pd.Timedelta(days=1), periods=period, freq="D"
        )
        forecast_list = [
            {
                "date": date.strftime("%Y-%m-%d"),
                "forecasted_consumption_mega_units": round(value, 2),
            }
            for date, value in zip(forecast_dates, forecast_values, strict=True)
        ]

        scope = {
            "state": state,
            "region": region,
            "power_supplier": power_supplier,
        }
        output_json = {
            "forecast_parameters": {
                "scope": {k: v for k, v in scope.items() if v is not None}
                or "National",
                "forecast_days": period,
                "method": "Triple Exponential Smoothing (Holt-Winters)",
                "historical_days_used": len(time_series),
                "based_on_last_date": last_date.strftime("%Y-%m-%d"),
            },
            "demand_forecast": forecast_list,
        }

        return json.dumps(output_json, indent=2)


def get_demand_forecast(
    period: int,
    state: str | None = None,
    region: str | None = None,
    power_supplier: str | None = None,
    history_days: int | None = 180,
) -> str:
    """
    Forecasts demand using Triple Exponential Smoothing.

    This tool is fully flexible. It can forecast for a specific state, region,
    supplier, any combination of these, or perform a national forecast if no
    filters are provided.

    Args:
        period (int): The number of future days to forecast.
        state (Optional[str]): A state to filter by.
        region (Optional[str]): A region to filter by.
        power_supplier (Optional[str]): A power supplier to filter by.
        history_days (int): Number of most recent days of data to use. Defaults to 180.

    Returns:
        str: The report JSON containing the detailed forecast.
    """
    try:
        forecaster = DemandForecast(
            project_id=config.project_id,
            dataset_id=config.dataset_id,
            table_id=config.table_id,
        )
        return forecaster.forecast(
            period=period,
            state=state,
            region=region,
            power_supplier=power_supplier,
            history_days=history_days,
        )
    except (ValueError, ConnectionError) as e:
        return json.dumps({"error": str(e)}, indent=2)
    except google.api_core.exceptions.GoogleAPICallError as e:
        return json.dumps({"error": f"BigQuery API error: {e}"}, indent=2)
