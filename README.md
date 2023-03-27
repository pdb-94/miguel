# Micro Grid User Energy Planning Tool Library (MiGUEL)

<p align="left">
  <img src="/documentation/MiGUEL_logo.png" alt="drawing" height="200"/>
</p>

## Introduction
MiGUEL is a python-based, open-source simulation tool to design, simulate and evaluate the performance of photovoltaic-diesel-hybrid systems. MiGUEL is based on a matlab tool developed at the Technische Hochschule Köln ([TH Köln](https://www.th-koeln.de/)). In the course of the research project Energy-Self-Sufficiency for Health Facilities in Ghana ([EnerSHelF](https://enershelf.de/)) the matlab tool was transferred to python, revised and additional components were added.  
MiGUEL aims to provide an easy-to-use simulation tool with low entry barriers and comprehensible results. Only a basic knowledge of the programming language is needed to use the tool. For the system design, simulation adn evaluation only a small number of parameters is needed. The simulation can run without data sets provided by the user. 
The results are provided in the form of csv files for each simulation step and in the form of an automatically generated pdf report. The csv files are understood as raw data for further processing. The pdf report serves as a project brochure. Here, the results are presented clearly and graphically, and an economic and ecological evaluation of the system is carried out.

## Table of contents
- [Authors and contributors](#authors-and-contributors)
- [Content and structure](#content-and-structure)
  - [Main](#main)
  - [Environment](#environment)
  - [Operator](#operator)
  - [Output](#output)
- [Project partners](#project-partners)
- [Dependencies](#dependencies)
- [References](#references)

## Authors and contributors
The main author is Paul Bohn ([@pdb-94](https://github.com/pdb-94)). Co-author of the project is Silvan Rummeny ([@srummeny](https://github.com/srummeny)) who created the first approach within his PhD. Other contributors are Moritz End ([@moend95](https://github.com/moend95)). Further assistence was provided by Sascha Birk ([@pyosch](https://github.com/Pyosch)). The development of the tool was supervised by Prof. Dr. Schneiders ([TH Köln CIRE](https://www.th-koeln.de/anlagen-energie-und-maschinensysteme/cologne-institute-for-renewable-energy_13385.php)).

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
| **name** | **Project name** | **str** |**MiGUEL Project**|-||
| **time** | **Project time data** | **dict** |-|-||
| start | Start time | datetime.datetime |-|-||
| end | End time | datetime.datetime |-|-||
| step | Time resolution | datetime.timedelta |15|min|Possible resolutions: 1min, 15min, 60min|
| timezone | Time zone | str |-|-||
| **location** | **Project location** | **dict** |-|-||
| longitude | Longitude | float |-|°||
| latitude | Latitude | float |-| °||
| altitude | Altitude | float |-|m||
| terrain | Terrain type | str |-|-| Terrain types mentioned in main.py description|
| **economy** | **Economical parameters** | **dict** |-|-||
| d_rate | Discount rate | float |-|-||
|lifetime | Project lifetime | int |20| a|
|currency| Currency| str| US$|-|If other currencies are used conversion rate needs to be applied|
|electricity_price |Electricity price|float|-|US$/kWh||
|diesel_price| Diesel price|float|-|US$/l|
|co2_price| Average CO2-price over system lifetime|float|-|US$/t||
|pv_feed_in_tariff| PV feed-in traiff | float |-|US$/kWh||
|wt_feed_in_tariff| Wind turbine feed-in traiff | float |-|US$/kWh||
|**ecology**| **Ecological parameters** | **dict** |-|-|
|co2_grid| Specific CO2-emissions power grid |float|-|kg/kWh||
|co2_diesel| Specific CO2-emissions diesel |float |0.2665|kg/kWh||
| **blackout** | **Stable or unstable power grid** | **bool** | **False** |-|**True: Unstable power grid; False: Stable power grid**|
|**blackout_data**|**csv-file path with blackout data**|**str**|-|-|**csv-file with bool-values for every timestep**|
|**feed_in**| **Feed-in possible** |**bool**|**False**|-|**True: Feed-in possible, False: Feed-in not possible**|
|**weather_data**|**csv-file path with weather data set**|**str**|-|-|**Enables off-line usage**|


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

| Parameter | Description | dtype | Default | Unit| Comment |
|-----------|-------------|-------|---------|-|-|
|annual_consumption|Annual electricity consumption|float|-|kWh|Only for method 1|
|load_profile|File path to load profile data|str|-|-|csv-file with load profile, Only for method 2|

The accuracy of the simulation resuls inceases with the quality of the input data. Using the adjusted standard load profile will provided less accurate results compared to measured data. The library [Load Profile Creator](https://github.com/pdb-94/load_profile_creator) can be used to create load profiles based on theelectric inventory of the subject.

If the resolution of the load profile does not match the environment time resolution the resolution of the load profile will be adjusted by summarizing or filling in the values. If no annual load profile is provided the load profile will be repeated to create an annual load profile.


##### Photovoltaic
The class Photovoltaic is based on the library [pvlib](https://pvlib-python.readthedocs.io/en/stable/#) [1]. There are three methods implemented to create PV systems:
1) Adding basic system parameters: Simplest way to create PV system with on ly basic parameters such as nominal power, surface tilt and azimuth, module and inverter power range. The class Photovoltaic will randomly choose a PV module, number if modules and an inverter that match the parameters
2) Selecting your modules and inverter: All sytem parameters such as module, number of modules, inverter, strings per inverter, modules per string, surface tilt and azimuth, ... need to be returned to the function.
3) Provide measured PV data: Input of measured PV as a csv-file

| Parameter | Description | dtype | Default | Unit| Comment |
|-----------|-------------|-------|---------|-|-|
|p_n|Nominal power|float|-|W||
|pv_profile|File path to pv porduction data|str|-|-|Measured pv data in csv file, Only for method 3|
|**pv_data**|**PV system parameters**|**dict**|-|-||
|pv_module|PV module|str|-|-|PV module from pvlib database, Only for method 2|
|inverter|Inverter|str|-|-|Inverter from pvlib database, Only for method 2|
|modules_per_string|Modules per string|int|-|-|Only for method 2|
|strings_per_inverter|Strings per inverster|int|-|-|Only for method 2|
|surface_tilt|PV system tilt angle|float|-|-||
|surface_azimuth|PV system orientation|float|-|-|North=0°, East=90°, South=180°, West=270°|
|min_module_power|Minimum module power|float|-|W|Only for method 1|
|max_module_power|Maximum module power|float|-|W|Only for method 1|
|inverter_power_range|Inverter power range|float|-|W|Only for method 1|


pvlib will run the PV simulation based on the selected system parameters. The weather data for the project location is retrieved by the Environment. The data source is [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) hosted by the European Comission.


##### Wind turbine
The class WindTurbine is based on the library [windpowerlib](https://windpowerlib.readthedocs.io/en/stable/index.html) [2]. To add wind turbines to the Environment the [turbine type](https://github.com/wind-python/windpowerlib/blob/master/windpowerlib/oedb/turbine_data.csv) and the turbine height [m] need to be returned.

| Parameter | Description | dtype | Default | Unit| Comment |
|-|-|-|-|-|-|
|**turbine_data**|**Turbine data**|**dict**|-|-||
|turbin_type|Turbine type|str|-|-|Turbine name and manufacturer from windpowerlib register|
|tubine_height|Hub height|float|-|m||

The weather data for the project location is retrieved by the Environment. The data source is [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) hosted by the European Comission. Inside the class WindTurbine the weather data is processed so it can be used for the simulation. 

##### Grid
The class grid represents the power grid. The power grid provides electricity to the energy system. Depending on the input of blackout data a stable or unstable power grid is simulated. The possibility of feed-in is determined in the Environment. To add a power grid to the Environment no specific parameters are needed.

##### Diesel Generator
The class DieselGenerator is based on a simplfied, self created generator model. The model assumes that in the future generators with low-load capability are used in PV-diesel hybrid systems. In comparison to conventional diesel generators, low-load diesel generators are more fuel efficient and therfore reduce CO2-emissions [3]. The input parameters for diesel generators are displayed in the table below.

| Parameter | Description | dtype | Default | Unit| Comment |
|-|-|-|-|-|-|
|p_n| Nominal power|float|-|W||
|fuel_consumption|Fuel consumption at nominal power|float|-|l||
|fuel_price|Fuel price|float|-|US$/l||


The fuel consumption for the generator is calculated every time step using the following equation. The equation was derived using characteristic values of a 150 kW diesel generator at loads of 0%, 25%, 50%, 75% and 100% [4]. 

*fc(l) = - 1.66360855 x l<sup> 4</sup> +3.96330272 x l<sup> 3</sup> -3.19877674 x l<sup> 2</sup>+1.8990825 x l +0*

*fc = relative fuel consumption [%]* &emsp; *l = relative load [%]*



##### Energy storage
The class Storage represents energy storage systems. The energy storage is represented by a basic model. The input parameters for storage systems are dsiplay in the table below:
| Parameter | Description | dtype | Default | Unit| Comment |
|-|-|-|-|-|-|
|p_n|Nominal power|float|-|W||
|c|capacity|float|-|Wh||
|soc|Initial state of charge|float|0.5|-||
|soc_max| Maximum state of charge|float|0.95|-||
|soc_min|Minimum state of charge|float|0.05|-||
|n_discharge|Discharge efficiency|float|0.8|-||
|n_charge|Charge efficiency|float|0.8|-||


The energy storage can be either charged or discharged at any time step. 

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
The LCOE are calculated accoring to Michael Papapetrou et. al. for every energy supply component [5]. The system LCOE is composed of the individual LCOEs of the system components, which are scaled according to the energetic share. The LCOE are calculated over the whole system lifetime. The LCOE includes the initial investment costs and the operation and maintenance cost. Cost for recycling are neglected in this evaluation. The investment adn operation and maintenance cost are based on specific cost from literature values. The specfic cost are scaled by the power (energy supply components) or capacity (energy storage).

| System component | Specific investment cost | Specific annual operation/maintenance cost | Unit | Source |
|-|-|-|-|-|
|PV|496.13|7.55|US$/kW|[6] [7]|
|Wind turbine|1160|43|US$/kW|[8] [9]|
|Diesel generator|468|Investment cost *0.03; 0.021 US$/kWh|US$/kW|[10] [11]|
|Energy storage|1200|30|US$/kWh|[12]|

##### CO2-emissions
The CO2-emissions are evaluated over the system lifetime. Included are the CO2-emissions during the production of the system component and the CO2-emissions emitted during the usage. 
| System component | Specific CO2 emissions production/installation | Unit | Source |
|-|-|-|-|
|PV|460|kg/kW|[13]|
|Wind turbine|200|kg/kW|[14]|
|Diesel generator|265|kg/kW|[15]|
|Energy storage|103|kg/kWh|[16]|

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

[4] Generator Source, LLC 1999-2023; Approximate Diesel Fuel Consumption Chart; online available: [https://www.generatorsource.com/Diesel_Fuel_Consumption.aspx](https://www.generatorsource.com/Diesel_Fuel_Consumption.aspx)

[5] Michael Papapetrou, George Kosmadakis, Chapter 9 - Resource, environmental, and economic aspects of SGHE, Editor(s): Alessandro Tamburini, Andrea Cipollina, Giorgio Micale, In Woodhead Publishing Series in Energy, Salinity Gradient Heat Engines, Woodhead Publishing, 2022, Pages 319-353, ISBN 9780081028476, [https://doi.org/10.1016/B978-0-08-102847-6.00006-1](https://doi.org/10.1016/B978-0-08-102847-6.00006-1)

[6] Vartiainen, E, Masson, G, Breyer, C, Moser, D, Román Medina, E. Impact of weighted average cost of capital, capital expenditure, and other parameters on future utility-scale PV levelised cost of electricity. Prog Photovolt Res Appl. 2020; 28: 439– 453. [https://doi.org/10.1002/pip.3189](https://doi.org/10.1002/pip.3189)

[7] Bjarne Steffen, Martin Beuse, Paul Tautorat, Tobias S. Schmidt, Experience Curves for Operations and Maintenance Costs of Renewable Energy Technologies, Joule, Volume 4, Issue 2, 2020, Pages 359-375, ISSN 2542-4351, [https://doi.org/10.1016/j.joule.2019.11.012]([https://www.sciencedirect.com/science/article/pii/S2542435119305793](https://doi.org/10.1016/j.joule.2019.11.012))

[8] Lucas Sens, Ulf Neuling, Martin Kaltschmitt, Capital expenditure and levelized cost of electricity of photovoltaic plants and wind turbines – Development by 2050, Renewable Energy, Volume 185, 2022, Pages 525-537, ISSN 0960-1481, [https://doi.org/10.1016/j.renene.2021.12.042]([https://www.sciencedirect.com/science/article/pii/S0960148121017626](https://doi.org/10.1016/j.renene.2021.12.042)

[9] Tyler Stehly, Philipp Beiter, and Patrick Duffy, National Renewable Energy Laboratory, 2019 Cost of Wind Energy Review, 2019, [https://www.nrel.gov/docs/fy21osti/78471.pdf9](https://www.nrel.gov/docs/fy21osti/78471.pdf)

[10] James Hamilton, Michael Negnevitsky, Xiaolin Wang, The potential of variable speed diesel application in increasing renewable energy source penetration, Energy Procedia, Volume 160, 2019, Pages 558-565, ISSN 1876-6102, [https://doi.org/10.1016/j.egypro.2019.02.206](https://doi.org/10.1016/j.egypro.2019.02.206)

[11] The EU Global Technical Assistance Facility for Sustainable Energy (EU GTAF), Sustainable Energy Handbook Module 6.1 Simplified Financial Models

[12] National Renewable Energy Laboratory, Utility-Scale Battery Storage, 2023, [https://atb.nrel.gov/electricity/2022/utility-scale_battery_storage](https://atb.nrel.gov/electricity/2022/utility-scale_battery_storage)

[13] Fraunhofer ISE, Photovoltaics and Climate Change, 2020, [https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/ISE-Sustainable-PV-Manufacturing-in-Europe.pdf(https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/ISE-Sustainable-PV-Manufacturing-in-Europe.pdf)


[14] Ozoemena, M., Cheung, W.M. & Hasan, R. Comparative LCA of technology improvement opportunities for a 1.5-MW wind turbine in the context of an onshore wind farm. Clean Techn Environ Policy 20, 173–190 (2018). [https://doi.org/10.1007/s10098-017-1466-2](https://doi.org/10.1007/s10098-017-1466-2)

[15] Friso Klemann, University Utrecht, The environmental impact of cycling 1,600 MWh electricity - A Life Cycle Assessment of a lithium-ion battery from Greener Power Solutions (P. 35)

[16] Hao, H.; Mu, Z.; Jiang, S.; Liu, Z.; Zhao, F. GHG Emissions from the Production of Lithium-Ion Batteries for Electric Vehicles in China. Sustainability 2017, 9, 504. [https://doi.org/10.3390/su9040504](https://doi.org/10.3390/su9040504)
