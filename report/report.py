import sys
import os
import calendar
import threading
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import io
import folium
import pandas as pd
from PIL import Image
from report.pdf import PDF


class Report:
    """
    Class to create results and report
    """

    def __init__(self,
                 env=None,
                 operator=None,
                 evaluation=None):
        """
        :param env: env.Environment
            MiGUEL Environment
        :param operator:
            MiGUEL Operator
        """
        self.timeout = 15
        self.env = env
        self.operator = operator
        self.eval = evaluation
        self.sankey = None
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
        self.evaluation_df = self.eval.evaluation_df
        # Root path
        self.root = sys.path[1]
        self.report_path = self.root + '/report/'
        self.txt_file_path = self.root + '/report/txt_files/'
        # Evaluation parameters
        self.system_LCOE = round(self.evaluation_df.loc['System', f'LCOE [{self.env.currency}/kWh]'], 2)
        self.system_annual_energy_cost = self.evaluation_df.loc['System', f'Annual cost [{self.env.currency}/a]']
        self.system_lifetime_cost = int(self.evaluation_df.loc['System', f'Lifetime cost [{self.env.currency}]'])
        self.gird_lifetime_cost = int(self.eval.grid_cost_comparison_lifetime)
        self.dg_lifetime_cost = int(self.eval.dg_cost_comparison_lifetime)
        # PDF
        self.pdf_file = PDF(title=self.name)
        self.create_pdf()

    def create_pdf(self):
        """
        Create pdf-report
        :return: None
        """
        # Set author
        self.pdf_file.set_author('Paul Bohn')
        self.pdf_file.set_creator('Micro Grid User Energy Planning Tool Library')
        self.pdf_file.set_keywords('EnerSHelF, Renewable Energy, Energy systems, MiGUEL, Ghana, '
                                   'PV-Diesel-Hybrid systems')
        self.pdf_file.add_page()
        self.pdf_file.chapter_title(label=f'Energy system: {self.name}\n\n',
                                    size=14)
        # Create Chapters
        event = threading.Event()
        thread = threading.Thread(target=self.create_sankey, daemon=True)
        thread.start()
        thread.join(self.timeout)
        if thread.is_alive():
            event.set()
            print(f'The function create_sankey was interrupted because it lasted longer than {self.timeout}s.')
        else:
            self.sankey = True
        self.introduction_summary()
        self.base_data()
        self.climate_data()
        self.energy_consumption()
        if len(self.env.pv) or len(self.env.wind_turbine) > 0:
            self.energy_supply()
        self.dispatch()
        self.evaluation()
        # Create report
        self.pdf_file.output(self.root + '/export/' + self.name + '.pdf')

    '''Functions to create chapters'''
    def introduction_summary(self):
        """
        Create Introduction and Summary
        :return: None
        """
        # Retrieve energy values from evaluation
        annual_energy_consumption = int(self.operator.energy_consumption)
        energy_parameters = {}
        for row in self.evaluation_df.index:
            energy_parameters[row] = self.evaluation_df.loc[row, 'Annual energy supply [kWh/a]']
        # Summarize values based on component type
        pv_energy = sum([value for key, value in energy_parameters.items() if 'PV' in key])
        wt_energy = sum([value for key, value in energy_parameters.items() if 'WT' in key])
        dg_energy = sum([value for key, value in energy_parameters.items() if 'DG' in key])
        grid_energy = sum([value for key, value in energy_parameters.items() if 'Grid' in key])
        # Calculate energy fraction
        pv_percentage = round(pv_energy / annual_energy_consumption, 2) * 100
        wt_percentage = round(wt_energy / annual_energy_consumption, 2) * 100
        dg_percentage = round(dg_energy / annual_energy_consumption, 2) * 100
        grid_percentage = round(grid_energy / annual_energy_consumption, 2) * 100
        # Retrieve Storage values
        es_charge = sum([value for key, value in energy_parameters.items() if '_charge' in key])
        es_discharge = abs(sum([value for key, value in energy_parameters.items() if '_discharge' in key]))
        # Calculate cost savings
        if self.env.system == 'Off Grid System':
            cost_difference = self.dg_lifetime_cost - self.system_lifetime_cost
            sys_comparison = 'a diesel generator'
        else:
            cost_difference = self.gird_lifetime_cost - self.system_lifetime_cost
            sys_comparison = 'the power grid'
        if cost_difference < 0:
            cost_paragraph = f" Additional costs of {abs(int(cost_difference)):,} {self.env.currency} occur over the system " \
                             f"lifetime of {self.env.lifetime} years, compared to an energy supply provided through " \
                             f"{sys_comparison}."
        else:
            cost_paragraph = f" Cost savings of {abs(int(cost_difference)):,} {self.env.currency} occur over the system " \
                             f"lifetime of {self.env.lifetime} years due to the implementation of the energy system, " \
                             f"compared to an energy supply provided through {sys_comparison}."
        # Write chapter depending on if energy consumption is met
        if self.operator.system_covered is True:
            system_status = f"The selected system is considered an '{self.env.system}'. With the selected system " \
                            f"configuration, the energy demand of {annual_energy_consumption:,} kWh is covered."
            system_status = system_status + cost_paragraph
        else:
            energy_demand = int(self.operator.power_sink['P [W]'].sum() * self.env.i_step / 60 / 1000)
            system_status = f"The selected system is considered an '{self.env.system}'. With the selected system " \
                            f"configuration, THE ANNUAL ENERGY DEMAND OF {annual_energy_consumption:,} kWh IS NOT COVERED. " \
                            f"The remaining energy to be covered equals {energy_demand:,} kWh. " \
                            f"The highest load peak to be covered equals {self.operator.power_sink_max/1000:,} kW. " \
                            f"The table shows the time stamps and the power to be covered."
        summary = system_status + \
                  f" The PV system(s) account for {pv_percentage}% ({pv_energy:,} kWh); The wind turbine(s) account for " \
                  f"{wt_percentage}% ({wt_energy:,} kWh); The grid accounts {grid_percentage}% ({grid_energy: ,} kWh); " \
                  f"The diesel generator(s) account for {dg_percentage}% ({dg_energy:,} kWh) of the total energy " \
                  f"consumption. The energy storage(s) provide {abs(es_discharge):,} kWh and are charged with " \
                  f"{abs(es_charge):,} kWh. The table below shows the energy systems key parameters. The parameters will " \
                  f"be described in detail in the upcoming report. \nThe investment cost and CO2 emissions for energy " \
                  f"storages include investment costs and CO2 emissions caused by replacements over the project lifetime. \n\n"
        self.create_txt(file_name='summary',
                        text=summary)
        self.pdf_file.print_chapter(chapter_type=[False, False],
                                    title=['Introduction', 'Summary'],
                                    file=[self.txt_file_path + 'default/introduction.txt',
                                          self.txt_file_path + 'summary.txt'])
        # Create evaluation table
        evaluation_header = ['Component',
                             'Lifetime energy [kWh]',
                             f'Invest. Cost [{self.env.currency}]',
                             f'LCOE [{self.env.currency}/kWh]',
                             'Lifetime CO2 emissions [t]']
        evaluation_values = [evaluation_header]
        for row in self.evaluation_df.index:
            data = [row]
            data.append(round(self.evaluation_df.loc[row, 'Lifetime energy supply [kWh]'], 0))
            data.append(round(self.evaluation_df.loc[row, f'Investment cost [{self.env.currency}]'], 0))
            if self.evaluation_df.loc[row, f'LCOE [{self.env.currency}/kWh]'] is None:
                data.append(None)
            else:
                data.append(round(self.evaluation_df.loc[row, f'LCOE [{self.env.currency}/kWh]'], 2))
            data.append(round(self.evaluation_df.loc[row, 'Lifetime CO2 emissions [t]'], 3))
            evaluation_values.append(data)
        evaluation_data = [[''], evaluation_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=evaluation_data,
                                   padding=2)

    def base_data(self):
        """
        Create chapter 1 - Base data
        :return: None
        """
        # Create map
        self.create_map()
        # Create chapter
        self.pdf_file.print_chapter(chapter_type=[True],
                                    title=['1 Base data'],
                                    file=[self.txt_file_path + 'default/1_base_data.txt'])
        input_header = ['Parameter', 'Value']
        input_values = [input_header]
        for row in self.input_parameter.index:
            input_values.append(self.input_parameter.loc[row, :].values.tolist())
        input_data = [[''], input_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=input_data,
                                   padding=2)
        self.pdf_file.ln(h=10)
        # Include location map
        self.pdf_file.image(name=self.report_path + 'pictures/' + '/location.png', w=160)

    def climate_data(self):
        """
        Create chapter 2 - Weather data
        :return: None
        """
        # Create plots
        self.create_plot(df=self.weather_data[0],
                         columns=['ghi', 'dni', 'dhi'],
                         file_name='solar_data',
                         y_label='P [W/m²]')
        # Wind speed
        self.create_plot(df=self.weather_data[0],
                         columns=['wind_speed'],
                         file_name='wind_data',
                         y_label='v [m/s]')
        # Print chapter 2
        self.pdf_file.print_chapter(chapter_type=[True],
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
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=tmy_data,
                                   padding=1.5,
                                   sep=False)
        self.pdf_file.ln(h=10)
        # 2.1 Solar irradiation
        self.pdf_file.print_chapter(chapter_type=[False],
                                    title=['2.1 Solar irradiation'],
                                    file=[self.txt_file_path + 'default/2_1_solar_radiation.txt'])
        # Plot solar irradiation
        self.pdf_file.image(name=self.report_path + 'pictures/' + '/solar_data.png', w=140, x=35)
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
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=solar_data,
                                   padding=1.5)
        self.pdf_file.ln(h=10)
        # 2.2 Wind speed
        self.pdf_file.print_chapter(chapter_type=[False],
                                    title=['2.2 Wind speed'],
                                    file=[self.txt_file_path + 'default/2_2_wind_speed.txt'])
        self.pdf_file.image(name=self.report_path + 'pictures/' + '/wind_data.png', w=140, x=35)
        # Monthly weather data Table
        wind_data_header = ['Month', 'Avg. Wind Speed [m/s]', 'Avg. Wind direction [°]']
        wind_values = [wind_data_header]
        for row in self.env.monthly_weather_data.index:
            data = [calendar.month_name[row], round(self.env.monthly_weather_data.iloc[row - 1, 6], 3),
                    round(self.env.monthly_weather_data.iloc[row - 1, 7], 3)]
            wind_values.append(data)
        wind_data = [[''], wind_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=wind_data,
                                   padding=1.5)
        wind_speed_max = round(self.env.monthly_weather_data['wind_speed'].max(), 3)
        self.pdf_file.ln(h=10)
        month_max = self.env.monthly_weather_data['wind_speed'].idxmax()
        month_max = calendar.month_name[month_max]
        wind_speed_average = round(self.env.monthly_weather_data['wind_speed'].mean(), 3)
        wind_direction_average = round(self.env.monthly_weather_data['wind_direction'].mean(), 3)
        wind_table_text = f'The main wind direction is {wind_direction_average}°. The annual average wind speed is ' \
                          f'{wind_speed_average:,} m/s. The highest monthly wind speed occurs in {month_max} and is ' \
                          f'{wind_speed_max:,} m/s.'
        self.create_txt(file_name='2_2_table_description',
                        text=wind_table_text)
        self.pdf_file.chapter_body(name=self.txt_file_path + '2_2_table_description.txt', size=10)

    def energy_consumption(self):
        """
        Create chapter 3 - Energy consumption
        :return: None
        """
        # Create plot
        self.create_plot(df=self.operator.df,
                         columns=['Load [W]'],
                         file_name='load_profile',
                         x_label='Time',
                         y_label='P [kW]',
                         factor=1000)
        # Print Chapters
        self.pdf_file.print_chapter(chapter_type=[True],
                                    title=['3 Energy consumption'],
                                    file=[self.txt_file_path + 'default/3_energy_consumption.txt'])
        self.pdf_file.image(name=self.report_path + 'pictures/' + 'load_profile.png',
                            w=150,
                            x=30)
        # Create table with reference parameters
        energy_con_header = ['', 'Power Grid', 'Diesel Generator']

        total_energy_con = ['Energy consumption [kWh]',
                            round(self.operator.energy_consumption, 3),
                            round(self.operator.energy_consumption, 3)]
        peak_load = ['Peak load [kW]',
                     round(self.operator.peak_load / 1000, 3),
                     round(self.operator.peak_load / 1000, 3)]

        cost = [f'Energy cost [{self.env.currency}]',
                int(self.eval.grid_cost_comparison_annual),
                int(self.eval.dg_cost_comparison_annual)]
        co2_emission = ['CO2 emissions [t]',
                        round(self.operator.energy_consumption / 1000 * self.env.co2_grid, 3),
                        round(self.operator.energy_consumption / 1000 * self.env.co2_diesel, 3)]
        energy_con_values = [energy_con_header, total_energy_con, peak_load, cost, co2_emission]
        energy_con_data = [[''], energy_con_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=energy_con_data,
                                   padding=1.5)
        self.pdf_file.ln(h=10)

    def energy_supply(self):
        """
        Create chapter - System configuration
        :return: None
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
        self.create_plot(df=self.env.df,
                         columns=columns,
                         file_name='re_supply',
                         x_label='Time',
                         y_label='P [kW]',
                         factor=1000)
        re_production = f'The plot shows the total wind power and PV output during the period from {self.env.t_start}' \
                        f' to {self.env.t_end} in a {self.env.t_step} resolution: \nPhotovoltaic total: ' \
                        f'{int(pv_energy / 1000):,} kWh \nWind turbine total: {int(wt_energy / 1000):,} kWh.'
        self.create_txt(file_name='4_2_re_energy_supply',
                        text=re_production)
        self.pdf_file.print_chapter(chapter_type=[True],
                                    title=['4 System configuration'],
                                    file=[self.txt_file_path + 'default/4_system_configuration.txt'])
        self.pdf_file.print_chapter(chapter_type=[False],
                                    title=['4.1 System components'],
                                    file=[self.txt_file_path + 'default/4_1_system_components.txt'],
                                    size=10)
        # Create Supply table
        supply_header = ['Component', 'Name', 'P [kW]', f'i_c [{self.env.currency}/kW]', f'I_c [{self.env.currency}]',
                         f'om_c [{self.env.currency}/kW]', f'OM_c [{self.env.currency}/a]']
        # Define table values
        supply_values = [supply_header]
        # Get technical data from env.supply_data
        for row in self.env.supply_data.index:
            supply_values.append(self.env.supply_data.loc[row, :].values.tolist())
        supply_components = [[''], supply_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=supply_components,
                                   padding=2)
        self.pdf_file.chapter_body(name=self.txt_file_path + 'default/4_1_energy_storage.txt',
                                   size=10)
        # Get technical data from env.storage_data
        storage_header = ['Component', 'Name', 'P [kW]', 'W [kWh]', f'i_c [{self.env.currency}/kWh]',
                          f'I_c [{self.env.currency}]', f'om_c [{self.env.currency}/kWh]',
                          f'OM_c [{self.env.currency}/a]']
        storage_values = [storage_header]
        for row in self.env.storage_data.index:
            storage_values.append(self.env.storage_data.loc[row, :].values.tolist())
        storage_components = [[''], storage_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=storage_components,
                                   padding=2)
        self.pdf_file.chapter_body(name=self.txt_file_path + 'default/4_1_system_configuration_description.txt',
                                   size=8)
        # Chapter 4 - Monthly data
        self.pdf_file.print_chapter(chapter_type=[False],
                                    title=['4.2 Renewable energy supply'],
                                    file=[self.txt_file_path + '4_2_re_energy_supply.txt'],
                                    size=10)
        self.pdf_file.image(name=self.report_path + 'pictures/' + '/re_supply.png', w=150, x=30)

    def dispatch(self):
        """
        Create chapter 5 - dispatch
        :return: None
        """
        env = self.env
        dispatch_5 = f"This chapter presents the dispatch of the power system. The system is considered a " \
                     f"'{self.env.system}'. The plot below shows the load profile and the power the system " \
                     f"components supply in kW. Energy storage systems can both consume and supply power. Negative " \
                     f"values correspond to power output (power source), positive loads to power input (power sink).\n "
        self.create_txt(file_name='5_dispatch',
                        text=dispatch_5)
        self.pdf_file.print_chapter(chapter_type=[True],
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
        if self.env.grid is not None:
            columns.append(self.env.grid.name + ' [W]')
        for dg in env.diesel_generator:
            columns.append(dg.name + ' [W]')
        self.create_plot(df=self.operator.df,
                         columns=columns,
                         file_name='dispatch',
                         y_label='P [W]')
        self.pdf_file.image(name=self.report_path + 'pictures/dispatch.png',
                            w=150,
                            x=30,
                            h=120)
        self.pdf_file.chapter_body(name=self.txt_file_path + '/default/5_sankey.txt',
                                   size=10)
        if self.sankey:
            self.pdf_file.image(name=self.report_path + 'pictures/sankey.png',
                                w=150,
                                x=30)

    def evaluation(self):
        """
        Chapter 6 - evaluation
        :return: None
        """
        env = self.env

        self.pdf_file.print_chapter(chapter_type=[True, False],
                                    title=['6 Evaluation', '6.1 Economic evaluation'],
                                    file=[self.txt_file_path + 'default/6_evaluation.txt',
                                          self.txt_file_path + 'default/6_1_economic_evaluation.txt'],
                                    size=10)
        # Create economic evaluation table
        economic_evaluation_header = ['Component',
                                      'Annual Energy [kWh]',
                                      f'Lifetime cost [{env.currency}]',
                                      f'Invest. Cost [{env.currency}]',
                                      f'Annual Cost [{env.currency}/a]',
                                      f'LCOE [{env.currency}/kWh]']
        economic_evaluation_values = [economic_evaluation_header]
        for row in self.evaluation_df.index:
            data = [row]
            data.append(self.evaluation_df.loc[row, 'Annual energy supply [kWh/a]'])
            data.append(self.evaluation_df.loc[row, f'Lifetime cost [{env.currency}]'])
            data.append(self.evaluation_df.loc[row, f'Investment cost [{env.currency}]'])
            data.append(self.evaluation_df.loc[row, f'Annual cost [{env.currency}/a]'])
            if self.evaluation_df.loc[row, f'LCOE [{env.currency}/kWh]'] is None:
                data.append(None)
            else:
                data.append(round(self.evaluation_df.loc[row, f'LCOE [{env.currency}/kWh]'], 2))
            economic_evaluation_values.append(data)
        economic_evaluation_data = [[''], economic_evaluation_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=economic_evaluation_data,
                                   padding=2)
        economic_table_description = f'The overall system LCOE is {self.system_LCOE} {env.currency}/kWh. The energy costs ' \
                                     f'incurred in the period under consideration amount to {self.system_lifetime_cost:,} ' \
                                     f'{env.currency}. '
        # Compare systems with energy supply only from grid or diesel generator
        if self.env.system == 'Off Grid System':
            comparison = f'In comparison, the energy costs from a complete supply from diesel generators amount to ' \
                         f'{self.dg_lifetime_cost:,} {env.currency}. '
            if self.dg_lifetime_cost - self.system_lifetime_cost < 0:
                cost = f'Additional cost of {int(abs(self.dg_lifetime_cost - self.system_lifetime_cost)):,} ' \
                       f'{env.currency} occur to cover the lifetime energy demand.\n\n'
            else:
                cost = f'{int(self.dg_lifetime_cost - self.system_lifetime_cost):,} {env.currency} are ' \
                       f'saved over the system lifetime with the simulated system configuration.\n\n'
        else:
            comparison = f'In comparison, the energy costs from a complete supply from the power grid amount to ' \
                         f'{self.gird_lifetime_cost:,} {env.currency}. '
            if self.gird_lifetime_cost - self.system_lifetime_cost < 0:
                cost = f'Additional cost of {int(abs(self.gird_lifetime_cost - self.system_lifetime_cost)):,} ' \
                       f'{env.currency} occur to cover the lifetime energy demand.\n\n'
            else:
                cost = f'{int(self.gird_lifetime_cost - self.system_lifetime_cost):,} {env.currency} are ' \
                       f'saved over the system lifetime with the simulated system configuration.\n\n'
        self.create_txt(file_name='6_1_table_description',
                        text=economic_table_description + comparison + cost)
        self.pdf_file.ln(h=10)
        self.pdf_file.chapter_body(name=self.txt_file_path + '6_1_table_description.txt',
                                   size=10)
        self.pdf_file.print_chapter(chapter_type=[False],
                                    title=['6.2 Ecologic evaluation'],
                                    file=[self.txt_file_path + 'default/6_2_ecologic_evaluation.txt'],
                                    size=10)
        # Ecologic evaluation
        ecologic_evaluation_header = ['Component',
                                      'Lifetime CO2 emission [t]',
                                      'Initial CO2 emission [t]',
                                      'Annual CO2 emission [t/a]']
        ecologic_evaluation_values = [ecologic_evaluation_header]
        for row in self.evaluation_df.index:
            data = [row]
            data.append(round(self.evaluation_df.loc[row, 'Lifetime CO2 emissions [t]'], 3))
            data.append(round(self.evaluation_df.loc[row, 'Initial CO2 emissions [t]'], 3))
            data.append(round(self.evaluation_df.loc[row, 'Annual CO2 emissions [t/a]'], 3))
            ecologic_evaluation_values.append(data)
        ecologic_evaluation_data = [[''], ecologic_evaluation_values]
        self.pdf_file.create_table(file=self.pdf_file,
                                   table=ecologic_evaluation_data,
                                   padding=2)
        self.pdf_file.ln(h=10)
        self.create_bar_plot(df=self.evaluation_df,
                             columns=['Initial CO2 emissions [t]', 'Annual CO2 emissions [t/a]'],
                             file_name='co2_emissions',
                             y_label='CO2 emissions [t]')
        self.pdf_file.image(name=self.report_path + 'pictures/co2_emissions.png', w=150)
        self.pdf_file.chapter_body(name=self.txt_file_path + 'default/6_2_table_description.txt', size=10)

    '''Functions to support chapter content'''

    def create_input_parameter(self):
        """
        Create DataFrame with input Parameters
        :return: pd.DataFrame
            df with input parameters
        """
        env = self.env
        data = {'Parameter': ['Project name', 'City', 'ZIP Code', 'State', 'Country', 'Country Code', 'Latitude [°]',
                              'Longitude [°]', 'Start time', 'End time', 'Time resolution', 'Currency',
                              f'Electricity price [{env.currency}/kWh]', f'CO2 price [{env.currency}/t]',
                              'Feed in possible', f'PV Feed-in tariff [{env.currency}/kWh]',
                              f'Wind turbine Feed-in tariff [{env.currency}/kWh]', 'System lifetime [a]',
                              'Discount rate', 'CO2 equivalent Diesel [kg/kWh]', 'CO2 equivalent Grid [kg/kWh]'],
                'Value': [env.name, env.address[0], env.address[1], env.address[2], env.address[3], env.address[4],
                          env.latitude, env.longitude, env.t_start, env.t_end, env.t_step, env.currency,
                          env.electricity_price, env.avg_co2_price, env.feed_in, env.pv_feed_in_tariff,
                          env.wt_feed_in_tariff, env.lifetime, env.d_rate, env.co2_diesel, env.co2_grid]}
        df = pd.DataFrame.from_dict(data=data)

        return df

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
        plt.savefig(self.report_path + 'pictures/' + file_name + '.png',
                    dpi=300)

    def create_bar_plot(self, df: pd.DataFrame, columns: list, file_name: str, y_label: str = None):
        """
        Create bar chart with co2-emissions
        :param df: pd.DataFrame
            data to plot
        :param columns: list
            columns of dataframe
        :param file_name: str
            file name to save plot
        :param y_label: str
            y label
        :return: None
        """
        fig, ax = plt.subplots()
        ax.bar(df.index,
               df[columns[1]] * self.env.lifetime,
               0.5,
               label='Operational CO2 emissions [t]')
        ax.bar(df.index,
               df[columns[0]],
               0.5,
               label='Initial CO2 emissions [t]')
        ax.set_ylabel(y_label)
        ax.set_ylabel(y_label)
        ax.legend()
        plt.tight_layout()
        plt.savefig(self.report_path + 'pictures/' + file_name + '.png',
                    dpi=300)

    def create_sankey(self):
        """
        Create Sankey diagram to visualize energy flow
        :return: None
        """
        env = self.env
        op = self.operator
        time_factor = env.i_step / 60 / 1000
        label = ['PV', 'PV self consumption', 'PV charge',
                 'Wind turbine', 'Wind turbine self consumption', 'Wind turbine charge',
                 'Grid', 'Diesel generator', 'Battery storage',
                 'Battery storage discharge', 'Load', 'Feed-in', 'Losses']
        node = dict(pad=15,
                    thickness=20,
                    line=dict(color='black',
                              width=0.5),
                    label=label)
        pv_sc = 0
        pv_charge = 0
        pv_feed_in = 0
        for pv in env.pv:
            pv_sc += op.df[f'{pv.name} [W]'].sum() * time_factor
            if len(env.storage) > 0:
                pv_charge += op.df[f'{pv.name}_charge [W]'].sum() * time_factor
            if env.grid_connection and env.feed_in is True:
                pv_feed_in += op.df[f'{pv.name} Feed in [W]'].sum() * time_factor
        pv_production = pv_sc
        wt_sc = 0
        wt_charge = 0
        wt_feed_in = 0
        grid_production = 0
        if env.grid is not None:
            grid_production += op.df[f'{env.grid.name} [W]'].sum() * time_factor
        for wt in env.wind_turbine:
            wt_sc += op.df[f'{wt.name} [W]'].sum() * time_factor
            if len(env.storage) > 0:
                wt_charge += op.df[f'{wt.name}_charge [W]'].sum() * time_factor
            if env.grid_connection and env.feed_in is True:
                wt_feed_in += op.df[f'{wt.name} Feed in [W]'].sum() * time_factor
        wt_production = wt_sc
        dg_production = 0
        for dg in env.diesel_generator:
            dg_production += op.df[f'{dg.name} [W]'].sum() * time_factor
        es_discharge = 0
        for es in env.storage:
            es_discharge += op.df[op.df[f'{es.name} [W]'] > 0].sum() * time_factor
        source = [6, 7, 0, 1, 0, 2, 2, 0, 3, 4, 3, 5, 5, 3, 8, 9, 9]
        target = [10, 10, 1, 10, 2, 8, 12, 11, 4, 10, 5, 8, 12, 11, 9, 10, 12]
        value = [grid_production,
                 dg_production,
                 pv_production, pv_sc, pv_charge, pv_charge * 0.9, pv_charge * 0.1, pv_feed_in,
                 wt_production, wt_sc, wt_charge, wt_charge * 0.9, wt_charge * 0.1, wt_feed_in,
                 (pv_charge + wt_charge) * 0.9, (pv_charge + wt_charge) * 0.9 ** 2, (pv_charge + wt_charge) * 0.1]
        link = dict(source=source,
                    target=target,
                    value=value)
        fig = go.Figure(data=[go.Sankey(node=node,
                                        link=link)])
        fig.update_layout(font_size=24)
        fig.write_image(file=self.report_path + '/pictures/sankey.png',
                        width=1500,
                        height=1500 / 1.618)

    def create_map(self):
        """
        Create folium map and save picture
        :return: folium Map object
            m
        """
        m = folium.Map(location=[self.latitude, self.longitude],
                       zoom_start=10)
        folium.Marker(location=[self.latitude, self.longitude],
                      tooltip='MiGUEL Project').add_to(m)
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
