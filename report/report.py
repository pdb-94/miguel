import sys
import os
import calendar
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
import pandas as pd
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
        # Weather data
        self.weather_data = self.env.weather_data
        self.input_parameter = self.create_input_parameter()
        # Root path
        self.root = sys.path[1]
        self.report_path = self.root + '/report/'
        self.txt_file_path = self.root + '/report/txt_files/'
        # PDF
        self.pdf = PDF(title=self.name)
        self.create_pdf()

    def create_input_parameter(self):
        """
        Create DataFrame with input Parameters
        :return: pd.DataFrame
            df with input parameters
        """
        env = self.env
        data = {'Parameter': ['Project name', 'Start time', 'End time', 'Time resolution',
                              'Currency', 'Electricity price [' + env.currency + '/kWh]',
                              'CO2 price [' + env.currency + '/t]',
                              'Feed-in tariff [' + env.currency + '/kWh]', 'System lifetime [a]', 'Interest rate',
                              'Discount rate',
                              'CO2 equivalent Diesel [kg/kWh]', 'CO2 equivalent Grid [kg/kWh]',
                              'City', 'ZIP Code', 'State', 'Country', 'Country Code', 'Latitude [°]', 'Longitude [°]'],
                'Values': [env.name, env.t_start, env.t_end, env.t_step, env.currency, env.electricity_price,
                           env.co2_price, env.feed_in, env.lifetime, env.i_rate, env.d_rate, env.co2_diesel,
                           env.co2_grid, env.address[0], env.address[1], env.address[2], env.address[3],
                           env.address[4], env.latitude, env.longitude]}
        df = pd.DataFrame.from_dict(data=data)

        return df

    def create_plot(self, df: pd.DataFrame, columns: list, file_name: str, x_label: str = None, y_label: str = None):
        """
        :param x_label: str
            x-label text
        :param df: pd.DataFrame
            data to plot
        :param columns: list
            list including df columns
        :param file_name: str
            plot file name
        :param x_label: str
            x-label text
        :param y_label: str
            y-label text
        :return: None
        """
        df[columns].plot(linewidth=0.5)
        plt.ylabel(y_label)
        plt.xlabel(x_label)
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
        # Set author
        self.pdf.set_author('MiGUEL, Paul Bohn')
        self.pdf.add_page()
        self.pdf.chapter_title(label='Energy system: ' + self.name + '\n\n', size=14)
        # Create Chapter
        self.introduction_summary()
        self.base_data()
        self.climate_data()
        self.energy_consumption()
        self.energy_supply()
        # Create report
        self.pdf.output(self.report_path + self.name + '.pdf')

    def introduction_summary(self):
        """
        Create Introduction and Summary
        :return: None
        """
        # Introduction - contains disclaimer
        introduction = "The report '" + self.name + \
                       "' was created automatically using the Micro Grid User Energy Planning Tool Library (MiGUEL). " \
                       " The calculation results are based on the user's input data. The input data is supplemented " \
                       "through weather data from the Photovoltaic Geographical Information System (PVGIS). \n\n"

        self.create_txt(file_name='introduction',
                        text=introduction)
        # Summary - contains most important results
        summary = "The most important findings are displayed in the upcoming chapter."
        self.create_txt(file_name='summary',
                        text=summary)
        self.pdf.print_chapter(chapter_type=[False, False],
                               title=['Introduction', 'Summary'],
                               file=[self.txt_file_path + 'introduction.txt',
                                     self.txt_file_path + 'summary.txt'])

    def base_data(self):
        """
        Create chapter 1 - Base data
        :return: None
        """
        # Create txt-file
        base_data = 'The following parameters are provided through the user. If no values were entered default values will be used.' \
                    ' The chapter functions as an overview of the base parameters. \n\n'
        self.create_txt(file_name='1_base_data',
                        text=base_data)
        # Create map
        self.create_map()
        # Create chapter
        self.pdf.print_chapter(chapter_type=[True],
                               title=['1 Base data'],
                               file=[self.txt_file_path + '1_base_data.txt'])
        input_header = ['Parameter', 'Values']
        input_values = [input_header]
        for row in self.input_parameter.index:
            input_values.append(self.input_parameter.loc[row, :].values.tolist())
        input_data = [[''], input_values]
        self.pdf.create_table(file=self.pdf,
                              table=input_data,
                              padding=2)
        self.pdf.chapter_body(name=self.txt_file_path + 'default/line_break.txt', size=10)
        # Include location map
        self.pdf.image(name=self.report_path + 'pictures/' + '/location.png', w=180)

    def climate_data(self):
        """
        Create chapter 2 - Weather data
        :return: None
        """
        # Create txt-file
        weather_data_2 = 'In the upcoming chapter displays climate conditions at the selected location. ' \
                         'The provided data originates from the Photovoltaic Geographical Information System (PVGIS) hosted by the European Commission.' \
                         'The data is created from a typical meteorological year (TMY). For this purpose, the typical meteorological ' \
                         'month in the period 2005-2016 is selected. ' \
                         'The table shows the month and the years where the data is taken from.  \n\n'
        self.create_txt(file_name='2_weather_data',
                        text=weather_data_2)
        weather_data_2_1 = 'The plot shows the global horizontal irradiation (GHI), direct normal irradiation (DNI) ' \
                           'and the direct horizontal irradiation (DHI) at the selected location in an hourly ' \
                           'resolution based on the TMY. The table shows the average monthly GHI, DNI and DHI values.\n\n'
        self.create_txt(file_name='2_1_solar_radiation',
                        text=weather_data_2_1)
        weather_data_2_2 = 'The plot shows the wind speed at 10m height in hourly-resolution. ' \
                           'The table shows the monthly average wind speed and direction. \n\n'
        self.create_txt(file_name='2_2_wind_speed',
                        text=weather_data_2_2)
        # Create plots
        self.create_plot(df=self.weather_data[0], columns=['ghi', 'dni', 'dhi'], file_name='solar_data',
                         y_label='P [W/m²]')
        # Wind speed
        self.create_plot(df=self.weather_data[0], columns=['wind_speed'], file_name='wind_data',
                         y_label='v [m/s]')
        # Print chapter 2
        self.pdf.print_chapter(chapter_type=[True],
                               title=['2 Climate data'],
                               file=[self.txt_file_path + '2_weather_data.txt'])
        tmy_header = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                      'November', 'December']
        tmy_values = [tmy_header]
        tmy_year = []
        for i in range(len(self.weather_data[1])):
            tmy_year.append(self.weather_data[1][i]['year'])
        tmy_values.append(tmy_year)
        tmy_data = [[''], tmy_values]
        self.pdf.create_table(file=self.pdf,
                              table=tmy_data,
                              padding=2)
        self.pdf.chapter_body(name=self.txt_file_path + 'default/line_break.txt', size=10)
        # 2.1 Solar irradiation
        self.pdf.print_chapter(chapter_type=[False],
                               title=['2.1 Solar irradiation'],
                               file=[self.txt_file_path + '2_1_solar_radiation.txt'])
        # Plot solar irradiation
        self.pdf.image(name=self.report_path + 'pictures/' + '/solar_data.png', w=140, x=35)
        # Monthly solar data Table
        solar_data_header = ['Month', 'Avg. GHI [W/m²]', 'Avg. DNI [W/m²]', 'Avg. DHI [W/m²]']
        solar_values = [solar_data_header]
        for row in self.env.monthly_weather_data.index:
            data = []
            data.append(calendar.month_name[row])
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 2], 3))
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 3], 3))
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 4], 3))
            solar_values.append(data)
        solar_data = [[''], solar_values]
        self.pdf.create_table(file=self.pdf,
                              table=solar_data,
                              padding=2)
        self.pdf.chapter_body(name=self.txt_file_path + 'default/line_break.txt', size=10)
        # 2.2 Wind speed
        self.pdf.print_chapter(chapter_type=[False],
                               title=['2.2 Wind speed'],
                               file=[self.txt_file_path + '2_2_wind_speed.txt'])
        self.pdf.image(name=self.report_path + 'pictures/' + '/wind_data.png', w=140, x=35)
        # Monthly weather data Table
        wind_data_header = ['Month', 'Avg. Wind Speed [m/s]', 'Avg. Wind direction [°]']
        wind_values = [wind_data_header]
        for row in self.env.monthly_weather_data.index:
            data = []
            data.append(calendar.month_name[row])
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 6], 3))
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 7], 3))
            wind_values.append(data)
        wind_data = [[''], wind_values]
        self.pdf.create_table(file=self.pdf,
                              table=wind_data,
                              padding=2)

    def energy_consumption(self):
        """
        Create chapter 3 - Energy consumption
        :return: None
        """
        # Create txt-file
        energy_consumption_3 = 'The energy consumption gives an overview of the systems load profile, ' \
                               'the total energy consumption, energy cost and CO2-emissions.\n\n'
        self.create_txt(file_name='3_energy_consumption',
                        text=energy_consumption_3)
        energy_consumption_3_1 = 'The given load profile is displayed below. ' \
                                 'The load profile is repeated to fill in the period under consideration.  \n'
        self.create_txt(file_name='3_1_energy_consumption',
                        text=energy_consumption_3_1)
        energy_data_3_1 = '\nParameters:\nTotal energy consumption from ' + str(self.env.t_start) + ' to ' \
                          + str(self.env.t_end) + ': ' + str(round(self.operator.energy_consumption / 1000, 3)) \
                          + ' kWh. \n' + 'Peak load: ' + str(round(self.operator.peak_load / 1000, 3)) + ' kW.'
        self.create_txt(file_name='3_1_energy_data',
                        text=energy_data_3_1)
        # Create plot
        self.create_plot(df=self.env.load[0].load_profile, columns=['P [W]'], file_name='load_profile',
                         x_label='Time', y_label='P [W]')
        # Print Chapters
        self.pdf.print_chapter(chapter_type=[True],
                               title=['3 Energy consumption'],
                               file=[self.txt_file_path + '3_energy_consumption.txt'])
        self.pdf.print_chapter(chapter_type=[False],
                               title=['3.1 Load profile'],
                               file=[self.txt_file_path + '3_1_energy_consumption.txt'],
                               size=10)
        self.pdf.image(name=self.report_path + 'pictures/' + 'load_profile.png', w=150, x=30)
        self.pdf.chapter_body(name=self.txt_file_path + '3_1_energy_data.txt', size=10)

    def energy_supply(self):
        """
        Create chapter - System configuration
        :return:
        """
        system_config_4 = 'The chapter system configuration contains detailed information about the selected system components.' \
                          ' This includes parameters such as nominal power/capacity, specific investment and operation and' \
                          'maintenance cost (chapter 3.1). Furthermore the renewable energy energy supply is displayed (chapter 3.2).\n\n '
        self.create_txt(file_name='4_system_configuration',
                        text=system_config_4)
        system_config_4_1_supply = 'The upcoming chapters list all system components of the energy system. ' \
                                   'The system components are split up into the categories energy supply and energy storage. \n\n' \
                                   'Energy supply:'
        self.create_txt(file_name='4_1_system_components',
                        text=system_config_4_1_supply)
        system_config_4_1_storage = '\nEnergy Storage:'
        self.create_txt(file_name='4_1_energy_storage',
                        text=system_config_4_1_storage)
        system_config_4_1_description = '\nP : \t\t\t\t\t\t\t Nominal power  \n' \
                                        + 'i_c: \t\t\t\t\t\t Specific investment cost \n' \
                                        + 'I_c: \t\t\t\t\t\t Investment cost \n' \
                                        + 'om_c: \t\t Specific operation maintenance cost \n' \
                                        + 'OM_c: \t Operation maintenance cost \n' \
                                        + 'W: \t\t\t\t\t\t\t Capacity\n\n'
        self.create_txt(file_name='4_1_system_configuration_description',
                        text=system_config_4_1_description)
        # 4.2 RE Supply - contains annual RE production with system configurations
        monthly_data = 'Renewable energy production from ' + str(self.env.t_start) + ' to ' + str(self.env.t_end) + '.'
        self.create_txt(file_name='4_2_re_energy_supply',
                        text=monthly_data)
        # Create Plot
        columns = []
        for wt in self.env.wind_turbine:
            columns.append(wt.name + ': P [W]')
        for pv in self.env.pv:
            columns.append(pv.name + ': P [W]')
        self.create_plot(df=self.env.df, columns=columns, file_name='re_supply', x_label='Time', y_label='P [W/]')
        self.pdf.print_chapter(chapter_type=[True],
                               title=['4 System configuration'],
                               file=[self.txt_file_path + '4_system_configuration.txt'])
        self.pdf.print_chapter(chapter_type=[False],
                               title=['4.1 System components'],
                               file=[self.txt_file_path + '4_1_system_components.txt'],
                               size=10)
        # Create Supply table
        supply_header = ['Component', 'Name', 'P [kW]', 'i_c ' + '[' + self.env.currency + '/kW]',
                         'I_c ' + '[' + self.env.currency + ']', 'om_c ' + '[' + self.env.currency + '/kW]',
                         'OM_c ' + '[' + self.env.currency + '/a]']
        # Define table values
        supply_values = [supply_header]
        # Get technical data from env.supply_data
        for row in self.env.supply_data.index:
            supply_values.append(self.env.supply_data.loc[row, :].values.tolist())
        supply_components = [[''], supply_values]
        self.pdf.create_table(file=self.pdf, table=supply_components, padding=3)
        self.pdf.chapter_body(name=self.txt_file_path + '4_1_energy_storage.txt',
                              size=10)
        # Get technical data from env.storage_data
        storage_header = ['Component', 'Name', 'P [kW]', 'W [kWh]', 'i_c ' + '[' + self.env.currency + '/kWh]',
                          'I_c ' + '[' + self.env.currency + ']', 'om_c ' + '[' + self.env.currency + '/kWh]',
                          'OM_c ' + '[' + self.env.currency + '/a]']
        storage_values = [storage_header]
        for row in self.env.storage_data.index:
            storage_values.append(self.env.storage_data.loc[row, :].values.tolist())
        storage_components = [[''], storage_values]
        self.pdf.create_table(file=self.pdf, table=storage_components, padding=3)
        self.pdf.chapter_body(name=self.txt_file_path + '4_1_system_configuration_description.txt', size=8)
        # Chapter 4 - Monthly data
        self.pdf.print_chapter(chapter_type=[False],
                               title=['3.2 Renewable energy supply'],
                               file=[self.txt_file_path + '4_2_re_energy_supply.txt'],
                               size=10)
        self.pdf.image(name=self.report_path + 'pictures/' + '/re_supply.png', w=150, x=30)
