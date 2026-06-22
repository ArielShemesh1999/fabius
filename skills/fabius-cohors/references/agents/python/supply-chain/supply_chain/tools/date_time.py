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

"""Tool for getting current date and time"""

from datetime import datetime
from zoneinfo import ZoneInfo  # for handling timezones


def get_current_date_time(time_zone: str = "UTC") -> dict:
    """
    Gets the current date and time in the specified time zone.
    Defaults to UTC if no time zone is provided.

    Args:
        time_zone (str): The time zone to get the date and time for. Defaults to 'UTC'.

    Returns:
        dict: A dictionary containing the current date, time, and time zone.
    """
    try:
        current_time = datetime.now(ZoneInfo(time_zone))
    except Exception:
        # Fallback to UTC if timezone is invalid
        current_time = datetime.now(ZoneInfo("UTC"))
        time_zone = "UTC"

    return {
        "current_date": current_time.strftime("%Y-%m-%d"),
        "current_time": current_time.strftime("%H:%M:%S"),
        "time_zone": time_zone,
    }
