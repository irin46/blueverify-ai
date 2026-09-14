import numpy as np
import rasterio
import requests
from pystac_client import Client
import planetary_computer


def calculate_ndvi(latitude: float, longitude: float):

    catalog = Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace
    )

    # Small area around submitted coordinates
    bbox = [
        longitude - 0.01,
        latitude - 0.01,
        longitude + 0.01,
        latitude + 0.01
    ]

    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        query={"eo:cloud_cover": {"lt": 20}},
        max_items=1
    )

    items = list(search.items())

    if not items:
        return {
            "ndvi": None,
            "ndvi_status": "No imagery",
            "ndvi_explanation": "No suitable Sentinel-2 image was found."
        }

    item = items[0]

    red_url = item.assets["B04"].href
    nir_url = item.assets["B08"].href

    red_response = requests.get(red_url)
    nir_response = requests.get(nir_url)

    red_response.raise_for_status()
    nir_response.raise_for_status()

    with rasterio.MemoryFile(red_response.content) as red_file:
        with red_file.open() as red_src:
            red = red_src.read(1)

    with rasterio.MemoryFile(nir_response.content) as nir_file:
        with nir_file.open() as nir_src:
            nir = nir_src.read(1)

    red = red.astype(float)
    nir = nir.astype(float)

    denominator = nir + red

    ndvi_values = np.divide(
        nir - red,
        denominator,
        out=np.zeros_like(nir),
        where=denominator != 0
    )

    ndvi = float(np.nanmean(ndvi_values))

    if ndvi >= 0.5:
        status = "Healthy vegetation"
    elif ndvi >= 0.2:
        status = "Moderate vegetation"
    else:
        status = "Low vegetation"

    return {
        "ndvi": round(ndvi, 3),
        "ndvi_status": status,
        "ndvi_explanation":
            f"Sentinel-2 imagery produced an average NDVI of {ndvi:.3f}."
    }