import math
import ht
import fluids
# import thermo

import variables as var

from fluids.units import *
from thermo.chemical import Mixture

import intercoolerSizing as cooler
import variables as var

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

import time

#get air components and pressure at given elevation
atm = fluids.ATMOSPHERE_NRLMSISE00(Z=100) #z is meters
Patm = atm.P
# print (atm.P)

# atm = ATMOSPHERE_NRLMSISE00(Z=1E3*u.m, latitude=45*u.degrees, longitude=45*u.degrees, day=150*u.day)
# print (atm.rho, atm.O2_density)

N2 = atm.zs[0]
O2 = atm.zs[1]
Ar = atm.zs[2]

Q = 800 * u.ft**3/u.minute# CFM
# Q /=2
EGT = 500+273 #->K

ex_dia = 3 * u.inch
A = (math.pi*(ex_dia/2)**2)
T = 00+273
L = 10*u.ft
# print (Q, EGT)

#create air mixture so I can get some properties I need
air = Mixture(['nitrogen', 'oxygen', 'argon'], Vfgs=[N2, O2, Ar], T=EGT, P=Patm)
# k = air.isentropic_exponent
rho = air.rho*u.kg/u.m**3
mu = air.mu * 1000 *u.cP
# print(rho, mu)
V = Q/(math.pi/4*ex_dia**2)
Re = Reynolds(D=ex_dia, V=V, rho=rho, mu=mu)
print (f"Re={Re} and density = {rho}")
fd = friction_factor(Re=Re)
K = K_from_f(fd=fd, L=L, D=ex_dia)
P = dP_from_K(K=K, V=V, rho=rho)
P = P.to(u.mbar)
print (f"Area = {A}, Backpressure = {P}")
