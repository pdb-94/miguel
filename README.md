# MiGUEL

Micro Grid User Energy Planning Tool Library (MiGUEL)

Purpose: miguel is a user-oriented planning tool library for the implementation of renewable powered micro or mini grids. With the help of this tool, users such as network planners and owners are to be helped in the implementation of renewable-based microgrids.

Author and Contributors: main author is Silvan Rummeny. He created this tool wihtin its PhD "planning, implementation and operation of micro grids on the low and medium voltage level based on renewable energies as a basis for a sustainable and resilient power system". The miguel-part "HEyDU", a load model for Ghanaian Hospitals, is mainly created by Paul Bohn, Moritz End and is adapted and integrated into the miguel library by Silvan Rummeny. TODO: Samers contribution?

Funding and Project-Association: The development of this Tool library at the TH Köln is associated to the PV-Diesel-Project and Project EnerSHelF (www.enershelf.de)

Content and Structure:

    miguel: the MiGUEL library including models, simulation environment and operator and optimizer
    GUI: a graphical user interface for user-friendly control and test of the MiGUEL library
    HEyDU: additional demand response load model for Ghanaian Hospitals, created by Paul Bohn and Moritz End in a student project at the TH Köln. This model can be optionally implemented by the MiGUEL library
    docs: detailled documentation of this repository

Dependencies:

    matplotlib
    numpy
    pandas
    PyQt5
    fpdf
    pvlib
    pandapower
    windpowerlib
    folium

History: First draft version and simulation of a PV-Diesel microgrid was created in MATLAB & MATLAB-Simulink in the PV-Diesel project from 2015 to 2018 supervised by Prof. Eberhard Waffenschmidt at the TH Köln. The micro grid implementation guideline and tool-creation in python was developed in the dissertation of Silvan Rummeny with the title "feasibility, planning and operation of renewable based micro grids as a basis for a resilient power grid", supervised by Prof. Dr.-Ing. Markus Zdrallek from the Bergische Universität Wuppertal and Prof. Dr.-Ing. Eberhard Waffenschmidt. As a continuation to the PV-Diesel project, the developement of the tool in python with special focus on micro grids of Ghanaian health facilities continued in the Project EnerSHelF from 2019 to 2022 supervised by Prof. Thorsten Schneiders. Various student contributions are associated to this work, which is described in further detail in the docs. All contributors of associated student contributions and direct contributions to this repository are listed below.

Direct contributors to this repository:

    Paul Bohn, Technische Hochschule Köln
    Silvan Rummeny, Technische Hochschule Köln
    Moritz End, Technische Hochschule Köln
    Samer Chaaraoui, Hochschule Bonn-Rhein-Sieg

Associated student contributions:

    N. Specht, M. Schifani, J. Wußler, Evaluation of a photovoltaic installation located at the St. Dominic's Hospital in Ghana, 2015
    K. Isa, T. Mast, S. Breker, A. Schmäling, Evaluation of a photovoltaic installation located at the St. Dominic's Hospital in Ghana, 2016
    N. Maitanova, M. Roman, F. Klein, T. Wolf, More sun, less fuel for independent energy supply of the St. Dominic's Hospital in Akwatia, Ghana, 2016
    J. Sanna, F. Rosenau, T. Scheja, F. Binder, Optimum Combination of Photovoltaics and Batteries to Substitute Diesel Generators, IRES 2017, Düsseldorf, 2017
    TODO: Samers Masterarbeit
    J. Kohout, M. Hericks, "Father Franz Kruse Solar Energy Project", Solarenergie für das St. Dominic's Hospital in Akwatia, Ghana, 2018
    [Tobias Linke, Giuliano de Marinis, Markus Heek, Christian Nießen, Johannes Wußler]??
