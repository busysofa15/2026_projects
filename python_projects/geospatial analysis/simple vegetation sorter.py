import numpy as np
from PIL import Image
main_image = Image.open(
    r"c:\Users\ADMIN\Pictures\Screenshots\forest.png").convert("RGB")
pixels = np.array(main_image)[:, :, :3]
red_layer = pixels[:, :, 0]
green_layer = pixels[:, :, 1]
blue_layer = pixels[:, :, 2]
is_plant = (green_layer > red_layer) & (
    green_layer > blue_layer)
plant_count = np.count_nonzero(is_plant)
total_pixels = is_plant.size
plant_cover = (plant_count/total_pixels*100)
mask = Image.fromarray((is_plant * 255).astype(np.uint8))
mask.show()
