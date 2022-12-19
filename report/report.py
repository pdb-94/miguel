import sys
import os
# import random
# import numpy as np
# import pandas as pd
# import datetime as dt
import matplotlib.pyplot as plt
# from matplotlib.sankey import Sankey
# import folium
# import fpdf as fpdf
import io
# import selenium
import folium
from PIL import Image
from report.pdf import PDF


class Report:
    """
    Class to create results and report
    """
    def __init__(self,
                 environment=None,
                 operator=None):
        self.env = environment
        self.operator = operator
        # Name
        if self.env.name is not None:
            self.name = self.env.name
        else:
            self.name = 'MiGUEL Project'
        # Location
        self.longitude = self.env.location.get('longitude')
        self.latitude = self.env.location.get('latitude')
        self.altitude = self.env.location.get('altitude')
        self.address = self.env.address
        # Time
        self.start = self.env.t_start.strftime('%d/%m/%Y, %H:%M:%S')
        self.end = self.env.t_end.strftime('%d/%m/%Y, %H:%M:%S')
        self.step = self.env.t_step
        # Economy
        self.currency = self.env.currency
        self.lifetime = self.env.lifetime
        self.i_rate = self.env.i_rate
        self.d_rate = self.env.d_rate
        self.co2_price = str(self.env.co2_price).replace('{', '').replace('}', '')
        self.feed_in = self.env.feed_in
        # Ecology
        self.co2_grid = self.env.co2_grid
        self.co2_diesel = self.env.co2_diesel
        # Root path
        self.root = sys.path[1]
        self.report_path = self.root + '/report/'
        self.txt_file_path = self.root + '/report/txt_files/'

        # Create txt-files
        # Chapter 1
        disclaimer = 'This report was created automatically. The calculations and results are based on the data entered. \n\n'
        self.create_txt(file_name='1_disclaimer',
                        text=disclaimer)
        # Chapter 2
        base_data = 'Project name: \t' + self.name + '\n\n' \
                    + 'Time frame: \n' \
                    + 'Start time: \t' + self.start + '\n' \
                    + 'End time: \t' + self.end + '\n' \
                    + 'Time resolution: \t' + str(self.step) + '\n\n' \
                    + 'Economy: \n' \
                    + 'Currency: \t' + self.currency + '\n' \
                    + 'CO2-price: \t' + self.co2_price + ' ' + self.currency + '/kg\n' \
                    + 'Feed-in-tariff: \t' + str(self.feed_in) + ' ' + self.currency + '/kWh\n' \
                    + 'System lifetime: \t' + str(self.lifetime) + ' a\n' \
                    + 'Interest rate: \t' + str(self.i_rate) + '\n' \
                    + 'Discount rate: \t' + str(self.d_rate) + '\n\n' \
                    + 'Ecology: \n' \
                    + 'CO2-factor grid: \t' + str(self.co2_grid) + ' kg/kWh\n' \
                    + 'CO2-factor diesel: \t' + str(self.co2_diesel) + ' kg/kWh\n\n' \
                    + 'Location: \n' \
                    + 'City: \t' + str(self.address[0]) + '\n' \
                    + 'ZIP code: \t' + str(self.address[1]) + '\n' \
                    + 'State: \t' + str(self.address[2]) + '\n' \
                    + 'Country: \t' + str(self.address[3]) + '\n' \
                    + 'Country code: \t' + str(self.address[4]) + '\n' \
                    + 'Latitude: \t' + str(self.latitude) + '°\n' \
                    + 'Longitude: \t' + str(self.longitude) + '°\n'
        self.create_txt(file_name='2_base_data',
                        text=base_data)
        # Chapter 3
        system_config = 'Overview over all system components: \n\n' \
                        + 'Energy supply:'
        self.create_txt(file_name='3_system_configuration',
                        text=system_config)

        system_config_1 = '\nP : \t\t\t\t\t\t\t Nominal power  \n' \
                          + 'i_c: \t\t\t\t\t\t Specific investment cost \n' \
                          + 'I_c: \t\t\t\t\t\t Investment cost \n' \
                          + 'om_c: \t\t Specific operation maintenance cost \n' \
                          + 'OM_c: \t Operation maintenance cost \n' \
                          + 'W: \t\t\t\t\t\t\t Capacity'
        self.create_txt(file_name='3_1_system_configuration',
                        text=system_config_1)

        system_config_2 = '\n Energy Storage:'
        self.create_txt(file_name='3_1_energy_storage',
                        text=system_config_2)
        # Chapter 4
        monthly_data = '\n Renewable energy production from ' + self.start + ' to ' + self.end + '.'
        self.create_txt(file_name='4_re_energy_supply',
                        text=monthly_data)

        # Create plots
        self.columns = []
        for wt in self.env.wind_turbine:
            self.columns.append(wt.name + ': P [W]')
        for pv in self.env.pv:
            self.columns.append(pv.name + ': P [W]')
        self.create_plot(df=self.env.df, columns=self.columns, file_name='re_supply')

        # Report components
        self.map = self.create_map()
        self.create_pdf()

    def create_plot(self, df, columns, file_name):
        """
        :param df: pd.DataFrame
            data to plot
        :param columns: list
            list including df columns
        :param file_name: str
            plot file name
        :return: None
        """
        df[columns].plot(linewidth=0.5)
        plt.ylabel('P [W]')
        plt.xlabel('Time')
        plt.tight_layout()
        plt.savefig(self.report_path + 'pictures/' + file_name + '.png', dpi=300)

    def create_map(self):
        """
        Create folium map and save picture
        :return: folium Map object
            m
        """
        m = folium.Map(location=[self.latitude, self.longitude], zoom_start=13)
        folium.Marker(location=[self.latitude, self.longitude], tooltip='MiGUEL Project').add_to(m)
        img_data = m._to_png(5)
        img = Image.open(io.BytesIO(img_data))
        img.save(self.report_path + 'pictures/' + 'location.png')

        # Delete file
        if os.path.exists('geckodriver.log'):
            os.remove('geckodriver.log')

        return m

    def create_txt(self, file_name: str, text: str):
        """
        Create txt-files
        :param file_name: str
            txt-file name
        :param text: str
            txt-file content
        :return: None
        """
        file = open(self.txt_file_path + file_name + '.txt', 'w')
        file.write(text)

    def create_pdf(self):
        """
        Create pdf-report
        :return: None
        """
        pdf = PDF(title=self.name)
        # Set author
        pdf.set_author('MiGUEL, Paul Bohn')
        # Chapter 1 & 2 - Disclaimer & Base data
        pdf.print_chapter(num=[1, 2],
                          title=['Disclaimer', 'Base data'],
                          file=[self.txt_file_path + '1_disclaimer.txt', self.txt_file_path + '2_base_data.txt'])
        # Include location map
        pdf.image(name=self.report_path + 'pictures/' + '/location.png', w=180)
        # Chapter 3 - System configuration
        pdf.print_chapter(num=[3],
                          title=['System configuration'],
                          file=[self.txt_file_path + '3_system_configuration.txt'])
        # Create Supply table
        supply_header = ['Component',
                         'Name',
                         'P [kW]',
                         'i_c ' + '[' + self.env.currency + '/kW]',
                         'I_c ' + '[' + self.env.currency + ']',
                         'om_c ' + '[' + self.env.currency + '/kW]',
                         'OM_c ' + '[' + self.env.currency + ']']
        # Define table values
        supply_values = [supply_header]
        # Get technical data from env.supply_data
        for row in self.env.supply_data.index:
            supply_values.append(self.env.supply_data.loc[row, :].values.tolist())
        supply_components = [[''], supply_values]
        pdf.create_table(file=pdf, table=supply_components, padding=3)
        pdf.chapter_body(name=self.txt_file_path + '3_1_energy_storage.txt')
        # Get technical data from env.storage_data
        storage_header = ['Component',
                          'Name',
                          'P [kW]',
                          'W [kWh]',
                          'i_c ' + '[' + self.env.currency + '/kWh]',
                          'I_c ' + '[' + self.env.currency + ']',
                          'om_c ' + '[' + self.env.currency + '/kWh]',
                          'OM_c ' + '[' + self.env.currency + ']']
        storage_values = [storage_header]
        for row in self.env.storage_data.index:
            storage_values.append(self.env.storage_data.loc[row, :].values.tolist())
        storage_components = [[''], storage_values]
        pdf.create_table(file=pdf, table=storage_components, padding=3)
        pdf.chapter_body(name=self.txt_file_path + '3_1_system_configuration.txt', size=8)
        # Chapter 4 - Monthly data
        pdf.print_chapter(num=[4], title=['Renewable energy supply'], file=[self.txt_file_path + '4_re_energy_supply.txt'])
        pdf.image(name=self.report_path + 'pictures/' + '/re_supply.png', w=180)
        # Create report
        pdf.output(self.report_path + self.name + '.pdf')
