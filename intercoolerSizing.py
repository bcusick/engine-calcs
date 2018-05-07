import math
import ht
import fluids
import thermo
import variables as var

'''
    #PN INT000203

    x1 = 4.5
    y1 = 10.0
    z1 = 9

    #PN INT000219
    x2 = 3.75
    y2 = 4.5
    z2 = 9.75

    x = x1
    y = y1
    z = z1
    '''

def get_Tout(T, flow, rho, x, y, z, Ctemp):
    coreHeight = x * 25.4/1000 #all dims in meters
    coreWidth = y * 25.4/1000 #coolant tank to tank
    coreThickness = z * 25.4/1000

    wallThickness = 0.5/1000

    finHeightAir= 6.0/1000
    finSpacingAir = 25.4/12.5/1000  #ref frozen spec

    finHeightCoolant= 2.0/1000
    finSpacingCoolant = 25.4/8.5/1000  #ref frozen spec

    ## calculate surface areas
    numberofBars = math.floor((coreHeight - wallThickness)/(finHeightAir + wallThickness + finHeightCoolant + wallThickness))
    numberCoolantPass = (coreThickness/finSpacingCoolant + 1) * numberofBars

    numberAirPass = (coreWidth/finSpacingAir + 1) * numberofBars


    areaCoolant = numberCoolantPass * 2 * coreWidth * (finSpacingCoolant + finHeightCoolant)
    areaAir =  numberAirPass * 2 * coreThickness * (finSpacingAir + finHeightAir)

    ##fluid constants
    ##coolant to 50-50 glycol/water

    tempAir = T-273.0 # Celsius
    tempCoolant = Ctemp # Celsius

    percentGlycol = .5
    Coolant = thermo.Mixture(['water', 'glycol'], Vfls=[1-percentGlycol, percentGlycol], T= 273+tempCoolant, P=2E5)
    k_Coolant = Coolant.k # W/(m K), thermal conductivity
    C_Coolant = Coolant.Cp # J/(kg K), Specific Heat
    rho_Coolant = Coolant.rho # kg/m3, Density
    mu_Coolant = Coolant.mu # Pa s, Dynamic Viscosity

    k_Air = 0.02664 # W/(m K), thermal conductivity
    C_Air = 1004.16 # J/(kg K), Specific Heat
    rho_Air = rho # kg/m3, Density
    mu_Air = 0.00001912 # Pa s, Dynamic Viscosity

    ## operating conditions

    flowrateCoolant = 5 #GPM, volumetric
    flowrateCoolant = flowrateCoolant * 3.8 #LPM

    flowrateCoolant = flowrateCoolant /60.0/1000. # convert to m3/s
    massflowCoolant = flowrateCoolant *rho_Coolant

    massflowAir = flow
    flowrateAir = massflowAir/rho_Air

    ## fluids calcs
    #Coolant
    Dh_Coolant = 4 * (finHeightCoolant * finSpacingCoolant) / (2*(finHeightCoolant + finSpacingCoolant))

    tubeVelocity = flowrateCoolant/numberCoolantPass/(finHeightCoolant*finSpacingCoolant)
    reynoldsCoolant = fluids.core.Reynolds(D=Dh_Coolant, rho=rho_Coolant, V=tubeVelocity, mu=mu_Coolant)
    reynoldsCoolant = 5000.0 #force turbulent
    prandltCoolant = fluids.core.Prandtl(Cp=C_Coolant , k=k_Coolant , mu=mu_Coolant, nu=None, rho=None, alpha=None)
    if reynoldsCoolant<2600:
        nusseltCoolant = ht.conv_internal.laminar_Q_const()
    else:
        nusseltCoolant = ht.conv_internal.turbulent_Dittus_Boelter(Re=reynoldsCoolant, Pr=prandltCoolant, heating=True)
    h_Coolant = nusseltCoolant * k_Coolant / Dh_Coolant

    #AIR
    Dh_Air = 4 * (finHeightAir * finSpacingAir) / (2*(finHeightAir + finSpacingAir))
    airVelocity = flowrateAir/numberAirPass/(finHeightAir*finSpacingAir)
    reynoldsAir = fluids.core.Reynolds(D=Dh_Air, rho=rho_Air, V=airVelocity, mu=mu_Air)
    reynoldsAir = 5000.0 # force turbulent

    prandltAir = fluids.core.Prandtl(Cp=C_Air , k=k_Air , mu=mu_Air, nu=None, rho=None, alpha=None)
    if reynoldsAir<2600:
        nusseltAir = ht.conv_internal.laminar_Q_const()
    else:
        nusseltAir = ht.conv_internal.turbulent_Dittus_Boelter(Re=reynoldsAir, Pr=prandltAir, heating=False)

    #nusseltAir =ht.conv_external.Nu_cylinder_Zukauskas(Re=reynoldsAir, Pr=prandltAir, Prw=None)

    #nusseltAir = 10  # manual overide for laminare flow

    h_Air = nusseltAir * k_Air / Dh_Air

    #calculate UA
    UA = 1/(h_Coolant*areaCoolant) + 1/(h_Air*areaAir)
    UA = 1/UA

    #NTU = ht.hx.effectiveness_NTU_method(mh=massflowCoolant, mc=massflowAir, Cph=C_Coolant, Cpc=C_Air, subtype='crossflow', Thi=tempCoolant, Tho=None, Tci=tempAir, Tco=None, UA=UA)
    NTU = ht.hx.effectiveness_NTU_method(mh=massflowAir, mc=massflowCoolant, Cph=C_Air, Cpc=C_Coolant, subtype='crossflow', Thi=tempAir, Tho=None, Tci=tempCoolant, Tco=None, UA=UA)
    #print NTU
    #print NTU['Q']

    Tout = NTU['Tho'] + 273 #kelvin
    Pwr = NTU['Q'] / 1000 #kW
    TCout = NTU['Tco']

    #output = [Tout, flowrateAir2]


    return Tout, Pwr, TCout

'''

    vol=15*3.8/1000.
    ma=vol*rho_Coolant
    jol_10=ma*C_Coolant*10
    s=jol_10/(Pwr*1000)
    '''
