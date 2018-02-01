import thermo

Pwr = 5 #kW
Tank = 2 #gal
dT = 1 #F
dC = 40 #C
def F_to_C(dF):
    F1=0
    F2=F1 + dF
    C1=(F1-32)*5/9.
    C2=(F2-32)*5/9.
    dC=C2-C1
    return dC

def F_to_C2(F):
    C=(F-32)*5/9.
    return C


percentGlycol = .5
Coolant = thermo.Mixture(['water', 'glycol'], Vfls=[1-percentGlycol, percentGlycol], T= 273+25, P=2E5)
k_Coolant = Coolant.k # W/(m K), thermal conductivity
C_Coolant = Coolant.Cp # J/(kg K), Specific Heat
rho_Coolant = Coolant.rho # kg/m3, Density
mu_Coolant = Coolant.mu # Pa s, Dynamic Viscosity

vol=Tank*3.8/1000.
print vol
ma=vol*rho_Coolant
print ma
print C_Coolant
jol=ma*C_Coolant*dC
print jol
s=jol/(Pwr*1000)
print s
print 'Time to heat {0} gallons {1} degC = {2} min.'.format(Tank, dC, s/60.)
print 1/(20.)
