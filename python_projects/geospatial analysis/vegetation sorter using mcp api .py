import pystac_client
import planetary_computer
import stackstac
import xarray as xr
from dask.diagnostics import ProgressBar
catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace
)
capture_area = [-60.00, -4.00, -59.00, -3.00]
search = catalog.search(
    collections=["sentinel-2-l2a"],
    bbox=capture_area,
    datetime="2023-01-01/2024-03-01",
    query={"eo:cloud_cover": {"lt": 1}})
items = search.item_collection()[0:1]
if len(items) > 0:
    print(f"I found {len(items)} images.")
    print(f"The first image link is: {items[0].assets['B08'].href}")
else:
    print("yo pc washed bro.")
cube_of_data = stackstac.stack(
    items, assets=["B08", "B04", "SCL"], epsg=3857, bounds_latlon=capture_area,
    chunksize=1024, resolution=500,)
scl = cube_of_data.sel(band="SCL")
mask = (scl == 4) | (scl == 5)
cube_of_vegetation = cube_of_data.where(mask)
nir = ((cube_of_vegetation.sel(band="B08") - 1000)/10000)
red = ((cube_of_vegetation.sel(band="B04") - 1000)/10000)
valid_pixels = (nir >= 0) & (red >= 0)
ndvi_cube = ((nir - red) / (nir + red)).where(valid_pixels)
greenest_day = ndvi_cube.max(dim="time")
is_vegetation = (greenest_day > 0.1)
actual_ground_pixels = greenest_day.notnull().sum()
plant_pixels = is_vegetation.sum()
veg_percentage = (plant_pixels / actual_ground_pixels) * 100
total_raw_pixels = is_vegetation.size
print("this might take some time....")
with ProgressBar():
    ground_count = actual_ground_pixels.compute().item()
    plant_count = plant_pixels.compute().item()
if (ground_count > 0):
    final_percentage = ((plant_count/ground_count)
                        * 100)
    print(f"ha well vegetation percentage found it is {final_percentage}%")
    print(f"Max NDVI found: {greenest_day.max().compute().item()}")
else:
    print("ok so yo pc aint washed but u did encounter a cloud or wrong cords")
    print(f"DEBUG: Total pixels in the box: {total_raw_pixels}")
    print(f"DEBUG: Ground pixels found: {ground_count}")
    print(f"DEBUG: Plant pixels found: {plant_count}")
