"""
Module including GUI functions
@author: Paul Bohn
@contributor: Paul Bohn
"""

__version__ = '0.1'
__author__ = 'pdb-94'

import datetime as dt
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


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
    for i in range(len(widget)):
        widget[i].clear()


def change_widget_text(widget: list, text: list):
    """
    Change widget text
    :param widget: PyQt5 Widget
        Widget to change text
    :param text: str
        new text
    :return: NOne
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
    widget.setPixmap(pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))