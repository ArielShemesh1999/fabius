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

"""ToolKit for weather analysis"""

import io
import logging

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns
from google import genai
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from ..config import config
from . import prompts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalyseWeatherToolkit:
    """
    A class to handle weather forecast data using Open-Meteo API.

    This class connects to the Open-Meteo API to fetch historical weather data for a specific
    location/address & date.
    """

    def __init__(
        self,
        project_id: str,
        location: str,
        geo_maps_api_key: str | None = None,
        **kwargs,
    ):
        """
        Initializes the AnalyseWeatherToolkit.

        Args:
            project_id (str): Your Google Cloud project ID.
            location (str): Your Google Cloud location.
            geo_maps_api_key (str): Your Google Maps API Key.
        """
        self.project_id = project_id
        self.location = location

        # Geo Maps API
        self.geo_maps_api_key = geo_maps_api_key
        self.geo_maps_geocoding_url = (
            "https://maps.googleapis.com/maps/api/geocode/json"
        )
        # Open Meteo API
        self.open_meteo_url = "https://archive-api.open-meteo.com/v1/archive"
        self.open_meteo_forecast_url = "https://api.open-meteo.com/v1/forecast"
        self.open_meteo_geocoding_url = (
            "https://geocoding-api.open-meteo.com/v1/search"
        )

        self.model_name = kwargs.get("model_name", config.model_name)
        self.gen_client = genai.Client(
            vertexai=True,
            project=project_id,
            location=location,
            http_options=types.HttpOptions(
                api_version="v1",
            ),
        )
        # define gen ai model config
        self.safety_settings = self.load_safety_config()
        self.generation_config = types.GenerateContentConfig(
            system_instruction=prompts.WEATHER_CHARTS_SUMMARIZATION_SYSTEM_INSTRUCTIONS,
            safety_settings=self.safety_settings,
            temperature=kwargs.get("temperature", config.temperature),
            top_p=kwargs.get("top_p", config.top_p),
            response_mime_type="text/plain",
        )

    def load_safety_config(self) -> list[types.SafetySetting]:
        """Set Safety Settings for a Gemini instance using genai types."""
        return [
            # RELAX THESE (To prevent blocking legitimate reports on severe weather and supply chain disruptions)
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            # KEEP THESE STRICT (Standard guardrails to block non-weather policy violations)
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                threshold=types.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            ),
        ]

    def _get_open_meteo_forecast(
        self,
        latitude: float,
        longitude: float,
        init_time: str,
        end_time: str | None = None,
    ) -> pd.DataFrame:
        """
        Fetches historical weather data from Open-Meteo for the given location and date range.

        Args:
            latitude (float): Latitude of the location.
            longitude (float): Longitude of the location.
            init_time (str): The start time (ISO 8601 format). Used to determine the target date.
            end_time (str, optional): The end time (ISO 8601 format). If None, defaults to init_time.

        Returns:
            pd.DataFrame: A DataFrame matching the expected schema.
        """
        try:
            target_time = pd.to_datetime(init_time)
            start_date = target_time.strftime("%Y-%m-%d")

            if end_time:
                target_end = pd.to_datetime(end_time)
                end_date = target_end.strftime("%Y-%m-%d")
            else:
                end_date = start_date  # Get data for the specific day

            # Determine which API to use based on date
            # If end_date is today or in the future, use Forecast API
            # Forecast API also supports past data (up to ~92 days), so it handles mixed ranges well.
            current_date = pd.Timestamp.now().normalize()
            target_end_dt = pd.to_datetime(end_date)

            if target_end_dt >= current_date:
                url = self.open_meteo_forecast_url
                logger.info(
                    f"Using Open-Meteo Forecast API for range ending {end_date} (Future/Mixed)"
                )
            else:
                url = self.open_meteo_url
                logger.info(
                    f"Using Open-Meteo Archive API for range ending {end_date} (Historical)"
                )

            params = {
                "latitude": latitude,
                "longitude": longitude,
                "start_date": start_date,
                "end_date": end_date,
                "hourly": "temperature_2m,precipitation,pressure_msl,wind_speed_10m,wind_direction_10m,relative_humidity_2m",
                "timezone": "UTC",
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            hourly = data.get("hourly", {})
            if not hourly:
                logger.warning("Open-Meteo returned no hourly data.")
                return pd.DataFrame()

            df = pd.DataFrame(hourly)

            # Rename columns to match BQ schema partial matches
            df = df.rename(
                columns={
                    "time": "time",
                    "temperature_2m": "2m_temperature",
                    "pressure_msl": "mean_sea_level_pressure",
                }
            )

            # Convert time to datetime
            df["time"] = pd.to_datetime(df["time"])

            # Create init_time column (simulate it as being created at the start of the day)
            # This ensures it passes the downstream filter which expects init_time.hour == 0
            # Fix: derive init_time from the actual time column so it's correct for each row in a range
            df["init_time"] = df["time"].dt.normalize()

            # Calculate u and v components of wind
            # Open-Meteo direction is degrees (0=North, 90=East, etc.)
            wd_rad = np.deg2rad(df["wind_direction_10m"])
            ws = df["wind_speed_10m"]

            # Standard conversion: u = -wind_abs * sin(theta), v = -wind_abs * cos(theta) for wind *from* direction
            df["10m_u_component_of_wind"] = -ws * np.sin(wd_rad)
            df["10m_v_component_of_wind"] = -ws * np.cos(wd_rad)

            # Use hourly precipitation as total_precipitation_6hr approximation/scalar
            df["total_precipitation_6hr"] = df["precipitation"]

            # Use relative_humidity_2m as 100_specific_humidity approximation
            df["100_specific_humidity"] = df["relative_humidity_2m"] / 100.0

            # Select and order columns
            required_cols = [
                "init_time",
                "time",
                "2m_temperature",
                "total_precipitation_6hr",
                "mean_sea_level_pressure",
                "10m_u_component_of_wind",
                "10m_v_component_of_wind",
                "100_specific_humidity",
            ]

            # Fill missing cols with 0 if any calculation failed
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 0.0

            return df[required_cols]

        except (requests.RequestException, KeyError, ValueError) as e:
            logger.error(f"Failed to fetch from Open-Meteo: {e}")
            return pd.DataFrame()

    def get_weather_forecast_dataframe(
        self,
        tool_context: ToolContext,
        init_time: str,
        end_time: str | None = None,
    ):
        """Executes a Open-Meteo API call to get weather forecast data.

        This tool uses the latitude and longitude from the tool_context to query
        weather data from Open-Meteo, processes it into a pandas DataFrame, and
        stores it in the tool_context.

        Args:
            init_time (str): The start time for filtering (ISO 8601 format).
            end_time (str, Optional): The end time for filtering (ISO 8601 format).
            tool_context (ToolContext): The context from a previous tool call,
                                        containing latitude and longitude.

        Returns:
            dict: A dictionary containing the status and a summary of the DataFrame,
                or an error message.
        """
        if (
            "latitude" not in tool_context.state
            or "longitude" not in tool_context.state
        ):
            return {
                "status": "error",
                "error_message": "Latitude or longitude not found in context. "
                "Please get coordinates from an address first.",
            }

        latitude = tool_context.state["latitude"]
        longitude = tool_context.state["longitude"]

        try:
            df = self._get_open_meteo_forecast(
                latitude, longitude, init_time, end_time
            )
            if df.empty:
                return {
                    "status": "error",
                    "error_message": "Weather API returned no data.",
                }

            # Add plot helper columns
            df["month_day_time"] = df["time"].dt.strftime("%b-%d %H:%M:%S")
            df["year"] = df["time"].dt.year

            # Convert datetime objects to strings for JSON serialization
            df_serializable = df.copy()
            df_serializable["time"] = df_serializable["time"].astype(str)
            df_serializable["init_time"] = df_serializable["init_time"].astype(
                str
            )
            tool_context.state["dataframe"] = df_serializable.to_dict(
                orient="records"
            )

            report = (
                f"Successfully loaded DataFrame from Open-Meteo API for location "
                f"(lat: {latitude}, lon: {longitude}). "
                f"It has {df.shape[0]} rows. "
            )
            logger.info(f"Fetch weather data from API: {report}")
            return {"status": "success", "report": report}
        except (requests.RequestException, ValueError, KeyError) as e:
            logger.error(f"Weather API failed: {e}")
            return {
                "status": "error",
                "error_message": f"Weather API failed: {e}",
            }

    def filter_weather_dataframe_by_time(
        self,
        tool_context: ToolContext,
        init_time: str,
        end_time: str | None = None,
    ):
        """Filters the loaded DataFrame for records within a time range.
            Args:
                init_time (str): The start time for filtering (ISO 8601 format, e.g.,
                    '2023-01-01T12:00:00').
                end_time (str, optional): The end time for filtering (ISO 8601 format).
        Returns:
            dict: A dictionary containing the status and a summary of the filtered
                    DataFrame, or an error message.
        """
        if "dataframe" not in tool_context.state:
            return {
                "status": "error",
                "error_message": "No DataFrame in context. Please load a DataFrame first.",
            }

        try:
            df_data = tool_context.state.get("dataframe")
            if not df_data:
                return {
                    "status": "error",
                    "error_message": "DataFrame is empty or not found in context.",
                }

            df = pd.DataFrame(df_data)
            # Re-convert columns to datetime as this can be lost in serialization
            df["time"] = pd.to_datetime(df["time"])
            df["init_time"] = pd.to_datetime(df["init_time"])

            target_time = pd.to_datetime(init_time)
            target_month = target_time.month
            target_day = target_time.day

            # Filter the DataFrame based on time range
            start_dt = pd.to_datetime(init_time)
            end_dt = (
                pd.to_datetime(end_time)
                if end_time
                else start_dt + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
            )

            if end_time:
                # Range filter. We filter by `init_time` being in the range?
                # Ensure start_dt and end_dt are timezone-naive if df['init_time'] is naive (it usually is from Open-Meteo)
                # or normalize both.
                start_dt = start_dt.replace(tzinfo=None)
                end_dt = end_dt.replace(tzinfo=None)
                mask = (df["init_time"] >= start_dt) & (
                    df["init_time"] <= end_dt
                )
                if "time" in df.columns:
                    # Also optionally sort by time
                    pass
            else:
                # strict single day/hour filter as before?
                # (df['init_time'].dt.month == target_month) & ...
                mask = (
                    (df["init_time"].dt.month == target_month)
                    & (df["init_time"].dt.day == target_day)
                    & (df["init_time"].dt.hour == 0)
                )

            filtered_df = df[mask].copy()
            # Convert datetime objects to strings for JSON serialization
            filtered_df_serializable = filtered_df.copy()
            filtered_df_serializable["time"] = filtered_df_serializable[
                "time"
            ].astype(str)
            filtered_df_serializable["init_time"] = filtered_df_serializable[
                "init_time"
            ].astype(str)
            tool_context.state["dataframe"] = filtered_df_serializable.to_dict(
                orient="records"
            )

            report = (
                f"Filtered DataFrame. It now has {filtered_df.shape[0]} rows, "
                f"down from an original {df.shape[0]} rows."
            )
            logger.info(f"Filter weather data from BigQuery: {report}")
            return {"status": "success", "report": report}
        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Failed to filter data: {e}")
            return {
                "status": "error",
                "error_message": f"Failed to filter data: {e}",
            }

    async def generate_weather_info_charts(self, tool_context: ToolContext):
        """Generates charts from the DataFrame in context and saves them.

        Args:
            tool_context (ToolContext): The context from a previous tool call,
                                    containing the DataFrame to plot.

        Returns:
            A tuple containing a result dictionary and a ToolContext object with the
            paths to the generated charts.
        """
        if "dataframe" not in tool_context.state:
            return {
                "status": "error",
                "error_message": "No DataFrame in context. Please load and filter a DataFrame first.",
            }

        try:
            df_data = tool_context.state.get("dataframe")
            if not df_data:
                return {
                    "status": "error",
                    "error_message": "DataFrame is empty or not found in context.",
                }

            df = pd.DataFrame(df_data)

            # Defensive check: Ensure 'time' column exists
            if "time" not in df.columns:
                return {
                    "status": "error",
                    "error_message": "Crucial column 'time' is missing from the DataFrame. Cannot generate charts.",
                }

            # Ensure time is datetime for plotting and filtering
            df["time"] = pd.to_datetime(df["time"])

            if df.empty:
                return {
                    "status": "success",
                    "report": "DataFrame is empty, no charts generated.",
                }

            # Limit data to max 7 days to avoid clutter
            min_time = df["time"].min()
            cutoff_time = min_time + pd.Timedelta(days=7)

            original_len = len(df)
            df = df[df["time"] < cutoff_time]
            if len(df) < original_len:
                logger.info(
                    f"Capped chart data to 7 days. Reduced from {original_len} to {len(df)} rows."
                )

            filenames = []

            plot_variables = {
                "2m_temperature": "2m Temperature",
                "total_precipitation_6hr": "6-Hour Total Precipitation",
                "mean_sea_level_pressure": "Mean Sea Level Pressure",
                "10m_u_component_of_wind": "10m u component of wind",
                "10m_v_component_of_wind": "10m v component of wind",
                "100_specific_humidity": "100 Specific Humidity",
            }

            for col, title in plot_variables.items():
                plt.figure(figsize=(12, 6))
                sns.lineplot(data=df, x="time", y=col, hue="year", marker="o")
                plt.title(title)
                plt.ylabel(title)
                plt.xlabel("Time")

                # Format x-axis to avoid clutter
                ax = plt.gca()
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(
                    mdates.DateFormatter("%b-%d %H:%M")
                )

                plt.xticks(rotation=45)
                plt.tight_layout()

                buffer = io.BytesIO()
                plt.savefig(buffer, format="png")
                buffer.seek(0)
                image_byte_data = buffer.read()

                filename = f"{col}_plot.png"
                await tool_context.save_artifact(
                    filename,
                    types.Part.from_bytes(
                        data=image_byte_data, mime_type="image/png"
                    ),
                )
                filenames.append(filename)
                plt.close()
            tool_context.state["chart_filenames"] = filenames

            report = f"Successfully generated and saved {len(filenames)} charts as artifacts: {', '.join(filenames)}"
            logger.info(f"Generate weather info charts: {report}")
            return {"status": "success", "report": report}
        except (OSError, ValueError, KeyError) as e:
            logger.error(f"Failed to generate charts: {e}")
            return {
                "status": "error",
                "error_message": f"Failed to generate charts: {e}",
            }

    async def summarize_weather_from_plots(self, tool_context: ToolContext):
        """Generates a weather summary by analyzing saved chart images.

        Args:
            tool_context (ToolContext): The context from a previous tool call,
                                    containing the paths to the chart images.

        Returns:
            list: A list of Part objects, each containing an image to be
                displayed in the UI, or a dictionary with an error message.
        """
        if "chart_filenames" not in tool_context.state:
            return {
                "status": "error",
                "error_message": "No chart filenames in context. Please generate charts first.",
            }

        try:
            filenames = tool_context.state.get("chart_filenames", [])
            if not filenames:
                return {
                    "status": "success",
                    "summary": "No charts were provided to generate a summary.",
                }

            # Load each artifact by its filename
            image_parts = []
            for filename in filenames:
                artifact = await tool_context.load_artifact(filename)
                # Ensure compatibility by re-wrapping the Part object
                # The artifact might be from a different SDK version or context
                if hasattr(artifact, "inline_data") and artifact.inline_data:
                    # It's likely a protobuf or compatible object
                    blob = artifact.inline_data
                    image_parts.append(
                        types.Part.from_bytes(
                            data=blob.data, mime_type=blob.mime_type
                        )
                    )
                elif isinstance(artifact, bytes):
                    image_parts.append(
                        types.Part.from_bytes(
                            data=artifact, mime_type="image/png"
                        )
                    )
                elif isinstance(artifact, types.Part):  # Already compatible
                    image_parts.append(artifact)
                else:
                    image_parts.append(artifact)

            # Construct a multi-part prompt. The first part is the text instruction,
            # followed by the image parts for analysis.
            prompt_parts = [prompts.WEATHER_CHARTS_SUMMARIZATION_PROMPT]
            prompt_parts.extend(image_parts)

            response = self.gen_client.models.generate_content(
                model=self.model_name,
                contents=prompt_parts,
                config=self.generation_config,
            )
            logger.info(f"Summarize weather from plots: {response.text}")
            return {"status": "success", "summary": response.text}
        except (OSError, ValueError) as e:
            logger.error(f"Failed to generate summary: {e}")
            return {
                "status": "error",
                "error_message": f"Failed to generate summary: {e}",
            }
        except Exception as e:
            logger.error(f"Unexpected error in summary generation: {e}")
            return {
                "status": "error",
                "error_message": f"Unexpected error in summary generation: {e}",
            }

    def get_lat_long_from_address(
        self, tool_context: ToolContext, address: str
    ):
        """Gets latitude and longitude for a given address.

        Prioritizes Google Maps Geocoding API if a key is available.
        Falls back to Open-Meteo Geocoding API if key is missing or request fails.

        Args:
            address (str): The street address or location name.

        Returns:
            dict: A dictionary containing the status, latitude, and longitude,
                or an error message.
        """

        # 1. Try Google Maps Geocoding API
        if self.geo_maps_api_key:
            try:
                base_url = self.geo_maps_geocoding_url
                params = {"address": address, "key": self.geo_maps_api_key}
                response = requests.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()

                if data["status"] == "OK":
                    location = data["results"][0]["geometry"]["location"]
                    lat = location["lat"]
                    lng = location["lng"]

                    tool_context.state["latitude"] = lat
                    tool_context.state["longitude"] = lng

                    report = f"Successfully found coordinates for {address} using Google Maps: Latitude={lat}, Longitude={lng}"
                    logger.info(f"Get lat long (Google Maps): {report}")
                    return {
                        "status": "success",
                        "latitude": lat,
                        "longitude": lng,
                        "report": report,
                    }
                else:
                    logger.warning(
                        f"Google Maps API error: {data.get('error_message', data['status'])}"
                    )
            except requests.RequestException as e:
                logger.warning(
                    f"Google Maps API failed: {e}. Attempting fallback."
                )

        # 2. Fallback to Open-Meteo Geocoding API
        logger.info("Using Open-Meteo Geocoding API as fallback.")
        base_url = self.open_meteo_geocoding_url
        params = {
            "name": address,
            "count": 1,
            "language": "en",
            "format": "json",
        }
        try:
            # Add User-Agent header as polite request for Open-Meteo
            headers = {"User-Agent": "SupplyChainAgent/1.0"}
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            if data.get("results"):
                location = data["results"][0]
                lat = location["latitude"]
                lng = location["longitude"]

                tool_context.state["latitude"] = lat
                tool_context.state["longitude"] = lng

                report = f"Successfully found coordinates for {address} using Open-Meteo: Latitude={lat}, Longitude={lng}"
                logger.info(f"Get lat long (Open-Meteo): {report}")
                return {
                    "status": "success",
                    "latitude": lat,
                    "longitude": lng,
                    "report": report,
                }
            else:
                logger.error(
                    f"Geocoding API error: Location not found for {address}"
                )
                return {
                    "status": "error",
                    "error_message": f"Location not found for {address}",
                }
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request failed: {e}")
            return {
                "status": "error",
                "error_message": f"HTTP Request failed: {e}",
            }

    def get_weather_next_forecast_toolkit(
        self,
    ):
        """Get weather next forecast toolkit"""

        return [
            self.get_weather_forecast_dataframe,
            self.filter_weather_dataframe_by_time,
            self.get_lat_long_from_address,
            self.generate_weather_info_charts,
            self.summarize_weather_from_plots,
        ]


WEATHER_REPORT_TOOLKIT = AnalyseWeatherToolkit(
    project_id=config.project_id,
    location=config.location,
    geo_maps_api_key=config.geo_maps_api_key,
    model_name=config.model_name,
    temperature=config.temperature,
    top_p=config.top_p,
).get_weather_next_forecast_toolkit()
