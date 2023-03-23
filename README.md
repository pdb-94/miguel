# Micro Grid User Energy Planning Tool Library (MiGUEL)



## Introdcution

MiGUEL is a python-based, open-source simulation tool to design, simulate and evaluate the performance of photovoltaic-diesel-hybrid systems. MiGUEL is based on a matlab tool developed at the Technische Hochschule Köln (TH Köln). In the course of the research project Energy-Self-Sufficiency for Health Facilities in Ghana ([EnerSHelF](https://enershelf.de/)) the matlab tool was transferred to python, revised and additional components were added.  
MiGUEL aims to provide an easy-to-use simulation tool with low entry barriers and comprehensible results. Only a basic knowledge of the programming language is needed to use the tool. For the system design, simulation adn evaluation only a small number of parameters is needed. The simulation can run without data sets provided by the user. 
The results are provided in the form of csv files for each simulation step and in the form of an automatically generated pdf report. The csv files are understood as raw data for further processing. The pdf report serves as a project brochure. Here, the results are presented clearly and graphically, and an economic and ecological evaluation of the system is carried out.


## Authors and contributors
The main author is Paul Bohn (@pdb-94). Co-author of the project is Silvan Rummeny (TH Köln) who created the first approach within his PhD. Other contributors are Moritz End (@moend95). Further assistence was provided by Sascha Birk (@pyosch).

## Content and structure
The basic structure of MiGUEL is displayed below. 
![Structure](/documentation/structure.png)
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
2) Input via csv-file: If actual measurement data from the subject is available, the data can be returned to the program as a csv-file.

If the resolution of the load profile does not match the environment time resolution the resolution of the load profile will be adjusted by summarizing or filling in the values. If no annual load profile is provided the load profile will be repeated to create an annual load profile.




The simulation process is divided in three steps.
![SimulationProcess](/documantation/simulation_process.png)


### System components

##


## Project partners
![MiGUEL](/documentation/MiGUEL_logo.png )
![TH Kön](/documentation/th-koeln.png)
![EnerSHelF](/documentation/EnerSHelF_logo.png)
