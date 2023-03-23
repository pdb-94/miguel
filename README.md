# Micro Grid User Energy Planning Tool Library (MiGUEL)



## Introdcution

MiGUEL is a python-based, open-source simulation tool to design, simulate and evaluate the performance of photovoltaic-diesel-hybrid systems. MiGUEL is based on a matlab tool developed at the Technische Hochschule Köln (TH Köln). In the course of the research project Energy-Self-Sufficiency for Health Facilities in Ghana ([EnerSHelF](https://enershelf.de/)) the matlab tool was transferred to python, revised and additional components were added.  
MiGUEL aims to provide an easy-to-use simulation tool with low entry barriers and comprehensible results. Only a basic knowledge of the programming language is needed to use the tool. For the system design, simulation adn evaluation only a small number of parameters is needed. The simulation can run without data sets provided by the user. 
The results are provided in the form of csv files for each simulation step and in the form of an automatically generated pdf report. The csv files are understood as raw data for further processing. The pdf report serves as a project brochure. Here, the results are presented clearly and graphically, and an economic and ecological evaluation of the system is carried out.


## Authors and contributors
The main author is Paul Bohn (@pdb-94). Co-author of the project is Silvan Rummeny (TH Köln) who created the first approach within his PhD. Other contributors are Moritz End (@moend95). Further assistence was provided by Sascha Birk (@pyosch).

## Content and structure
The basic structure of MiGUEL is displayed below. 

<p align="center">
  <img src="/documentation/structure.png" alt="drawing" height="200"/>
</p>

The class Environment represents the energy system. It takes basic parameters such as time frame, location, economic and ecologic parameters. System components can be added to the Environment. The Operator runs the simulation and evaluation of the designed energy system. The class Report creates the pdf-report. The program is run by the main file.

### Main
The main file is used to run the program. The main file is the only time the user has to interact with the source code.  The Environment, Operator and Report are created by the user. 

### Environment
The class Environment represents the energy system. 
#### Input parameters
To create an instance of the class the following parameters have to provided. The list displays all input parameters, a brief description and the data type.
- name: project name (str)
- time: time data (dict)
  - start: start of annual simulation (datetime.datetime)
  - end: end of annual simulation (datetime.datetime)
  - step: time resolution: 1min, 15min, 60min (datetime.timedelta)
  - timezone: timezone (str)
- location: project location (dict)
  - longitude (float)
  - latitude (float)
  - altitude (float)
  - terrain (str)
- economy: economical parameters (dict)
  - currency: project currency (US$)
  - d_rate: discount rate (float)
  - lifetime: project lifetime [a] (int)
  - electricity_price: grid price [US$/kWh] (float)
  - diesel_price: Dieseel price [US$/l] (float)
  - co2_price: CO2 price [US$/t] (float)
  - pv_feed_in_teriff: PV feed-in tariff [US$/kWh] (float)
  - wt_feed_in_teriff: wind turbine feed-in tariff [US$/kWh] (float)
- ecology: ecological parameters (dict)
  - co2_grid: specific CO2 emissions per kWh power grid [kg/kWh] (float)
  - co2_diesel: specific CO2 emissions per kWh diesel [kg/kWh] (float)
- blackout: True: unstable power grid, False: stable power grid (bool)
- blackout_data: csv-file with blackout events (str)
- feed_in: True: Feed-in possible, False: Feed-in not possible (bool)
- weather_data: csv-file path with weather data (str) - OPTIONAL only for offline use

#### System copmonents
MiGUEL features the following system components. Each component can be added to the Environment by using a different function. The list displays the system components and the function to add the component to the Environment.
- Load (.add_load)
- Photovoltaic systems (.add_pv)
- Wind turbines (.add_wind_turbine)
- Grid (.add_grid)
- Diesel generator (.add_diesel_generator)
- Energy Storage (.add_storage)

##### Load
The system component load represents theload profile of the subject under review. The load profile can be generated in two different ways. 
1) Standard load profile for african hospitals: In the course of EnerSHelF standard load profiles for Ghanaian hospitals were created. This daily standard load profile is implemented in the program. To create a load profile from the standard load profile the annual electricity consumption needs to be returned to the function (annuala_consumption). The standard load profile has a 15min-time resolution.
2) Input via csv-file: If actual measurement data from the subject is available, the data can be returned to the program as a csv-file (load_profile).

The accuracy of the simulation resuls inceases with the quality of the input data. Using the adjusted standard load profile will provided less accurate results compared to measured data. The library [Load Profile Creator](https://github.com/pdb-94/load_profile_creator) can be used to create load profiles based on theelectric inventory of the subject.

If the resolution of the load profile does not match the environment time resolution the resolution of the load profile will be adjusted by summarizing or filling in the values. If no annual load profile is provided the load profile will be repeated to create an annual load profile.


##### Photovoltaic
The class Photovoltaic is based on the library [pvlib](https://pvlib-python.readthedocs.io/en/stable/#) [1]. PV systems can be added in three different ways:
1) Adding basic system parameters: Simplest way to create PV system with on ly basic parameters such as nominal power, surface tilt and azimuth, module and inverter power range. The class Photovoltaic will randomly choose a PV module, number if modules and an inverter that match the parameters
2) Selecting your modules and inverter: All sytem parameters such as module, number of modules, inverter, strings per inverter, modules per string, surface tilt and azimuth, ... need to be returned to the function.
3) Provide measured PV data: Input of measured PV as a csv-file

pvlib will run the PV simulation based on the selected system parameters. The weather data for the project location is retrieved by the Environment. The data source is [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) hosted by the European Comission.


##### Wind turbine
The class WindTurbine is based on the library [windpowerlib](https://windpowerlib.readthedocs.io/en/stable/index.html) [2]. To add wind turbines to the Environment the [turbine type](https://github.com/wind-python/windpowerlib/blob/master/windpowerlib/oedb/turbine_data.csv) and the turbine height [m] need to be returned.

The weather data for the project location is retrieved by the Environment. The data source is [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) hosted by the European Comission. Inside the class WindTurbine the weather data is processed so it can be used for the simulation. 

##### Grid
The class grid represents the power grid. The power grid provides electricity to the energy system. Depending on the input of blackout data a stable or unstable power grid is simulated. The possibility of feed-in is determined in the Environment. To add a power grid to the Environment no specific parameters are needed.

##### Diesel Generator

##### Energy storage

### Operator

The simulation process is divided in three steps.

<p align="center">
  <img src="/documentation/simulation_process.png" alt="drawing" height="100"/>
</p>





## Project partners
<p align="center">
  <img src="/documentation/MiGUEL_logo.png" alt="drawing" height="200"/>
</p>
<p align="center">
  <img src="/documentation/th-koeln_white.png" alt="drawing" height="200" align="center"/>
</p>
<p align="center">
  <img src="/documentation/EnerSHelF_logo.png" alt="drawing" height="200" align="center"/>
</p>


## References

[1] William F. Holmgren, Clifford W. Hansen, and Mark A. Mikofski. “pvlib python: a python package for modeling solar energy systems.” Journal of Open Source Software, 3(29), 884, (2018). [https://doi.org/10.21105/joss.00884](https://doi.org/10.21105/joss.00884)

[2] Sabine Haas, Uwe Krien, Birgit Schachler, Stickler Bot, kyri-petrou, Velibor Zeli, Kumar Shivam, & Stephen Bosch. (2021). wind-python/windpowerlib: Silent Improvements (v0.2.1). Zenodo. [https://doi.org/10.5281/zenodo.4591809](https://doi.org/10.5281/zenodo.4591809)
