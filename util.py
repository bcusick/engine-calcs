import math
import ht
import fluids

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

def float_range(start, end, step):
    while start <= end:
        yield start
        start += step

def C_to_F(C):
    F= C * 9./5. + 32
    return F
#def rho_to_SI(rho):

def fuelDensity(temp, density):
    temp = C_to_F(temp)
    tempArray=np.array([30.00, 40.00, 50.00, 60.00, 70.00, 80.00, 90.00, 100.00, 110.00, 120.00, 130.00, 140.00, 150.00, 160.00, 170.00, 180.00, 190.00, 200.00])
    #VCF is volume correction factor based on ASTM standard for fuel oil
    VCF_array=np.array([1.0128, 1.0084, 1.004, 0.9996, 0.9951, 0.9907, 0.9862, 0.9817, 0.9772, 0.9727, 0.9682, 0.9637, 0.9592, 0.9546, 0.9501, 0.9455, 0.941, 0.9364])
    f = interpolate.interp1d(tempArray, VCF_array, fill_value="extrapolate")
    VCF = f(temp)
    density = VCF * density
    return density

def airDensity(temp):
    temp = C_to_F(temp)
    tempArray=np.array([-40, -20, 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 433, 466,
    500, 600, 750, 1000, 1500])
    densityArray=np.array([9.456, 9.026, 8.633, 8.449, 8.273, 8.104, 7.942, 7.786, 7.636, 7.492, 7.353, 7.219, 7.090, 6.846, 6.617, 6.404, 6.204, 6.016, 5.841, 5.674,
    5.516, 5.367, 5.224, 5.091, 4.964, 4.843, 4.728, 4.616, 4.447, 4.288, 4.135, 3.746, 3.280, 2.717, 2.024])
    f = interpolate.interp1d(tempArray, densityArray, fill_value="extrapolate")
    density = f(temp)
    print (densityArray * 10)
    return density

x=fuelDensity(95, 850)
y=airDensity(95)

print x
print y

'''
graphtest=pd.Series(density, index=temp)
graphtest.plot()
plt.grid(1)
plt.show()
'''
