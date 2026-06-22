"""Earth Engine agent tools."""

import asyncio
import json
from typing import Any

import ee
import numpy as np
from google.api_core import retry_async


def get_angle(image1: ee.Image, image2: ee.Image) -> ee.Image:
    """Calculates the angle between two Earth Engine images.

    This function treats each pixel as a vector and computes the angle between
    the vectors from `image1` and `image2` using the dot product formula:
    angle = acos((image1 * image2) / (|image1| * |image2|)).
    Assuming the images are already normalized or the magnitude is handled
    elsewhere, this implementation simplifies to acos(dot_product).

    Args:
        image1: The first ee.Image.
        image2: The second ee.Image.

    Returns:
        An ee.Image containing the angle in radians.
    """
    return (
        image1.multiply(image2).reduce(ee.Reducer.sum()).acos().rename("angle")
    )


def get_change_year_image(threshold: float):
    """Generates an image showing the year of significant change.

    This function uses the GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL dataset to detect
    significant changes between consecutive years from 2018 to 2025. It calculates
    the angle between the embeddings of each year and the previous year. Pixels
    where this angle exceeds pi/4 are considered to have undergone a significant
    change. The output is a multi-band image where each band corresponds to a
    year, and the pixel value is the year if a significant change was detected
    in that year compared to the previous one.

    Args:
        threshold: Angular threshold in radians above which change is assumed.

    Returns:
        An ee.Image with bands for each year from 2018 to 2025, indicating
        the year of change.
    """
    embeddings = ee.ImageCollection("GOOGLE/SATELLITE_EMBEDDING/V1/ANNUAL")
    years = ee.List.sequence(2018, 2025)

    def annual_changes(year: int) -> ee.Image:
        cur = embeddings.filter(
            ee.Filter.calendarRange(year, year, "year")
        ).mosaic()
        prev_year = ee.Number(year).subtract(1)
        prev = embeddings.filter(
            ee.Filter.calendarRange(prev_year, prev_year, "year")
        ).mosaic()
        return (
            get_angle(prev, cur)
            .gt(threshold)
            .multiply(ee.Image.constant(year))
            .selfMask()
            .rename(ee.Number(year).format("%d"))
        )

    changes = (
        ee.ImageCollection.fromImages(years.map(annual_changes))
        .toBands()
        .rename(years.map(lambda s: ee.Number(s).format("%d")))
    )
    return changes


def get_annual_change_dictionary(geometry: ee.Geometry) -> ee.Dictionary:
    """Gets a dictionary of annual change areas within a given geometry.

    This function calculates the total area (in square meters) for each year
    (from 2018 to 2024) where significant land cover change was detected within
    the specified Earth Engine geometry.

    Args:
        geometry: The ee.Geometry in which to compute the change areas.

    Returns:
        An ee.Dictionary where keys are years (as strings) and values are the
        total area in square meters for which change was detected in that year.
    """
    threshold = np.pi / 4  # Arbitrary.
    scale = 10
    change_year_image = get_change_year_image(threshold)
    change_year_areas = change_year_image.gt(0).multiply(ee.Image.pixelArea())
    return change_year_areas.reduceRegion(
        reducer=ee.Reducer.sum(), geometry=geometry, scale=scale, maxPixels=1e13
    )


@retry_async.AsyncRetry(deadline=60)
async def get_2017_2025_annual_changes(
    geojson: str,
) -> dict[str, Any]:
    """Gets a dictionary of annual change areas within a given GeoJSON geometry.

    This function calculates the total area (in square meters) for each year
    (from 2018 to 2025) where significant land cover change was detected within
    the specified GeoJSON geometry.

    Args:
        geojson (str): A JSON string representing a GeoJSON geometry.

    Returns:
        A dictionary where keys are years (as strings) and values are the
        total area in square meters for which change was detected in that year.
    """
    region = ee.Geometry(json.loads(geojson))
    return await asyncio.to_thread(get_annual_change_dictionary(region).getInfo)
