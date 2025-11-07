# Micro Grid User Energy Planning Tool Library (MiGUEL)

<p align="left">
  <img src="/documentation/MiGUEL_logo.png" alt="drawing" height="200"/>
</p>

## Disclaimer 
MiGUEL is continously optimized in terms of handling and outputs. 


## Introduction
MiGUEL is a python-based, open-source simulation tool to design, simulate and evaluate the performance of **renewable energy hybrid systems with hydrogen storage**. MiGUEL is based on a matlab tool developed at the Technische Hochschule Köln ([TH Köln](https://www.th-koeln.de/)). In the course of the research project Energy-Self-Sufficiency for Health Facilities in Ghana ([EnerSHelF](https://enershelf.de/)) the matlab tool was transferred to python, revised and additional components were added.  

**NEW in 2024/2025:** MiGUEL now includes comprehensive **hydrogen system components** (Electrolyser, H2 Storage, Fuel Cell) enabling seasonal energy storage and power-to-gas-to-power applications. The tool supports both traditional battery storage and innovative hydrogen-based long-term storage solutions.

MiGUEL aims to provide an easy-to-use simulation tool with low entry barriers and comprehensible results. Only a basic knowledge of the programming language is needed to use the tool. For the system design, simulation and evaluation, only a small number of parameters is needed. The simulation can run without data sets provided by the user. 

The results are provided in the form of csv files for each simulation step and in the form of an automatically generated pdf report. The csv files are understood as raw data for further processing. The pdf report serves as a project brochure. Here, the results are presented clearly and graphically, and an economic and ecological evaluation of the system is carried out.

### Key Features
✅ **Renewable Energy**: Solar PV and Wind Turbine modeling  
✅ **Hydrogen System**: Electrolyser, H2 Storage, Fuel Cell for seasonal storage  
✅ **Battery Storage**: Short-term electrical energy storage  
✅ **Grid Connection**: Import/export with blackout modeling  
✅ **Economic Analysis**: LCOE, NPV, investment cost calculations  
✅ **Environmental Impact**: CO2 emissions tracking and reduction analysis  
✅ **Modern GUI**: User-friendly interface for system design (see [Modern GUI](#modern-graphical-user-interface))

## Table of contents
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Authors and contributors](#authors-and-contributors)
- [Content and structure](#content-and-structure)
  - [Main](#main)
  - [Environment](#environment)
  - [Operator](#operator)
  - [Evaluation](#evaluation)
  - [Output](#output)
- [Modern Graphical User Interface](#modern-graphical-user-interface-20242025)
- [Legacy Graphical User Interface](#legacy-graphical-user-interface-pyqt5---2023)
- [Database](#database)
- [Project partners](#project-partners)
- [Dependencies](#dependencies)
- [References](#references)
- [Appendix](#appendix)

## Installation

### Requirements
- Python 3.8 or higher (3.11+ recommended)
- pip (Python package installer)

### Installation Steps

1. **Clone or download the repository:**
   ```bash
   git clone https://github.com/pdb-94/miguel.git
   cd miguel
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify installation:**
   ```bash
   python -c "import environment; import operation; import evaluation; print('MiGUEL installed successfully!')"
   ```

### Troubleshooting Installation

**pvlib/h5py binary compatibility issues:**
```bash
pip install --upgrade numpy==1.24.4
pip install --upgrade h5py==3.8.0
pip install --upgrade pvlib
```

**GUI not opening (tkinter missing):**
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# macOS - tkinter is included with Python from python.org
# Windows - tkinter is included by default
```

## Quick Start

### Using the Modern GUI (Easiest)
```bash
python launch_gui.py
```
Follow the 7 tabs to configure your system, run simulation, and view results.

### Using Python Code (Most Flexible)
```python
from environment import Environment
from operation import Operator
from evaluation import Evaluation
from datetime import datetime, timedelta

# 1. Create environment
time = {
    'start': datetime(2023, 1, 1),
    'end': datetime(2023, 12, 31),
    'step': timedelta(minutes=60),
    'timezone': 'UTC'
}

location = {'latitude': 52.52, 'longitude': 13.40, 'terrain': 'urban'}
economy = {'d_rate': 0.05, 'lifetime': 20, 'electricity_price': 0.15}
ecology = {'co2_grid': 0.5}

env = Environment(name='Example', time=time, location=location, 
                  economy=economy, ecology=ecology, grid_connection=True)

# 2. Add components
env.add_load(annual_consumption=50000, ref_profile='H0')
env.add_pv(p_n=100000, pv_data={'surface_tilt': 30, 'surface_azimuth': 180})
env.add_storage(p_n=50000, c=200000, soc=0.5)

# 3. Add hydrogen system (optional)
env.add_electrolyser(p_n=50000)
env.add_H2_Storage(capacity=100, initial_level=0.1)
env.add_fuel_cell(p_n=30000)

# 4. Run simulation
operator = Operator(env=env)

# 5. Evaluate
evaluation = Evaluation(env=env, operator=operator)

# 6. Export
operator.df.to_excel('results.xlsx')
print(f"LCOE: ${evaluation.lcoe:.4f}/kWh")
```

### Running Examples
```bash
# Interactive examples
python gui_example.py

# Choose:
# 1 - Simple example (PV + Battery)
# 2 - Hydrogen example (PV + Battery + H2)
# 3 - Both
```

For more detailed guides:
- **QUICKSTART.md** - Quick start guide with tips
- **GUI_README.md** - Complete GUI user manual
- **GUI_ARCHITECTURE.py** - Technical documentation
- **documentation/HYDROGEN_SYSTEM_ARCHITECTURE.md** - Detailed hydrogen system documentation

## Authors and contributors
The main author is Paul Bohn ([@pdb-94](https://github.com/pdb-94)). Co-author of the project is Silvan Rummeny ([@srummeny](https://github.com/srummeny)) who created the first approach within his PhD. Key contributors include Moritz End ([@moend95](https://github.com/moend95)) who developed the hydrogen system components and modern GUI (2024/2025). Further assistance was provided by Sascha Birk ([@pyosch](https://github.com/Pyosch)). Academic contributions include Yassine Maali's master thesis work on MiGUEL architecture and system design. The development of the tool was supervised by Prof. Dr. Schneiders ([TH Köln CIRE](https://www.th-koeln.de/anlagen-energie-und-maschinensysteme/cologne-institute-for-renewable-energy_13385.php)).

## Content and structure
The basic structure of MiGUEL is displayed below. 

<p align="center">
  <img src="/documentation/structure.png" alt="drawing" height="200"/>
</p>

The class **Environment** represents the energy system. It takes basic parameters such as time frame, location, economic and ecologic parameters. System components can be added to the Environment. The **Operator** runs the simulation and evaluation of the designed energy system. The class **Evaluation** computes economic and environmental metrics. The class **Report** creates the pdf-report. The program is run by the main file.

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        ENVIRONMENT                          │
│  (System configuration, time, location, economics)          │
└────────┬────────────────────────────────────────────────────┘
         │
         ├──▶ Load Profile
         ├──▶ Solar PV (multiple)
         ├──▶ Wind Turbine (multiple)
         ├──▶ Battery Storage (multiple)
         ├──▶ Grid Connection
         │
         ├──▶ Hydrogen System:
         │    ├─ Electrolyser (PV → H2)
         │    ├─ H2 Storage (seasonal buffer)
         │    └─ Fuel Cell (H2 → Power)
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                         OPERATOR                            │
│         (Dispatch simulation, energy flows)                 │
│                                                             │
│  For each timestep:                                         │
│   1. Calculate renewable generation (PV, Wind)              │
│   2. Match load with available power                        │
│   3. Charge/discharge battery storage                       │
│   4. Excess PV → Electrolyser → H2 Storage                  │
│   5. H2 Storage → Fuel Cell → Power (when needed)           │
│   6. Grid import/export (if connected)                      │
│                                                             │
│  Output: Timestep-by-timestep power flows (DataFrame)       │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                       EVALUATION                            │
│    (LCOE, CO2 emissions, renewable fraction, H2 metrics)    │
│                                                             │
│  • Levelized Cost of Energy (LCOE)                          │
│  • Net Present Cost (NPC)                                   │
│  • Total CO2 emissions & avoided emissions                  │
│  • Renewable energy fraction                                │
│  • Total H2 produced & consumed                             │
│  • Grid import/export energy                                │
└────────┬────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT & REPORTING                        │
│                                                             │
│  • CSV files (raw timestep data)                            │
│  • Excel export (detailed results)                          │
│  • PDF report (system overview & evaluation)                │
│  • GUI results display                                      │
└─────────────────────────────────────────────────────────────┘
```

### Main
The main file is used to run the program. The main file is the only time the user has to interact with the source code.  The Environment, Operator and Report are created by the user. 

### Environment
The class Environment represents the energy system. 
#### Input parameters
To create an instance of the class, the following parameters have to be provided. The list displays all input parameters, a brief description and the data type.

| Parameter         | Description                             | dtype              | Default            | Unit    | Comment                                                          |
|-------------------|-----------------------------------------|--------------------|--------------------|---------|------------------------------------------------------------------|
| **name**          | **Project name**                        | **str**            | **MiGUEL Project** | -       |                                                                  |
| **time**          | **Project time data**                   | **dict**           | -                  | -       |                                                                  |
| start             | Start time                              | datetime.datetime  | -                  | -       |                                                                  |
| end               | End time                                | datetime.datetime  | -                  | -       |                                                                  |
| step              | Time resolution                         | datetime.timedelta | 15                 | min     | Possible resolutions: 15min, 60min                               |
| timezone          | Time zone                               | str                | -                  | -       |                                                                  |
| **location**      | **Project location**                    | **dict**           | -                  | -       |                                                                  |
| longitude         | Longitude                               | float              | -                  | °       |                                                                  |
| latitude          | Latitude                                | float              | -                  | °       |                                                                  |
| altitude          | Altitude                                | float              | -                  | m       |                                                                  |
| terrain           | Terrain type                            | str                | -                  | -       | see [Appendix](#appendix)                                        |
| **economy**       | **Economical parameters**               | **dict**           | -                  | -       |                                                                  |
| d_rate            | Discount rate                           | float              | -                  | -       |                                                                  |
| lifetime          | Project lifetime                        | int                | 20                 | a       |
| currency          | Currency                                | str                | US$                | -       | If other currencies are used conversion rate needs to be applied |
| electricity_price | Electricity price                       | float              | -                  | US$/kWh |                                                                  |
| diesel_price      | Diesel price                            | float              | -                  | US$/l   |
| co2_price         | Average CO2-price over system lifetime  | float              | -                  | US$/t   |                                                                  |
| pv_feed_in_tariff | PV feed-in tariff                       | float              | -                  | US$/kWh |                                                                  |
| wt_feed_in_tariff | Wind turbine feed-in tariff             | float              | -                  | US$/kWh |                                                                  |
| **ecology**       | **Ecological parameters**               | **dict**           | -                  | -       |
| co2_grid          | Specific CO2-emissions power grid       | float              | -                  | kg/kWh  |                                                                  |
| co2_diesel        | Specific CO2-emissions diesel           | float              | 0.2665             | kg/kWh  |                                                                  |
| **blackout**      | **Stable or unstable power grid**       | **bool**           | **False**          | -       | **True: Unstable power grid; False: Stable power grid**          |
| **blackout_data** | **csv-file path with blackout data**    | **str**            | -                  | -       | **csv-file with bool-values for every timestep**                 |
| **feed_in**       | **Feed-in possible**                    | **bool**           | **False**          | -       | **True: Feed-in possible, False: Feed-in not possible**          |
| **weather_data**  | **csv-file path with weather data set** | **str**            | -                  | -       | **Enables off-line usage**                                       |


#### System components
MiGUEL features the following system components. Each component can be added to the Environment by using a different function. The list displays the system components and the functions to add the components to the Environment.

| System component | Function | Type | Status |
|-|-|-|-|
| Load | `.add_load()` | Consumer | ✅ Core |
| Photovoltaic | `.add_pv()` | Generator | ✅ Core |
| Wind turbine | `.add_wind_turbine()` | Generator | ✅ Core |
| Grid | `.add_grid()` | Generator/Consumer | ✅ Core |
| **Electrolyser** | **`.add_electrolyser()`** | **Consumer (H2 Producer)** | **✅ NEW** |
| **H2 Storage** | **`.add_H2_Storage()`** | **H2 Buffer** | **✅ NEW** |
| **Fuel Cell** | **`.add_fuel_cell()`** | **Generator (H2 Consumer)** | **✅ NEW** |
| Battery Storage | `.add_storage()` | Storage | ✅ Core |
| Diesel generator | `.add_diesel_generator()` | Generator | ⚠️ Legacy |

**Legend:**
- ✅ **Core**: Fully supported and actively maintained
- ✅ **NEW**: Recently added hydrogen system components
- ⚠️ **Legacy**: Supported but may require manual integration in GUI

##### Load
The system component load represents the load profile of the subject under review. The load profile can be generated in two different ways. 
1) Reference load profiles: In the course of EnerSHelF standard load profiles for Ghanaian hospitals were created. This daily standard load profile is implemented in the program. Since May 2023 the reference load profiles from the Bundesverband der Energie- und Wasserwirtschaft (BDEW) have been included. The reference load profiles are used in the german dispatch to simulate certain inistitutions. [17] To create a load profile from the reference load profiles, the annual electricity consumption needs to be returned to the function (annual_consumption). The reference load profiles have a 15min-time resolution. 
2) Input via csv-file: If actual measurement data from the subject is available, the data can be returned to the program as a csv-file (load_profile). The csv file must contain two columns with the titles 'time' & 'P [W]'. ',' or ';' are used as separators; for decimal separation '.' or ',' are used depending on the setting. 

| Parameter          | Description                    | dtype | Default | Unit | Comment                                       |
|--------------------|--------------------------------|-------|---------|------|-----------------------------------------------|
| annual_consumption | Annual electricity consumption | float | -       | kWh  | Only for method 1                             |
| profile            | Reference load profile         | str   | -       | -    | Only for method 1                             |
| load_profile       | File path to load profile data | str   | -       | -    | csv-file with load profile, Only for method 2 |

The accuracy of the simulation results increases with the quality of the input data. Using the adjusted standard load profile will provide less accurate results compared to measured data. The library [Load Profile Creator](https://github.com/pdb-94/load_profile_creator) can be used to create load profiles based on the electric inventory of the subject.

If the resolution of the load profile does not match the environment time resolution, the resolution of the load profile will be adjusted by summarizing or filling in the values. If no annual load profile is provided, the load profile will be repeated to create an annual load profile.


##### Photovoltaic
The class Photovoltaic is based on the library [pvlib](https://pvlib-python.readthedocs.io/en/stable/#) [1]. There are three methods implemented to create PV systems:
1) Adding basic system parameters: Simplest way to create PV system with only basic parameters such as nominal power, surface tilt and azimuth, module and inverter power range. The class Photovoltaic will randomly choose a PV module, number of modules and an inverter that matches the parameters.
2) Selecting your modules and inverter: All system parameters such as module, number of modules, inverter, strings per inverter, modules per string, surface tilt and azimuth, ... need to be returned to the function. The modules and inverters featured in pvlib are stored in the [MiGUEL database](#database). 
3) Provide measured PV data: Input of measured PV as a csv-file

| Parameter            | Description                     | dtype    | Default | Unit | Comment                                          |
|----------------------|---------------------------------|----------|---------|------|--------------------------------------------------|
| p_n                  | Nominal power                   | float    | -       | W    |                                                  |
| pv_profile           | File path to pv porduction data | str      | -       | -    | Measured pv data in csv file, Only for method 3  |
| **pv_data**          | **PV system parameters**        | **dict** | -       | -    |                                                  |
| pv_module            | PV module                       | str      | -       | -    | PV module from pvlib database, Only for method 2 |
| inverter             | Inverter                        | str      | -       | -    | Inverter from pvlib database, Only for method 2  |
| modules_per_string   | Modules per string              | int      | -       | -    | Only for method 2                                |
| strings_per_inverter | Strings per inverster           | int      | -       | -    | Only for method 2                                |
| surface_tilt         | PV system tilt angle            | float    | -       | -    |                                                  |
| surface_azimuth      | PV system orientation           | float    | -       | -    | North=0°, East=90°, South=180°, West=270°        |
| min_module_power     | Minimum module power            | float    | -       | W    | Only for method 1                                |
| max_module_power     | Maximum module power            | float    | -       | W    | Only for method 1                                |
| inverter_power_range | Inverter power range            | float    | -       | W    | Only for method 1                                |


pvlib will run the PV simulation based on the selected system parameters. The weather data for the project location is retrieved by the Environment. The data source is [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) hosted by the European Commission.


##### Wind turbine
The class WindTurbine is based on the library [windpowerlib](https://windpowerlib.readthedocs.io/en/stable/index.html) [2]. To add wind turbines to the Environment the [turbine type](https://github.com/wind-python/windpowerlib/blob/master/windpowerlib/oedb/turbine_data.csv) and the turbine height [m] need to be returned. The wind turbines featured in windpowerlib are stored in the [MiGUELdatabase](#database).

| Parameter                | Description      | dtype    | Default | Unit | Comment                                                            |
|--------------------------|------------------|----------|---------|------|--------------------------------------------------------------------|
| **turbine_data**         | **Turbine data** | **dict** | -       | -    |                                                                    |
| turbin_type              | Turbine type     | str      | -       | -    | Turbine name and manufacturer from windpowerlib register (Methd 2) |
| tubine_height            | Hub height       | float    | -       | m    | Method 2                                                           |
| **selection_parameters** |                  | **list** | -       | -    | **Select random turbine iwthin power range**                       |
| p_min                    | Minimal power    | float    | -       | kW   | Method 1                                                           |
| p_max                    | Maximal power    | float    | -       | kW   | Method 1                                                           |

The weather data for the project location is retrieved by the Environment. The data source is [PVGIS](https://re.jrc.ec.europa.eu/pvg_tools/en/) hosted by the European Commission. Inside the class WindTurbine the weather data is processed, so it can be used for the simulation. 

##### Grid
The class grid represents the power grid. The power grid provides electricity to the energy system. Depending on the input of blackout data, a stable or unstable power grid is simulated. The possibility of feed-in is determined in the Environment. The grid is automatically added to the Environment if the parameter grid_connection is set to True. 

##### Diesel Generator
The class DieselGenerator is based on a simplified, self created generator model. The model assumes that in the future generators with low-load capability are used in PV-diesel hybrid systems. In comparison to conventional diesel generators, low-load diesel generators are more fuel efficient and therefore reduce CO2-emissions [3]. The input parameters for diesel generators are displayed in the table below.

| Parameter        | Description                       | dtype | Default | Unit  | Comment |
|------------------|-----------------------------------|-------|---------|-------|---------|
| p_n              | Nominal power                     | float | -       | W     |         |
| fuel_consumption | Fuel consumption at nominal power | float | -       | l     |         |
| fuel_price       | Fuel price                        | float | -       | US$/l |         |


The fuel consumption for the generator is calculated every time step using the following equation. The equation was derived using characteristic values of a 150 kW diesel generator at loads of 0%, 25%, 50%, 75% and 100% [4]. 

*fc(l) = - 1.66360855 x l<sup> 4</sup> +3.96330272 x l<sup> 3</sup> -3.19877674 x l<sup> 2</sup>+1.8990825 x l +0*

*fc = relative fuel consumption [%]* &emsp; *l = relative load [%]*



##### Energy storage
The class Storage represents energy storage systems. The energy storage is represented by a basic model. The input parameters for storage systems are displayed in the table below:

| Parameter   | Description             | dtype | Default | Unit | Comment |
|-------------|-------------------------|-------|---------|------|---------|
| p_n         | Nominal power           | float | -       | W    |         |
| c           | capacity                | float | -       | Wh   |         |
| soc         | Initial state of charge | float | 0.5     | -    |         |
| soc_max     | Maximum state of charge | float | 0.95    | -    |         |
| soc_min     | Minimum state of charge | float | 0.05    | -    |         |
| n_discharge | Discharge efficiency    | float | 0.8     | -    |         |
| n_charge    | Charge efficiency       | float | 0.8     | -    |         |


The energy storage can be either charged or discharged at any time step. The following boundary conditions apply to loading and unloading. The memory can only be discharged to the minimum state of charge and charged to the maximum state of charge. The maximum charging or discharging power corresponds to the nominal power multiplied by the respective efficiency.

##### Electrolyser (NEW)
The class Electrolyser represents a **PEM (Proton Exchange Membrane) electrolyser** that converts electrical energy into hydrogen through water electrolysis. This component enables long-term seasonal energy storage by converting excess renewable energy (especially from solar PV) into hydrogen gas.

**Key Features:**
- Converts electrical power to hydrogen (H2) with efficiency curves
- Operates with minimum load threshold (typically 10% of nominal power)
- Tracks hydrogen production in kg
- Includes investment and operation costs specific to electrolyser technology

**Input Parameters:**

| Parameter | Description | dtype | Default | Unit | Comment |
|-----------|-------------|-------|---------|------|---------|
| p_n | Nominal power | float | - | W | Maximum electrical power consumption |
| c_invest | Investment cost | float | Auto-calculated | US$ | Total investment cost |
| c_invest_n | Specific investment cost | float | 1854.6 | US$/kW | Per kW investment cost |
| c_op_main | Annual O&M cost | float | Auto-calculated | US$/year | Annual operation & maintenance |
| c_op_main_n | Specific O&M cost | float | 18.55 | US$/kW/year | Per kW O&M cost |
| co2_init | Production emissions | float | 36.95 | kg CO2/kW | CO2 emissions from manufacturing |
| life_time | Operational lifetime | int | 20 | years | Expected lifetime |

**Energy Flow:** Excess PV/Wind Power → **Electrolyser** → H2 → H2 Storage

##### H2 Storage (NEW)
The class H2Storage represents a **hydrogen storage tank** that stores hydrogen produced by the electrolyser and provides it to the fuel cell when needed. This enables **seasonal energy storage**, storing summer solar energy as hydrogen for winter use.

**Key Features:**
- Stores hydrogen in kg (mass-based storage)
- Tracks state of charge (SOC) with min/max limits
- Supports both inflow (from electrolyser) and outflow (to fuel cell)
- Enables long-term storage (days to months)

**Input Parameters:**

| Parameter | Description | dtype | Default | Unit | Comment |
|-----------|-------------|-------|---------|------|---------|
| capacity | Total storage capacity | float | - | kg | Maximum hydrogen storage |
| initial_level | Initial H2 level | float | 0.1 * capacity | kg | Starting hydrogen amount (can be fraction if ≤1) |
| soc_min | Minimum state of charge | float | 0.01 | - | Minimum allowed SOC |
| soc_max | Maximum state of charge | float | 0.95 | - | Maximum allowed SOC |
| c_invest | Investment cost | float | Auto-calculated | US$ | Total investment cost |
| c_invest_n | Specific investment cost | float | 534.94 | US$/kg | Per kg storage cost |
| c_op_main_n | Specific O&M cost | float | 0 | US$/kg/year | Per kg O&M cost |
| co2_init | Production emissions | float | 48 | kg CO2/kg | CO2 emissions from manufacturing |
| lifetime | Operational lifetime | int | 25 | years | Expected lifetime |

**Storage Operation:**
- **Charging:** H2 from electrolyser → Storage tank (limited by soc_max)
- **Discharging:** Storage tank → H2 to fuel cell (limited by soc_min)

##### Fuel Cell (NEW)
The class FuelCell represents a **PEM fuel cell** that converts stored hydrogen back into electrical energy. This closes the hydrogen energy cycle and provides dispatchable renewable power when solar/wind generation is insufficient.

**Key Features:**
- Converts hydrogen (H2) to electrical power with efficiency curves
- Variable efficiency based on load (part-load operation)
- Tracks hydrogen consumption in kg
- Provides firm renewable capacity

**Input Parameters:**

| Parameter | Description | dtype | Default | Unit | Comment |
|-----------|-------------|-------|---------|------|---------|
| p_n | Nominal power | float | - | W | Maximum electrical power output |
| c_invest | Investment cost | float | Auto-calculated | US$ | Total investment cost |
| c_invest_n | Specific investment cost | float | 3000 | US$/kW | Per kW investment cost |
| c_op_main | Annual O&M cost | float | Auto-calculated | US$/year | Annual operation & maintenance |
| c_op_main_n | Specific O&M cost | float | 30 | US$/kW/year | Per kW O&M cost |
| co2_init | Production emissions | float | 56 | kg CO2/kW | CO2 emissions from manufacturing |
| life_time | Operational lifetime | int | 10 | years | Expected lifetime (stack replacement) |

**Energy Flow:** H2 Storage → **Fuel Cell** → Electrical Power → Load/Grid

**Hydrogen System Architecture:**

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Excess PV  │ ───▶ │ Electrolyser │ ───▶ │ H2 Storage  │
│   Power     │      │ (e⁻ → H2)    │      │   (tank)    │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │  Fuel Cell  │
                                            │  (H2 → e⁻)  │
                                            └──────┬──────┘
                                                   │
                                                   ▼
                                            ┌─────────────┐
                                            │    Load     │
                                            └─────────────┘
```

**Use Case - Seasonal Storage:**
- **Summer:** High PV generation → Excess power → Electrolyser → H2 Storage
- **Winter:** Low PV generation → H2 Storage → Fuel Cell → Load coverage
- **Result:** Higher renewable energy fraction, reduced grid dependence

### Operator
The simulation process is divided in three steps. 

<p align="center">
  <img src="/documentation/simulation_process.png" alt="drawing" height="100"/>
</p>

The system design is the only time the user needs to interact with the program code. Here the Environment ([create Environment](#environment)) and the system components are created ([system components](#system-components)). The annual simulation and the system evaluation are carried out by the [Operator](#operator).

#### Annual simulation
The energy system type depends on the input parameters and the system components in the energy system. A distinction is made between off-grid systems and on-grid systems. On-grid systems are further divided into stable systems (without blackouts) and unstable systems (with blackouts). Depending on the type of energy system, different dispatch strategies are applied for the annual simulation.

<p align="center">
  <img src="/documentation/dispatch_priorities.svg" alt="drawing" height="400"/>
</p>

RE = Renewable energies &emsp; ES = Energy storage &emsp; DG = Diesel generator

The figure displays the dispatch strategies for all system components. If a system component is not added to the system, this component will be skipped in the dispatch.

### Evaluation

The two key parameters for the system evaluation are the Levelized Cost of Energy (LCOE) in US$/kWh and the CO2-emissions [t] over the system lifetime. The class Evaluation takes the Envrionemnet and the Operator as input parameters.

Note: The specific values for investment, operating and maintenance costs have been partially converted from euros to US$ (27.03.2023). The costs may differ depending on the exchange rate.

#### Levelized Cost of Energy
The LCOE are calculated according to Michael Papapetrou et. al. for every energy supply component [5]. The system LCOE is composed of the individual LCOEs of the system components, which are scaled according to the energetic share. The LCOE are calculated over the whole system lifetime. The LCOE includes the initial investment costs and the operation and maintenance costs. Costs for recycling are neglected in this evaluation. The investment and operation and maintenance cost are based on specific costs from literature values. The specific costs are scaled by the power (energy supply components) or capacity (energy storage).

**Traditional Components:**

| System component | Specific investment cost | Specific annual operation/maintenance cost | Unit    | Source    |
|------------------|--------------------------|--------------------------------------------|---------|-----------|
| PV               | 496                      | 7.55                                       | US$/kW  | [6] [7]   |
| Wind turbine     | 1160                     | 43                                         | US$/kW  | [8] [9]   |
| Diesel generator | 468                      | Investment cost *0.03; 0.021 US$/kWh       | US$/kW  | [10] [11] |
| Battery storage  | 1200                     | 30                                         | US$/kWh | [12]      |

**Hydrogen System Components (NEW):**

| System component | Specific investment cost | Specific annual operation/maintenance cost | Unit    | Source/Assumptions |
|------------------|--------------------------|--------------------------------------------|---------|-------------------|
| Electrolyser     | 1854.6                   | 18.55                                      | US$/kW  | Industry average 2024 |
| H2 Storage       | 534.94                   | 0                                          | US$/kg  | Compressed storage tank |
| Fuel Cell        | 3000                     | 30                                         | US$/kW  | PEM fuel cell stack |

**Note:** Hydrogen component costs are based on current market conditions (2024) and continue to decrease with technology maturation. The electrolyser and fuel cell costs include power electronics and balance of plant.

#### CO2-emissions
The CO2-emissions are evaluated over the system lifetime. Included are the CO2-emissions during the production of the system component and the CO2-emissions emitted during the usage.

**Traditional Components:**

| System component | Specific CO2 emissions production/installation | Unit   | Source |
|------------------|------------------------------------------------|--------|--------|
| PV               | 460                                            | kg/kW  | [13]   |
| Wind turbine     | 200                                            | kg/kW  | [14]   |
| Diesel generator | 265                                            | kg/kW  | [15]   |
| Battery storage  | 103                                            | kg/kWh | [16]   |

**Hydrogen System Components (NEW):**

| System component | Specific CO2 emissions production/installation | Unit   | Source/Assumptions |
|------------------|------------------------------------------------|--------|-------------------|
| Electrolyser     | 36.95                                          | kg/kW  | PEM electrolyser manufacturing |
| H2 Storage       | 48                                             | kg/kg  | Tank production (compressed) |
| Fuel Cell        | 56                                             | kg/kW  | PEM fuel cell stack |

**Operational Emissions:**
- **Renewable Generation (PV, Wind):** 0 kg CO2/kWh (zero emissions during operation)
- **Battery Storage:** 0 kg CO2/kWh (no direct emissions)
- **Hydrogen System:** 0 kg CO2/kWh (when powered by renewable energy)
- **Grid Import:** Variable (co2_grid parameter, typically 0.3-0.8 kg CO2/kWh)
- **Diesel Generator:** 0.2665 kg CO2/kWh (combustion emissions)

**Avoided Emissions:**
The evaluation calculates CO2 emissions avoided by using renewable energy instead of grid electricity or diesel generation.

### Output
MiGUEL provides two types of outputs. The first output is a csv-file with every simulation time step. The csv-files can be used for further research or in depth analysis of the system behaviour. The csv-files do not include the system evaluation. The second output is the pdf-report. The report includes the most important results. The results are displayed graphically and will be explained briefly. 

#### csv-files
The csv-files display the raw data of the annual simulation. The file lists every time step of the simulation, the load and all system components, as well as their generation power.

<p align="center">
  <img src="/documentation/csv_example.png" alt="drawing" height="200"/>
</p>

#### Report
The pdf-Report is automatically created by MiGUEL. It gives an overview of the simulation results and features the system evaluation based on the LCOE and CO2-emissions. The report is structured in the following chapters:

1) Introduction: Brief description of MiGUEL and EnerSHelF
2) Summary: Summary of the most important simulation results and system evaluation
3) Base data: Displays input parameters 
4) Climate data: Solar and wind data from PVGIS at the selected location
5) Energy consumption: Load profile
6) System configuration: Overview of selected system components
7) Dispatch: Annual simulation results
8) Evaluation: System evaluation based on LCOE and CO2-emissions over system lifetime

The report focuses not only on the energetic results of the system evaluation but also on economic and ecologic parameters. This makes the results more comprehensible compared to the csv-files. The pdf-report can be used as a project brochure. 

## Modern Graphical User Interface (2024/2025)
A new **modern GUI** has been developed to support the latest MiGUEL features, including the hydrogen system components. The new GUI uses tkinter (built-in with Python) for minimal dependencies and maximum compatibility.

### Features
- ✅ **Hydrogen System Support**: Full integration of Electrolyser, H2 Storage, and Fuel Cell
- ✅ **Tab-Based Workflow**: Intuitive 7-tab design guides users through system configuration
- ✅ **Real-Time Feedback**: Progress indicators and status updates during simulation
- ✅ **Results Visualization**: Economic, energy, and environmental metrics display
- ✅ **Excel Export**: Detailed timestep data export for further analysis
- ✅ **Minimal Dependencies**: Uses standard library tkinter (no PyQt5 required)

### Quick Start
```bash
# Launch the modern GUI
python launch_gui.py

# Or run directly
python modern_gui.py
```

### Workflow (7 Tabs)
1. **System Setup**: Configure location, time period, economics, grid connection
2. **Load Profile**: Add energy consumption (annual + reference or custom CSV)
3. **Solar PV**: Add photovoltaic systems with tilt/azimuth configuration
4. **Battery Storage**: Add short-term electrical energy storage
5. **Hydrogen System**: Add Electrolyser, H2 Storage, Fuel Cell components
6. **Run Simulation**: Review system overview and execute dispatch calculation
7. **Results**: View LCOE, energy flows, H2 metrics, CO2 emissions, export data

### Example Usage
See detailed guides in:
- `QUICKSTART.md` - Quick start guide with examples
- `GUI_README.md` - Complete user manual
- `gui_example.py` - Working Python examples (without GUI)

### Alternative: Code-Based Approach
For advanced users or automation:
```python
from environment import Environment
from operation import Operator
from evaluation import Evaluation
from datetime import datetime, timedelta

# Create environment
env = Environment(name='My System', time={...}, location={...}, ...)

# Add components
env.add_load(annual_consumption=50000, ref_profile='H0')
env.add_pv(p_n=100000, pv_data={'surface_tilt': 30, 'surface_azimuth': 180})
env.add_electrolyser(p_n=50000)
env.add_H2_Storage(capacity=100)
env.add_fuel_cell(p_n=30000)

# Run simulation
operator = Operator(env=env)
evaluation = Evaluation(env=env, operator=operator)

# Export results
operator.df.to_excel('results.xlsx')
```

## Legacy Graphical User Interface (PyQt5 - 2023)
⚠️ **Note**: The original PyQt5-based GUI is no longer maintained and does not support hydrogen components. Users are encouraged to use the new modern GUI above.

<details>
<summary>Click to expand legacy GUI documentation (for reference only)</summary>

End of June 2023 a graphical user interface (GUI) was implemented into MiGUEL to increase the usability of the tool. With the implementation the entry hurdle is lowered even more. The GUI follows the logical process as described above. The following list gives an overview of the different tabs and a short description of their function:
1) **Get started**: Welcome Screen including a brief overview of MiGUEL and EnerSHelF. Select csv file format
2) **Energy system**: Input mask to  create Environment class.
3) **Weather data**: Displays weather data from PVGIS at selected location.
4) **Load profile**: Input mask to add load profile to Environment.
5) **PV system**: Input mask to add PV systems to Environment.
6) **Wind turbine**: Input mask to add wind turbines to Environment.
7) **Diesel Generator**: Input mask to addd diesel generator to Environment.
8) **Energy storage**: Input mask to add energy storage to Environment.
9) **Dispatch**: Overview of system components. Runs dispatch and system evaluation.
10) **Evaluation**: Overview of system evaluation parameters. Creates outputs.

**Limitations:**
- Does not support hydrogen components (Electrolyser, H2 Storage, Fuel Cell)
- Requires PyQt5 and additional dependencies
- No longer actively maintained

**Migration**: Users should transition to the new modern GUI for full feature support.
</details>


## Database
MiGUEL features a SQLite database in the directory /data/miguel.db. The following tables are included in the database:
| Name | Data sets | Source |
|-|-|-|
|pvlib_cec_module|pvlib cec module parameters||
|pvlib_cec_inverter|pvlib cec inverter parameters||
|windpowerlib_turbine|windpowerlib wind turbine parameters||
|standard_load_profile|standard load profile for Ghanaian hospitals||
|bdew_standard_load_profile|standard load profile of BDEW|[17]|

## Project partners
<p align="center">
  <img src="/documentation/MiGUEL_logo.png" alt="drawing" height="200"/>
</p>
<p align="center">
  <img src="/documentation/th-koeln_white.png" alt="drawing" height="200"/>
   <img src="/documentation/EnerSHelF_logo.png" alt="drawing" height="200"/>
</p>

## Dependencies
For a full list of all dependencies see requirements.txt. This file will ask the user to install the dependencies automtically. 

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

[lcoe](https://pypi.org/project/lcoe/)

[global-land-mask](https://github.com/toddkarin/global-land-mask)

[PyQT5](https://pypi.org/project/PyQt5/)

[geonames](https://pypi.org/project/geonames/)

[geopandas](https://geopandas.org/en/stable/)

[lcoe](https://pypi.org/project/lcoe/)

[plotly](https://pypi.org/project/plotly/)

## References

[1] William F. Holmgren, Clifford W. Hansen, and Mark A. Mikofski. “pvlib python: a python package for modeling solar energy systems.” Journal of Open Source Software, 3(29), 884, (2018). [https://doi.org/10.21105/joss.00884](https://doi.org/10.21105/joss.00884)

[2] Sabine Haas, Uwe Krien, Birgit Schachler, Stickler Bot, kyri-petrou, Velibor Zeli, Kumar Shivam, & Stephen Bosch. (2021). wind-python/windpowerlib: Silent Improvements (v0.2.1). Zenodo. [https://doi.org/10.5281/zenodo.4591809](https://doi.org/10.5281/zenodo.4591809)

[3] PV Magazine; "Low-load generators make photovoltaic diesel applications cleaner and more efficient"; 06. October 2015; online available:
[Niedrig-Last-Generatoren machen Photovoltaik-Diesel-Anwendungen sauberer und effizienter](https://www.pv-magazine.de/2015/10/06/niedrig-last-generatoren-machen-photovoltaik-diesel-anwendungen-sauberer-und-effizienter/)

[4] Generator Source, LLC 1999-2023; Approximate Diesel Fuel Consumption Chart; online available: [https://www.generatorsource.com/Diesel_Fuel_Consumption.aspx](https://www.generatorsource.com/Diesel_Fuel_Consumption.aspx)

[5] Michael Papapetrou, George Kosmadakis, Chapter 9 - Resource, environmental, and economic aspects of SGHE, Editor(s): Alessandro Tamburini, Andrea Cipollina, Giorgio Micale, In Woodhead Publishing Series in Energy, Salinity Gradient Heat Engines, Woodhead Publishing, 2022, Pages 319-353, ISBN 9780081028476, [https://doi.org/10.1016/B978-0-08-102847-6.00006-1](https://doi.org/10.1016/B978-0-08-102847-6.00006-1)

[6] Vartiainen, E, Masson, G, Breyer, C, Moser, D, Román Medina, E. Impact of weighted average cost of capital, capital expenditure, and other parameters on future utility-scale PV levelised cost of electricity. Prog Photovolt Res Appl. 2020; 28: 439– 453. [https://doi.org/10.1002/pip.3189](https://doi.org/10.1002/pip.3189)

[7] Bjarne Steffen, Martin Beuse, Paul Tautorat, Tobias S. Schmidt, Experience Curves for Operations and Maintenance Costs of Renewable Energy Technologies, Joule, Volume 4, Issue 2, 2020, Pages 359-375, ISSN 2542-4351, [https://www.sciencedirect.com/science/article/pii/S2542435119305793](https://doi.org/10.1016/j.joule.2019.11.012)

[8] Lucas Sens, Ulf Neuling, Martin Kaltschmitt, Capital expenditure and levelized cost of electricity of photovoltaic plants and wind turbines – Development by 2050, Renewable Energy, Volume 185, 2022, Pages 525-537, ISSN 0960-1481, [https://www.sciencedirect.com/science/article/pii/S0960148121017626](https://doi.org/10.1016/j.renene.2021.12.042)

[9] Tyler Stehly, Philipp Beiter, and Patrick Duffy, National Renewable Energy Laboratory, 2019 Cost of Wind Energy Review, 2019, [https://www.nrel.gov/docs/fy21osti/78471.pdf9](https://www.nrel.gov/docs/fy21osti/78471.pdf)

[10] James Hamilton, Michael Negnevitsky, Xiaolin Wang, The potential of variable speed diesel application in increasing renewable energy source penetration, Energy Procedia, Volume 160, 2019, Pages 558-565, ISSN 1876-6102, [https://doi.org/10.1016/j.egypro.2019.02.206](https://doi.org/10.1016/j.egypro.2019.02.206)

[11] The EU Global Technical Assistance Facility for Sustainable Energy (EU GTAF), Sustainable Energy Handbook Module 6.1 Simplified Financial Models

[12] National Renewable Energy Laboratory, Utility-Scale Battery Storage, 2023, [https://atb.nrel.gov/electricity/2022/utility-scale_battery_storage](https://atb.nrel.gov/electricity/2022/utility-scale_battery_storage)

[13] Fraunhofer ISE, Photovoltaics and Climate Change, 2020, [https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/ISE-Sustainable-PV-Manufacturing-in-Europe.pdf](https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/ISE-Sustainable-PV-Manufacturing-in-Europe.pdf)


[14] Ozoemena, M., Cheung, W.M. & Hasan, R. Comparative LCA of technology improvement opportunities for a 1.5-MW wind turbine in the context of an onshore wind farm. Clean Techn Environ Policy 20, 173–190 (2018). [https://doi.org/10.1007/s10098-017-1466-2](https://doi.org/10.1007/s10098-017-1466-2)

[15] Friso Klemann, University Utrecht, The environmental impact of cycling 1,600 MWh electricity - A Life Cycle Assessment of a lithium-ion battery from Greener Power Solutions (P. 35)

[16] Hao, H.; Mu, Z.; Jiang, S.; Liu, Z.; Zhao, F. GHG Emissions from the Production of Lithium-Ion Batteries for Electric Vehicles in China. Sustainability 2017, 9, 504. [https://doi.org/10.3390/su9040504](https://doi.org/10.3390/su9040504)

[17] BBDEW Bundesverband der Energie- und Wasserwirtschaft e.V.; Standardlastprofile Strom; [https://www.bdew.de/energie/standardlastprofile-strom/](https://www.bdew.de/energie/standardlastprofile-strom/); 01.01.2017

## Appendix

### Environment - terrain types

| Terrain type                                                                                                     | Roughness length [m] |
|------------------------------------------------------------------------------------------------------------------|----------------------|
| Water surfaces                                                                                                   | 0.0002               |
| Open terrain with smooth surface, e.g., concrete, airport runways, mowed grass                                   | 0.0024               |
| Open agricultural terrain without fences or hedges, possibly with widely scattered houses, very rolling hills    | 0.03                 |
| Agricultural terrain with some houses and 8 meter high hedges at a distance of approx. 1250 meters               | 0.055                |
| Agricultural terrain with many houses, bushes, plants or 8 meter high hedges at a distance of approx. 250 meters | 0.2                  |
| Villages, small towns, agricultural buildings with many or high hedges, woods and very rough and uneven terrain  | 0.4                  |
| Larger cities with tall buildings                                                                                | 0.8                  |
| Large cities, tall buildings, skyscrapers                                                                        | 1.6                  |

