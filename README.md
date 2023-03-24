# Micro Grid User Energy Planning Tool Library (MiGUEL)

<p align="left">
  <img src="/documentation/MiGUEL_logo.png" alt="drawing" height="200"/>
</p>

## Table of contents
- [Introduction](#introduction)
- [Content and structure](#content-and-structure)
  - [Main](#main)
  - [Environment](#environment)
  - [Operator](#operator)
  - [Output](#output)
- [Project partners](#project-partners)
- [Dependencies](#dependencies)
- [References](#references)

## Introduction
MiGUEL is a python-based, open-source simulation tool to design, simulate and evaluate the performance of photovoltaic-diesel-hybrid systems. MiGUEL is based on a matlab tool developed at the Technische Hochschule Köln ([TH Köln](https://www.th-koeln.de/)). In the course of the research project Energy-Self-Sufficiency for Health Facilities in Ghana ([EnerSHelF](https://enershelf.de/)) the matlab tool was transferred to python, revised and additional components were added.  
MiGUEL aims to provide an easy-to-use simulation tool with low entry barriers and comprehensible results. Only a basic knowledge of the programming language is needed to use the tool. For the system design, simulation adn evaluation only a small number of parameters is needed. The simulation can run without data sets provided by the user. 
The results are provided in the form of csv files for each simulation step and in the form of an automatically generated pdf report. The csv files are understood as raw data for further processing. The pdf report serves as a project brochure. Here, the results are presented clearly and graphically, and an economic and ecological evaluation of the system is carried out.

## Authors and contributors
The main author is Paul Bohn ([@pdb-94](https://github.com/pdb-94)). Co-author of the project is Silvan Rummeny (TH Köln) who created the first approach within his PhD. Other contributors are Moritz End ([@moend95](https://github.com/moend95)). Further assistence was provided by Sascha Birk ([@pyosch](https://github.com/Pyosch)). The development of the tool was supervised by Prof. Dr. Schneiders ([TH Köln CIRE](https://www.th-koeln.de/anlagen-energie-und-maschinensysteme/cologne-institute-for-renewable-energy_13385.php)).

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

| Parameter | Description | dtype | Default | Unit| Comment |
|-----------|-------------|-------|---------|-|-|
| **name** | **Project name** | **str** |**MiGUEL Project**|
| **time** | **Project time data** | **dict** ||
| start | Start time | datetime.datetime ||
| end | End time | datetime.datetime ||
| step | Time resolution | datetime.timedelta |15|min|Possible resolutions: 1min, 15min, 60min|
| timezone | Time zone | str ||
| **location** | **Project location** | **dict** ||
| longitude | Longitude | float ||°||
| latitude | Latitude | float || °||
| altitude | Altitude | float || m||
| terrain | Terrain type | str ||| Terrain types mentioned in main.py description|
| **economy** | **Economical parameters** | **dict** ||
| d_rate | Discount rate | float ||
|lifetime | Project lifetime | int |20| a|
|currency| Currency| str| US$||If other currencies are used conversion rate needs to be applied|
|electricity_price |Electricity price|float||currency/kWh||
|diesel_price| Diesel price|float||currency/l|
|co2_price| Average CO2-price over system lifetime|float||currency/t||
|pv_feed_in_tariff| PV feed-in traiff | float ||currency/kWh||
|wt_feed_in_tariff| Wind turbine feed-in traiff | float ||currency/kWh||
|**ecology**| **Ecological parameters** | **dict** |||
|co2_grid| Specific CO2-emissions power grid |float||kg/kWh||
|co2_diesel| Specific CO2-emissions diesel |float |0.2665|kg/kWh||
| **blackout** | **Stable or unstable power grid** | **bool** | **False** ||**True: Unstable power grid; False: Stable power grid**|
|**blackout_data**|**csv-file path with blackout data**|**str**|||**csv-file with bool-values for every timestep**|
|**feed_in**| **Feed-in possible** |**bool**|**False**||**True: Feed-in possible, False: Feed-in not possible**|
|**weather_data**|**csv-file with weather data set**|**str**|||**Enables off-line usage**|


#### System components
MiGUEL features the following system components. Each component can be added to the Environment by using a different function. The list displays the system components and the function to add the component to the Environment.
|System component|Function|
|-|-|
|Load|.add_load|
|Photovoltaic|.add_PV|
|Wind turbine|.add_wind_turbine|
|Grid| .add_grid|
|Diesel generator|.add_diesel_generator|
|Energy storage|.add_storage|

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
The class DieselGenerator is based on a simplfied, self created generator model. The model assumes that in the future generators with low-load capability are used in PV-diesel hybrid systems. In comparison to conventional diesel generators, low-load diesel generators are more fuel efficient and therfore reduce CO2-emissions [3]. 

The input parameters for diesel generators are the nominal power [W], the fuel consumption at nominal power [l] and the diesel price [currency/l]. 

##### Energy storage

### Operator
The simulation process is divided in three steps. 

<p align="center">
  <img src="/documentation/simulation_process.png" alt="drawing" height="100"/>
</p>

The system design is the only time the user needs to interact with the program code. Here the Environment ([create Environment](#environment)) and the system components are created ([system components](#system-components)). The annual simulaton and the system evaluation are carried out by the [Operator](#operator).

#### Annual simulation
The energy system type depends on the input parameters and the system components in the energy system. A distinction is made between off-grid systems and on-grid systems. On-grid systems are further divided into stable systems (without blackouts) and unstable systems (with blackouts). Depending on the type of energy system different dispatch strategies are applied for the annual simulation.

<p align="center">
  <img src="/documentation/dispatch_priorities.svg" alt="drawing" height="400"/>
</p>

RE = Renewable energies &emsp; ES = Energy storage &emsp; DG = Diesel generator

The figure displays the dispatch strategies for all system components. If a system component is noot added to the system this component will be skipped in the dispatch.

#### System evaluation
The two key parameters for the system evaluation are the Levelized Cost of Energy (LCOE) in US$/kWh and the CO2-emissions [t] over the system lifetime. 

##### Levelized Cost of Energy
The LCOE are calculated accoring to Michael Papapetrou et. al. for every energy supply component [4]. The system LCOE is composed of the individual LCOEs of the system components, which are scaled according to the energetic share. The LCOE are calculated over the whole system lifetime. The LCOE includes the initial investment costs and the operation and maintenance cost. Cost for recycling are neglected in this evaluation. The investment adn operation and maintenance cost are based on specific cost from literature values. The specfic cost are scaled by the power (energy supply components) or capacity (energy storage).

##### CO2-emissions
The CO2-emissions are evaluated over the system lifetime. Included are the CO2-emissions during the production of the system component and the CO2-emissions emitted during the usage. 

### Output
MiGUEL provides two types of outputs. The first begin a csv-file with every every simulation time step. The csv-files can be used for further research or in depth analysis of the system behaviour. The csv-files do not include the system evaluation. The second output is the pdf-report. The report includes the most important results. The results are displyed graphical and will be explined briefly. 

#### csv-files
The csv-files display the raw data of the annual simulation. The file lists every time step of the simulation, the load and all system components, as well as their generation power.

<p align="center">
  <img src="/documentation/csv_example.png" alt="drawing" height="200"/>
</p>

#### Report
The pdf-Report is automatically creted by MiGUEL. It gives an overview of the simulation results and features the system evaluation based on the LCOE and CO2-emissions. The report is structured in the following chapters:

1) Introduction: Brief description of MiGUEL and EnerSHelF
2) Summary: Summary of the most important simulation results and system evaluation
3) Base data: Displays input parameters 
4) Climate data: Solar and wind data from PVGIS at the selected location
5) Energy consumption: Load profile
6) System configuration: Overview of selected system components
7) Dispatch: Annual simulation results
8) Evaluation: System evaluation based on LCOE and CO2-emissions over system lifetime

The report focuses not only on the energetic results of the system evaluation but also on economic and ecologic parameters. This makes the results more comprehensible compared to the csv-files. The pdf-report can used as a projekt brochure. 


## Project partners
<p align="center">
  <img src="/documentation/MiGUEL_logo.png" alt="drawing" height="200"/>
</p>
<p align="center">
  <img src="/documentation/th-koeln_white.png" alt="drawing" height="200"/>
   <img src="/documentation/EnerSHelF_logo.png" alt="drawing" height="200"/>
</p>

## Dependencies

[pandas](https://pandas.pydata.org/)

[numpy](https://numpy.org)

[matplotlib](https://matplotlib.org/)

[folium](https://python-visualization.github.io/folium/)

[geopy](https://geopy.readthedocs.io/en/stable/)

[fpdf](http://www.fpdf.org/)

[pvlib](https://pvlib-python.readthedocs.io/en/stable/)

[windpowerlib](https://windpowerlib.readthedocs.io/en/stable/)

[selenium](https://selenium-python.readthedocs.io/)

[plotly](https://plotly.com/python/)


## References

[1] William F. Holmgren, Clifford W. Hansen, and Mark A. Mikofski. “pvlib python: a python package for modeling solar energy systems.” Journal of Open Source Software, 3(29), 884, (2018). [https://doi.org/10.21105/joss.00884](https://doi.org/10.21105/joss.00884)

[2] Sabine Haas, Uwe Krien, Birgit Schachler, Stickler Bot, kyri-petrou, Velibor Zeli, Kumar Shivam, & Stephen Bosch. (2021). wind-python/windpowerlib: Silent Improvements (v0.2.1). Zenodo. [https://doi.org/10.5281/zenodo.4591809](https://doi.org/10.5281/zenodo.4591809)

[3] PV Magazine; "Low-load generators make photovoltaic diesel applications cleaner and more efficient"; 06. October 2015; online available:
[Niedrig-Last-Generatoren machen Photovoltaik-Diesel-Anwendungen sauberer und effizienter](https://www.pv-magazine.de/2015/10/06/niedrig-last-generatoren-machen-photovoltaik-diesel-anwendungen-sauberer-und-effizienter/)

[4] Michael Papapetrou, George Kosmadakis, Chapter 9 - Resource, environmental, and economic aspects of SGHE, Editor(s): Alessandro Tamburini, Andrea Cipollina, Giorgio Micale, In Woodhead Publishing Series in Energy, Salinity Gradient Heat Engines, Woodhead Publishing, 2022, Pages 319-353, ISBN 9780081028476, [https://doi.org/10.1016/B978-0-08-102847-6.00006-1](https://doi.org/10.1016/B978-0-08-102847-6.00006-1)
