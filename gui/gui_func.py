"""
Module including GUI functions
@author: Paul Bohn
@contributor: Paul Bohn
"""

__version__ = '0.1'
__author__ = 'pdb-94'

import sys
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from gui.gui_table import Table
from components.storage import Storage


def convert_datetime(start: str, end: str, step: str):
    """
    Convert env datetime str to dt.datetime
    :param start: str
        start time
    :param end: str
        end time
    :param step: str
        timestep
    :return: list
    """
    t_start = dt.datetime.strptime(start, '%d.%m.%Y %H:%M')
    t_end = dt.datetime.strptime(end, '%d.%m.%Y %H:%M')
    t_step = dt.datetime.strptime(step, '%H:%M')
    help_date = dt.datetime(year=1900, month=1, day=1, hour=0, minute=0)
    t_step = t_step - help_date

    return t_start, t_end, t_step


def check_empty_string(parameter):
    """

    :param parameter:
    :return:
    """
    if parameter != '':
        return parameter
    else:
        return


def convert_time(text: str):
    """
    Convert text into int
    :param text: str
        time string
    :return: hour, minute: int
    """
    time_list = text.split(':')
    hour = int(time_list[0])
    minute = int(time_list[1])

    return hour, minute


def show_widget(widget: list, show: bool = True):
    """
    Show buttons
    :param widget: list
        buttons to show
    :param show: bool
        boolean value to show widgets
    :return: None
    """
    if show is True:
        for i in range(len(widget)):
            widget[i].show()
    elif show is False:
        for i in range(len(widget)):
            widget[i].hide()


def enable_widget(widget: list, enable: bool = True):
    """
    Show widgets
    :param widget: list
        buttons to show
    :param enable: bool
        boolean value to enable widgets
    :return: None
    """
    for i in range(len(widget)):
        widget[i].setEnabled(enable)


def delete_from_viewer(widget, item: int):
    """
    Delete Item from ListWidget
    :param widget: PyQt5 ListWidget()
        ListWidget from tab
    :param item: list
        strings to delete from ListWidget
    :return:
    """
    viewer = widget.viewer
    viewer.takeItem(item)


def add_to_viewer(widget, item: list):
    """
    Add Item to ListWidget
    :param widget: PyQt5 ListWidget
        ListWidget from tab
    :param item: list
        strings to add to ListWidget
    :return: None
    """
    viewer = widget.viewer
    viewer.addItems(item)


def add_to_room_viewer(widget, item: list):
    """
    Add Item to Room ListWidget
    :param widget: PyQt5 ListWidget
        ListWidget from tab
    :param item: list
        strings to add to ListWidget
    :return: None
    """
    viewer = widget.viewer
    if viewer.count() == 0:
        viewer.addItems(item)


def add_combo(widget, name: list):
    """
    Add Item to department_ComboBox in Tab Room
    :param widget: PyQt5 ComboBox
        QComboBox
    :param name: list
        items to add to ComboBox
    :return: None
    """
    combo_box = widget
    combo_box.addItems(name)


def change_combo_index(combo: list, index: list = None):
    """
    Show first item in ComboBox
    :param combo: list
    :return: None
    """
    for i in range(len(combo)):
        if combo[i].count() == 0:
            pass
        else:
            if index == None:
                combo[i].setCurrentIndex(0)
            else:
                combo[i].setCurrentIndex(index[i])


def delete_from_combo(combo, index: int):
    """
    :param combo: PyQt5 QComboBox
        QComboBox
    :param index: int
        row to delete
    :return: None
    """
    combo.removeItem(index)


def clear_widget(widget: list):
    """
    Clear widgets
    :param widget: PyQt5 Widget
        Widget to clear
    :return: None
    """
    for x in widget:
        x.clear()


def change_widget_text(widget: list, text: list):
    """
    Change widget text
    :param widget: PyQt5 Widget
        Widget to change text
    :param text: str
        new text
    :return: None
    """
    for i in range(len(widget)):
        widget[i].setText(text[i])


def set_alignment(widget, alignment):
    """

    :param widget:
    :param alignment:
    :return:
    """
    for i in range(len(widget)):
        widget[i].setAlignment(alignment)


def create_pixmap(path, widget, w, h):
    """
    :param path:
    :param widget:
    :param w:
    :param h:
    :return:
    """
    pixmap = QPixmap(path)
    widget.setPixmap(pixmap.scaled(w,
                                   h,
                                   Qt.KeepAspectRatio,
                                   Qt.SmoothTransformation))


def convert_str_float(string):
    """
    Convert string to float
    :param string: str
    :return: float/None
    """
    if string != '':
        try:
            parameter = float(string)
        except ValueError:
            parameter = False
    else:
        parameter = None

    return parameter


def update_component_df(data: pd.DataFrame, tab: QWidget):
    """
    Update dispatch component df
    :param tab: QWidget
    :param data: pd.DataFrame
        Component data
    :return: None
    """
    tab.component_df = pd.concat([tab.component_df, data], ignore_index=True)


def collect_component_data(component):
    """
    Collect parameters for overview
    :param component: object
    :return: dict
        component data
    """
    if isinstance(component, Storage):
        c = component.c / 1000
    else:
        c = None
    c_type = component.name.split('_')[0]
    data = {'Component': [c_type],
            'Name': [component.name],
            'Power [kW]': [component.p_n / 1000],
            'Capacity [kWh]': [c],
            'Investment cost [US$]': [component.c_invest],
            'Operation maintenance cost [US$/a]': [component.c_op_main],
            'Initial CO2 emissions [kg]': [component.co2_init]}

    component_data = pd.DataFrame(data)

    return component_data


def update_listview(tab: QWidget, df: pd.DataFrame):
    """

    :return: None
    """
    tab.table = Table(data=df)
    tab.overview.setModel(tab.table)


def create_wind_plot(name: str, data_1: pd.Series, data_2: pd.Series):
    """
    Create monthly wind data plot
    :param name: str
        Image name
    :param data_1: pd.Series
        Wind speed data array
    :param data_2: pd.Series
        Wind direction data array
    :return:
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel('Month')
    fig.legend(['wind speed', 'wind direction'])
    ax2 = ax.twinx()
    data_1.plot(kind='bar', color='lightgreen', ax=ax, width=0.2, position=1, label='Wind speed')
    data_2.plot(kind='bar', color='steelblue', ax=ax2, width=0.2, position=0, label='Wind direction')
    ax.set_ylabel(ylabel='wind speed [m/s]')
    ax2.set_ylabel(ylabel='wind direction [°]')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')
    fig.tight_layout()
    plt.savefig(f'{sys.path[1]}/gui/images/{name}.png')


def create_solar_plot(name: str, data: pd.DataFrame):
    """
    Create monthly solar data plot
    :param name: str
        image name
    :param data: pd:DataFrame
        Data source
    :return: None
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel('Month')
    data['ghi'].plot(kind='bar', color='yellow', ax=ax, width=0.2, position=1,
                     label='Global horizontal irradiation')
    data['dhi'].plot(kind='bar', color='gold', ax=ax, width=0.2, position=0, label='Direct horizontal irradiation')
    data['dni'].plot(kind='bar', color='darkorange', ax=ax, width=0.2, position=2,
                     label='Direct normal irradiation')
    ax.set_ylabel(ylabel='Solar irradiation [W/m²]')
    plt.legend(loc='upper left')
    fig.tight_layout()
    plt.savefig(f'{sys.path[1]}/gui/images/{name}.png')
