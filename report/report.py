import sys
import os
import calendar
# import random
# import numpy as np
# import datetime as dt
import matplotlib.pyplot as plt
import io
import folium
import pandas as pd
from PIL import Image
import selenium
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
        self.evaluation_df = self.create_evaluation_parameter()
        # Root path
        self.root = sys.path[1]
        self.report_path = self.root + '/report/'
        self.txt_file_path = self.root + '/report/txt_files/'
        # PDF
        self.pdf = PDF(title=self.name)
        self.create_pdf()

    def create_pdf(self):
        """
        Create pdf-report
        :return: None
        """
        # Set author
        self.pdf.set_author('Paul Bohn')
        self.pdf.set_creator('Micro Grid User Energy Planning Tool Library')
        self.pdf.set_keywords('EnerSHelF, Renewable Energy, Energy systems, MiGUEL, PV-Diesel-Hybrid systems')
        self.pdf.add_page()
        self.pdf.chapter_title(label='Energy system: ' + self.name + '\n\n', size=14)
        # Create Chapters
        self.introduction_summary()
        self.base_data()
        self.climate_data()
        self.energy_consumption()
        self.energy_supply()
        self.dispatch()
        self.evaluation()
        # Create report
        self.pdf.output(self.report_path + self.name + '.pdf')

    '''Functions to create chapters'''
    def introduction_summary(self):
        """
        Create Introduction and Summary
        :return: None
        """
        # Retrieve energy values from operator
        total_energy = int(self.operator.energy_data[0])
        energy_parameters = self.retrieve_energy_parameters()
        pv_energy = energy_parameters[0]
        pv_percentage = round(pv_energy / total_energy * 100, 2)
        wt_energy = energy_parameters[1]
        wt_percentage = round(wt_energy / total_energy * 100, 2)
        grid_energy = energy_parameters[2]
        grid_percentage = round(grid_energy / total_energy * 100, 2)
        dg_energy = energy_parameters[3]
        dg_percentage = round(dg_energy / total_energy * 100, 2)
        es_charge = energy_parameters[4]
        es_discharge = energy_parameters[5]
        # Write chapter depending if energy consumption is met
        if self.operator.system_covered is True:
            system_status = "The selected system is considered an '" + self.env.system + \
                            "'. With the selected system configuration, the energy demand of " + str(total_energy) + \
                            " kWh is covered."
        else:
            system_status = "The selected system is considered an '" + self.env.system + \
                            "'. With the selected system configuration, the energy demand of " + str(total_energy) + \
                            " kWh is not covered. The maximum remaining power to be covered equals " + \
                            str(self.operator.power_sink_max) + \
                            "W. The table shows the time stamps and the power to be covered. "
        summary = system_status + "The PV system(s) account for " + str(pv_percentage) + "% (" + str(pv_energy) + \
                  " kWh); The wind turbine(s) account for " + str(wt_percentage) + "% (" + str(wt_energy) + \
                  " kWh); The grid accounts  " + str(grid_percentage) + "% (" + str(grid_energy) + \
                  " kWh); The diesel generator(s) account for " + str(dg_percentage) + "% (" + \
                  str(dg_energy) + " kWh) of the total energy consumption. The energy storage(s) provide " + \
                  str(abs(es_discharge)) + " kWh and are charged with " + str(abs(es_charge)) + " kWh.\n\n"
        self.create_txt(file_name='summary',
                        text=summary)
        self.pdf.print_chapter(chapter_type=[False, False],
                               title=['Introduction', 'Summary'],
                               file=[self.txt_file_path + 'default/introduction.txt',
                                     self.txt_file_path + 'summary.txt'])
        # if self.operator.system_covered is not True:
        #     summary_header = ['Time stamps', 'P [W]']
        #     # Define table values
        #     summary_values = [summary_header]
        #     # Get technical data from env.supply_data
        #     for row in self.operator.power_sink.index:
        #         data = [row]
        #         data.append(self.operator.power_sink.loc[row, 'P [W]'])
        #         summary_values.append(data)
        #     summary_data = [[''], summary_values]
        #     self.pdf.create_table(file=self.pdf,
        #                           table=summary_data,
        #                           padding=1.5)
        # Create evaluation table
        evaluation_header = ['Component',
                             'Energy production [kWh]',
                             'Investment Cost [' + self.env.currency + ']',
                             'LCOE [' + self.env.currency + '/kWh]',
                             'CO2-emissions [t]']
        evaluation_values = [evaluation_header]
        for row in self.evaluation_df.index:
            data = [row]
            data.append(round(self.evaluation_df.loc[row, 'Energy production [kWh]'], 0))
            data.append(round(self.evaluation_df.loc[row, 'Investment Cost [' + self.env.currency + ']'], 0))
            data.append(round(self.evaluation_df.loc[row, 'LCOE [' + self.env.currency + '/kWh]'], 2))
            data.append(round(self.evaluation_df.loc[row, 'CO2-emissions [t]'], 3))
            evaluation_values.append(data)
        evaluation_data = [[''], evaluation_values]
        self.pdf.create_table(file=self.pdf,
                              table=evaluation_data,
                              padding=2)

    def base_data(self):
        """
        Create chapter 1 - Base data
        :return: None
        TODO: Add system type (grid connection/blackout) to input data
        """
        # Create map
        self.create_map()
        # Create chapter
        self.pdf.print_chapter(chapter_type=[True],
                               title=['1 Base data'],
                               file=[self.txt_file_path + 'default/1_base_data.txt'])
        input_header = ['Parameter', 'Values']
        input_values = [input_header]
        for row in self.input_parameter.index:
            input_values.append(self.input_parameter.loc[row, :].values.tolist())
        input_data = [[''], input_values]
        self.pdf.create_table(file=self.pdf,
                              table=input_data,
                              padding=2)
        self.pdf.ln(h=10)
        # Include location map
        self.pdf.image(name=self.report_path + 'pictures/' + '/location.png', w=160)

    def climate_data(self):
        """
        Create chapter 2 - Weather data
        :return: None
        """
        # Create plots
        self.create_plot(df=self.weather_data[0], columns=['ghi', 'dni', 'dhi'], file_name='solar_data',
                         y_label='P [W/m²]')
        # Wind speed
        self.create_plot(df=self.weather_data[0], columns=['wind_speed'], file_name='wind_data',
                         y_label='v [m/s]')
        # Print chapter 2
        self.pdf.print_chapter(chapter_type=[True],
                               title=['2 Climate data'],
                               file=[self.txt_file_path + 'default/2_weather_data.txt'])
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
                              padding=1.5)
        self.pdf.ln(h=10)
        # 2.1 Solar irradiation
        self.pdf.print_chapter(chapter_type=[False],
                               title=['2.1 Solar irradiation'],
                               file=[self.txt_file_path + 'default/2_1_solar_radiation.txt'])
        # Plot solar irradiation
        self.pdf.image(name=self.report_path + 'pictures/' + '/solar_data.png', w=140, x=35)
        # Monthly solar data Table
        solar_data_header = ['Month', 'Avg. GHI [W/m²]', 'Avg. DNI [W/m²]', 'Avg. DHI [W/m²]']
        solar_values = [solar_data_header]
        for row in self.env.monthly_weather_data.index:
            data = [calendar.month_name[row]]
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 2], 3))
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 3], 3))
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 4], 3))
            solar_values.append(data)
        solar_data = [[''], solar_values]
        self.pdf.create_table(file=self.pdf,
                              table=solar_data,
                              padding=1.5)
        self.pdf.ln(h=10)
        # 2.2 Wind speed
        self.pdf.print_chapter(chapter_type=[False],
                               title=['2.2 Wind speed'],
                               file=[self.txt_file_path + 'default/2_2_wind_speed.txt'])
        self.pdf.image(name=self.report_path + 'pictures/' + '/wind_data.png', w=140, x=35)
        # Monthly weather data Table
        wind_data_header = ['Month', 'Avg. Wind Speed [m/s]', 'Avg. Wind direction [°]']
        wind_values = [wind_data_header]
        for row in self.env.monthly_weather_data.index:
            data = [calendar.month_name[row]]
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 6], 3))
            data.append(round(self.env.monthly_weather_data.iloc[row - 1, 7], 3))
            wind_values.append(data)
        wind_data = [[''], wind_values]
        self.pdf.create_table(file=self.pdf,
                              table=wind_data,
                              padding=1.5)
        wind_speed_max = round(self.env.monthly_weather_data['wind_speed'].max(), 3)
        self.pdf.ln(h=10)
        month_max = self.env.monthly_weather_data['wind_speed'].idxmax()
        month_max = calendar.month_name[month_max]
        wind_speed_average = round(self.env.monthly_weather_data['wind_speed'].mean(), 3)
        wind_direction_average = round(self.env.monthly_weather_data['wind_direction'].mean(), 3)
        wind_table_text = 'The main wind direction is ' + str(
            wind_direction_average) + '°. The annual average wind speed is ' \
                          + str(wind_speed_average) + ' m/s. The highest monthly wind speed occurs in ' \
                          + month_max + ' and is ' + str(wind_speed_max) + ' m/s.'
        self.create_txt(file_name='2_2_table_description',
                        text=wind_table_text)
        self.pdf.chapter_body(name=self.txt_file_path + '2_2_table_description.txt', size=10)

    def energy_consumption(self):
        """
        Create chapter 3 - Energy consumption
        :return: None
        """
        # Create plot
        self.create_plot(df=self.env.load[0].load_profile, columns=['P [W]'], file_name='load_profile',
                         x_label='Time', y_label='P [kW]', factor=1000)
        # Print Chapters
        self.pdf.print_chapter(chapter_type=[True],
                               title=['3 Energy consumption'],
                               file=[self.txt_file_path + 'default/3_energy_consumption.txt'])
        self.pdf.image(name=self.report_path + 'pictures/' + 'load_profile.png', w=150, x=30)
        # Create table with reference parameters
        energy_con_header = ['', 'Power Grid', 'Diesel Generator']

        total_energy_con = ['Energy consumption [kWh]',
                            int(self.operator.energy_consumption / 1000),
                            int(self.operator.energy_consumption / 1000)]
        peak_load = ['Peak load [kW]',
                     int(self.operator.peak_load / 1000),
                     int(self.operator.peak_load / 1000)]
        cost = ['Energy cost [' + self.env.currency + ']',
                int(self.operator.energy_consumption / 1000 * self.env.electricity_price),
                int(self.operator.energy_consumption / 1000 * self.env.diesel_price)]
        co2_emission = ['CO2 emissions [t]',
                        round(self.operator.energy_consumption / 1e6 * self.env.co2_grid, 3),
                        round(self.operator.energy_consumption / 1e6 * self.env.co2_diesel, 3)]
        energy_con_values = [energy_con_header, total_energy_con, peak_load, cost, co2_emission]
        energy_con_data = [[''], energy_con_values]
        self.pdf.create_table(file=self.pdf,
                              table=energy_con_data,
                              padding=1.5)
        self.pdf.ln(h=10)

    def energy_supply(self):
        """
        Create chapter - System configuration
        :return: None
        TODO: Add grid connection and blackout data
        """
        # 4.2 RE Supply - contains annual RE production with system configurations
        # Create Plot
        columns = []
        wt_energy = 0
        pv_energy = 0
        for i in range(len(self.env.wind_turbine)):
            columns.append(self.env.wind_turbine[i].name + ': P [W]')
            wt_energy += self.env.df['WT_' + str(i + 1) + ': P [W]'].sum()
        for i in range(len(self.env.pv)):
            columns.append(self.env.pv[i].name + ': P [W]')
            pv_energy += self.env.df['PV_' + str(i + 1) + ': P [W]'].sum()
        self.create_plot(df=self.env.df, columns=columns, file_name='re_supply', x_label='Time', y_label='P [kW]',
                         factor=1000)
        re_production = 'The plot shows the total wind power and PV output during the period from ' \
                        + str(self.env.t_start) + ' to ' + str(self.env.t_end) + ' in a ' \
                        + str(self.env.t_step) + ' resolution: \n' \
                        + 'Photovoltaic: ' + str(round((pv_energy / 1000), 0)) + ' kWh \n' \
                        + 'Wind turbine: ' + str(round((wt_energy / 1000), 0)) + ' kWh'
        self.create_txt(file_name='4_2_re_energy_supply',
                        text=re_production)
        self.pdf.print_chapter(chapter_type=[True],
                               title=['4 System configuration'],
                               file=[self.txt_file_path + 'default/4_system_configuration.txt'])
        self.pdf.print_chapter(chapter_type=[False],
                               title=['4.1 System components'],
                               file=[self.txt_file_path + 'default/4_1_system_components.txt'],
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
        self.pdf.create_table(file=self.pdf, table=supply_components, padding=2)
        self.pdf.chapter_body(name=self.txt_file_path + 'default/4_1_energy_storage.txt',
                              size=10)
        # Get technical data from env.storage_data
        storage_header = ['Component', 'Name', 'P [kW]', 'W [kWh]', 'i_c ' + '[' + self.env.currency + '/kWh]',
                          'I_c ' + '[' + self.env.currency + ']', 'om_c ' + '[' + self.env.currency + '/kWh]',
                          'OM_c ' + '[' + self.env.currency + '/a]']
        storage_values = [storage_header]
        for row in self.env.storage_data.index:
            storage_values.append(self.env.storage_data.loc[row, :].values.tolist())
        storage_components = [[''], storage_values]
        self.pdf.create_table(file=self.pdf, table=storage_components, padding=2)
        self.pdf.chapter_body(name=self.txt_file_path + 'default/4_1_system_configuration_description.txt', size=8)
        # Chapter 4 - Monthly data
        self.pdf.print_chapter(chapter_type=[False],
                               title=['4.2 Renewable energy supply'],
                               file=[self.txt_file_path + '4_2_re_energy_supply.txt'],
                               size=10)
        self.pdf.image(name=self.report_path + 'pictures/' + '/re_supply.png', w=150, x=30)

    def dispatch(self):
        """
        Create chapter 5 - dispatch
        :return: None
        """
        env = self.env
        dispatch_5 = "This chapter presents the dispatch of the power system. The system is considered a '" \
                     + self.env.system + "'. The plot below shows the load profile and the power the system components supply in kW. " \
                     + "Energy storage systems can both consume and supply power. Negative values correspond to " \
                     + "power output (power source), positive loads to power input (power sink).\n\n "
        self.create_txt(file_name='5_dispatch', text=dispatch_5)
        self.pdf.print_chapter(chapter_type=[True],
                               title=['5 Dispatch'],
                               file=[self.txt_file_path + '5_dispatch.txt'],
                               size=10)
        # Create Dispatch plot
        columns = ['Load [W]']
        for pv in env.pv:
            columns.append(pv.name + ' [W]')
        for wt in env.wind_turbine:
            columns.append(wt.name + ' [W]')
        for es in env.storage:
            columns.append(es.name + ' [W]')
        for grid in env.grid:
            columns.append(grid.name + ' [W]')
        for dg in env.diesel_generator:
            columns.append(dg.name + ' [W]')
        self.create_plot(df=self.operator.df, columns=columns, file_name='dispatch', y_label='P [W]')
        self.pdf.image(name=self.report_path + 'pictures/' + '/dispatch.png', w=150, x=30)

    def evaluation(self):
        """
        Chapter 6 - evaluation
        :return: None
        """
        self.pdf.print_chapter(chapter_type=[True],
                               title=['6 Evaluation'],
                               file=[self.txt_file_path + 'default/6_evaluation.txt'],
                               size=10)
        economic_6_1 = ""
        self.create_txt(file_name='6_1_economic_evaluation', text=economic_6_1)
        self.pdf.print_chapter(chapter_type=[False],
                               title=['6.1 Economic evaluation'],
                               file=[self.txt_file_path + '6_1_economic_evaluation.txt'],
                               size=10)

    '''Functions to create chapter data'''
    def create_input_parameter(self):
        """
        Create DataFrame with input Parameters
        :return: pd.DataFrame
            df with input parameters
        """
        env = self.env
        data = {'Parameter': ['Project name', 'City', 'ZIP Code', 'State', 'Country', 'Country Code', 'Latitude [°]',
                              'Longitude [°]', 'Start time', 'End time', 'Time resolution', 'Currency',
                              'Electricity price [' + env.currency + '/kWh]', 'CO2 price [' + env.currency + '/t]',
                              'Feed-in tariff [' + env.currency + '/kWh]', 'System lifetime [a]', 'Interest rate',
                              'Discount rate', 'CO2 equivalent Diesel [kg/kWh]', 'CO2 equivalent Grid [kg/kWh]'],
                'Values': [env.name, env.address[0], env.address[1], env.address[2], env.address[3], env.address[4],
                           env.latitude, env.longitude, env.t_start, env.t_end, env.t_step, env.currency,
                           env.electricity_price, env.co2_price, env.feed_in, env.lifetime, env.i_rate, env.d_rate,
                           env.co2_diesel, env.co2_grid]}
        df = pd.DataFrame.from_dict(data=data)

        return df

    def create_evaluation_parameter(self):
        """
        Create df with system evaluation parameters
        :return: pd.DataFrame
            Parameters for system evaluation
        """
        env = self.env
        df = self.operator.evaluation_df
        df = df.set_index('Component')
        for pv in self.env.pv:
            df.loc[pv.name, 'Investment Cost [' + env.currency + ']'] = pv.c_invest_n*pv.p_n/1000
        for wt in self.env.wind_turbine:
            df.loc[wt.name, 'Investment Cost [' + env.currency + ']'] = wt.c_invest_n*wt.p_n/1000
        for dg in self.env.diesel_generator:
            df.loc[dg.name, 'Investment Cost [' + env.currency + ']'] = dg.c_invest_n*dg.p_n/1000
        df.loc['System', 'Investment Cost [' + env.currency + ']'] = df['Investment Cost [' + env.currency + ']'].sum()

        return df

    def retrieve_energy_parameters(self):
        """
        Retrieve and calculate energy supply per component group
        :return: list
            energy supply values
        """
        env = self.env
        data = self.operator.energy_supply_parameters
        pv_energy = 0
        wt_energy = 0
        grid_energy = 0
        dg_energy = 0
        es_charge = 0
        es_discharge = 0
        for pv in env.pv:
            pv_energy += int(data[0][pv.name])
        for wt in env.wind_turbine:
            wt_energy += int(data[1][wt.name])
        for grid in env.grid:
            grid_energy += int(data[2][grid.name])
        for dg in env.diesel_generator:
            dg_energy += int(data[3][dg.name])
        for es in env.storage:
            es_charge += int(data[4][es.name])
            es_discharge += int(data[5][es.name])

        return pv_energy, wt_energy, grid_energy, dg_energy, es_charge, es_discharge

    def create_plot(self, df: pd.DataFrame, columns: list, file_name: str, x_label: str = None, y_label: str = None,
                    factor: float = None):
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
        :param factor: float
            factor to scale values
        :return: None
        """
        if factor is not None:
            df = df[columns] / factor
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
        m = folium.Map(location=[self.latitude, self.longitude], zoom_start=10)
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
