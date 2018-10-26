import math
import ht
import fluids
import thermo
import intercoolerSizing as cooler
import variables as var

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import interpolate

import time



def psi_to_Pa(P):
    P=P/14.5038*1E5
    return P

def ft_to_m(ft):
    m= ft*12.*25.4/1000.
    return m

#specific fuel consumption
specFuel = var.fuel
specFuel = specFuel/2.2 #kg/HP/hr
specFuel = specFuel/750. #kg/W/hr
specFuel = specFuel/3600. #kg/W/s

bore = var.bore
stroke = var.stroke
cylinders = var.cylinders

revs = var.rpm #rpm

displacement = (math.pi * (bore/2.)**2) * stroke * cylinders
displacement = displacement / (1E3**3) #m3

flowVol = displacement/2. * revs/60.  #m3/s
volEff = var.VE
flowVol = flowVol * volEff

elevation = var.elevation # ft
elevation = ft_to_m(elevation)
ambient = var.ambient #C
ambient +=273 #K

#get air components and pressure at given elevation
atm = fluids.ATMOSPHERE_NRLMSISE00(Z=elevation) #z is meters
Patm = atm.P
N2 = atm.zs[0]
O2 = atm.zs[1]
Ar = atm.zs[2]

#create air mixture so I can get some properties I need
air = thermo.Mixture(['nitrogen', 'oxygen', 'argon'], Vfgs=[N2, O2, Ar], T=ambient, P=Patm)
k = air.isentropic_exponent
D1 = air.rho

# recalculate air density at given temp and pressure
def air_density_calc(T, P):
    air.calculate(T=T, P=P)
    density = air.rho
    return density

#compressor values
Pgage = var.boost #psi gage
Pgage= psi_to_Pa(Pgage) #Pa gage
Pabs = Pgage + Patm
Pman = Pabs - psi_to_Pa(var.pDrop) # est. pressure drop thru intercooler/piping

eta = .7 #compressor effieciency
#temp and density out of compressor
Tturbo = fluids.isentropic_T_rise_compression(P1=Patm, P2=Pabs, T1=ambient, k=k, eta=eta)

Tcooler1 = Tturbo
Tcooler2 = Tturbo
Pcooler1 = 0
Pcooler2 = 0

D2 = air_density_calc(T=Tturbo, P=Pabs)
D3 = air_density_calc(T=Tcooler2, P=Pman) #density at engine
D4 = air_density_calc(T=800, P=Patm)
massflowAir = flowVol * D3 #kg/s, mass flow into 2nd cooler

#loop intercooler calcs since flowrate influences Tout from intercooler (this is cooled from radiator)
Tcooler1 = Tturbo
Tcooler2 = Tturbo
Told = 0
while math.fabs(Tcooler2-Told) >1E-10:
    Told = Tcooler2
    print (Tcooler1-273)
    print (Tcooler2-273)

    D3 = air_density_calc(T=Tcooler2, P=Pman) #density at engine
    massflowAir = flowVol * D3 #kg/s, mass flow into 2nd cooler
    #print massflowAir*3600.
    Tcooler1, Pcooler1, Tco1 = cooler.get_Tout(Tturbo, massflowAir, D2, 4.5, 10.0, 4.5, var.coolantTemp)
    Tcooler2, Pcooler2, Tco2 = cooler.get_Tout(Tcooler1, massflowAir, D2, 4.5, 10.0, 4.5, var.intCoolTemp)
    #print Tco2



coolerEff = (Tturbo - Tcooler2)/ (Tturbo - ambient)

#How much fuel can I add to available air
air_fuel=var.AF
massflowFuel = massflowAir/air_fuel

massflowAirNoTurbo = flowVol * D1
massflowFuelNoTurbo = massflowAirNoTurbo/air_fuel

massflowAirNoCooler = flowVol *D2
massflowFuelNoCooler = massflowAirNoCooler/air_fuel

#How much power do I get from fuel mass
power= massflowFuel/specFuel #watts
power= power/750 #HP
torque = power*5252/revs
powerNoTurbo = massflowFuelNoTurbo/specFuel/750
powerNoCooler = massflowFuelNoCooler/specFuel/750

CFM_engine = flowVol * (3.281**3) * 60 #convert from SI back to CFM
CFM_cooler = CFM_engine *D3/D2
CFM_filter = CFM_engine *D3/D1
CFM_exhaust = CFM_engine *D3/D4
print (f"exhaust flow = {CFM_exhaust}")

Data = {'Power':power, 'CFM_engine':CFM_engine, 'CFM_cooler':CFM_cooler, 'CFM_filter':CFM_filter,
        'Turbo Temp':Tturbo-273, 'Cooler Temp':Tcooler2-273, 'Cooler Eff': coolerEff, 'Torque': torque, 'Displacement': displacement*1E3}
print (Data)
print (f"Turbo Adds {round(powerNoCooler-powerNoTurbo)} HP")
print (f"Intercooler Adds {round(power-powerNoCooler)} HP")
print (f"Intercooler1 dumps {round(Pcooler1)} kW")
print (f"Intercooler2 dumps {round(Pcooler2)} kW")
print (D1, D2, D3, D4)
