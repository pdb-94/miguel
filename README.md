Micro Grid User Energy Planning Tool Library (MiGUEL)

Introdcation:
MiGUEL is a python-based, open-source modeling tool for PV-Diesel hybrid systems. The tool was created in the course of the research project Energy-Self-Sufficiency for Health Facilities in Ghana (EnerSHelF). MiGUEL was developed by Paul Bohn (Technische Hochschule Köln). MiGUEL focuses on a low entry barrier and compehensible results. Users need only little porgramming knowledge to run the modeling process. Fruthermore, only little parameters are needed to run the simulation. The tool delivers two types of outputs:
1) csv-files with every simulation step
2) pdf-report with the most important results and a syste evaluation.

Authors and contributors:
The main author is Paul Bohn (Technische Hochschule Köln). Co-author of the project is Silvan Rummeny (Technische Hochschule Köln) who created the first approach within his PhD. Other contributors are Moritz End (Technische Hochschule Köln).

Content and structure:
  
  main: main file to run MiGUEL simulation
  environment: Environment with all basic simulation parameters and systemcomponents
  operation: Carries out the simulation and system evaluation
  report: creates pdf report  
  pv: Modeling the system component PV based on the library pvlib 
  windturbine: Modeling the system component WindTurbine based on the library windpowerlib
  storage: Modeling the system component Storage with a simple storage model  
  dieselgenerator: Modeling the system component DieselGenerator with a simple generator model
  load: Modeling the system component load
  grid: Modeling the system component grid with a simple grid model
  
  



