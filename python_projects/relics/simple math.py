import math
startup = "hello😁"
intro = "here is your desired ratio"
radius = 10
volume_of_sphere = (4/3*math.pi*radius**3)
surface_area_of_sphere = (4*math.pi*radius**2)
ratio = round(volume_of_sphere/surface_area_of_sphere, 1)
side = (volume_of_sphere**(1/3))
extra_information = "also here's the side of a cube with the same volume👌"
surface_area_of_cube = (6*(side)**2)
even_more_info = "also random sidenote i found the cube's surface area as well "
final = (f"{startup}\n{intro}\n{ratio}"
         f"\n{extra_information}\n{side:.2f}\n{even_more_info}\n{surface_area_of_cube:.2f}")
print(final)
