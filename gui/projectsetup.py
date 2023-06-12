import sys
import gui_func as gui_func
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ProjectSetup(QWidget):
    """
    Tab Welcome Screen
    """
    def __init__(self):
        super().__init__()

        self.screen_geometry = QDesktopWidget().screenGeometry(-1)
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        root = sys.path[1]
        # Logos
        self.miguel_logo = QLabel()
        self.miguel_logo.adjustSize()
        gui_func.create_pixmap(path=root + '/documentation/MiGUEL_logo.png',
                               widget=self.miguel_logo,
                               w=int(self.screen_width/3),
                               h=int(self.screen_height/3))
        self.th_logo = QLabel()
        self.th_logo.adjustSize()
        gui_func.create_pixmap(path=root + '/documentation/th-koeln.png',
                               widget=self.th_logo,
                               w=int(self.screen_width/10),
                               h=int(self.screen_width/10))
        self.enershelf_logo = QLabel()
        self.enershelf_logo.adjustSize()
        gui_func.create_pixmap(path=root + '/documentation/EnerSHelF_logo.png',
                               widget=self.enershelf_logo,
                               w=int(self.screen_width/10),
                               h=int(self.screen_width/10))
        # Description
        description = """The Micro Grid User Energy Planning Tool Library (MiGUEL) was developed in the course of the project Energy-Self-Sufficiency for Health Facilities in Ghana (EnerSHelF). EnerSHelF was funded by the German Federal Ministry for Education and Research from June 2019 until March 2023. The main author of MiGUEL is Paul Bohn (Technische Hochschule Köln) other contributors were Moritz End and Silvan Rummeny. The development was supervised by Prof. Dr. Thorsten Schneiders (Cologne Institute for Renewable Energies, Technische Hochschule Köln). MiGUEL is a python-based, open source tool to model, simulate and analyse PV-diesel hybrid systems. MiGUEL aims to have a low entry barrier and understandable results. Neither is the user required to deliver datasets to the program nor are programming skills required. Only basic parameters are needed to carry out the simulation in the basic form. As results MiGUEL delivers both csv-files with every simulation time step as well as a pdf-report with an overview of the most important results as well as the system evaluation."""
        font = QFont('Calibri', 13)
        self.description = QLabel(description)
        self.description.setAlignment(Qt.AlignJustify)
        self.description.setFont(font)
        self.description.setWordWrap(True)

        # Set up Layout
        self.layout = QGridLayout()
        self.layout.addWidget(self.miguel_logo, 0, 0, 1, 1, Qt.AlignLeft)
        self.layout.addWidget(self.description, 1, 0, 1, 2)
        self.layout.addWidget(self.th_logo, 2, 0, Qt.AlignLeft)
        self.layout.addWidget(self.enershelf_logo, 2, 1, Qt.AlignLeft)
        self.setLayout(self.layout)



