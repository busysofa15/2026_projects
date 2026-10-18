this is a compressible fluid simulator which uses compressible fluid navier stokes equations and uses ideal gas laws to 
simulate the fluid and uses density clamps and upwind differrencing schemes to ensure that simulator does not explode into nans/inf
note that this is not completely accurate as the current upwind differeencing scheme probably introduces slight changes
->uses ndarray(with rayon feature) for the stencil operations for maximum performance
->it is a completely isolated system by the way
