#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007

"""

from PyQt5 import QtWidgets
from ....pyqtgraphCore.widgets.MatplotlibWidget import MatplotlibWidget
from ....analysis import Transmission, organize_dataframe_columns, get_proportions
from math import sqrt
from ..base import BasePlotWidget
from ....common.qdialogs import *
from ...utils import auto_colormap


class ProportionsWidget(BasePlotWidget, MatplotlibWidget):
    drop_opts = ['xs', 'ys']

    def __init__(self):
        super().__init__()
        self.ax = self.fig.add_subplot(111)

        self.message_label = QtWidgets.QLabel()
        self.message_label.setText('')
        self.message_label.setMaximumHeight(30)
        self.vbox.addWidget(self.message_label)

        xs_label = QtWidgets.QLabel(self)
        xs_label.setText('X column')
        xs_label.setMaximumHeight(30)
        self.vbox.addWidget(xs_label)

        self.xs_combo = QtWidgets.QComboBox(self)
        self.xs_combo.currentIndexChanged.connect(self.update_plot)
        self.xs_combo.setMaximumHeight(30)
        self.vbox.addWidget(self.xs_combo)

        ys_label = QtWidgets.QLabel(self)
        ys_label.setText('Y column')
        ys_label.setMaximumHeight(30)
        self.vbox.addWidget(ys_label)

        self.ys_combo = QtWidgets.QComboBox(self)
        self.ys_combo.setMaximumHeight(30)
        self.ys_combo.currentTextChanged.connect(self.update_plot)
        self.vbox.addWidget(self.ys_combo)

        self.checkbox_percent = QtWidgets.QCheckBox(self)
        self.checkbox_percent.setText('Show percentages')
        self.checkbox_percent.setChecked(True)
        self.checkbox_percent.toggled.connect(self.update_plot)
        self.checkbox_percent.setMaximumHeight(30)
        self.vbox.addWidget(self.checkbox_percent)

        self.btn_swap_xy = QtWidgets.QPushButton(self)
        self.btn_swap_xy.setText('Swap X-Y')
        self.btn_swap_xy.clicked.connect(self.swap_x_y)
        self.btn_swap_xy.setMaximumHeight(30)
        self.vbox.addWidget(self.btn_swap_xy)

        hlayout = QtWidgets.QHBoxLayout()

        btn_save = QtWidgets.QPushButton(self)
        btn_save.setText('Save')
        btn_save.clicked.connect(self.save_plot_dialog)
        btn_save.setMaximumHeight(30)
        hlayout.addWidget(btn_save)

        btn_load = QtWidgets.QPushButton(self)
        btn_load.setText('Load')
        btn_load.clicked.connect(self.open_plot_dialog)
        btn_load.setMaximumHeight(30)
        hlayout.addWidget(btn_load)

        self.vbox.addLayout(hlayout)

        btn_export = QtWidgets.QPushButton(self)
        btn_export.setText('Export CSV')
        btn_export.clicked.connect(self.export)
        btn_export.setMaximumHeight(30)
        self.vbox.addWidget(btn_export)

        spacer = QtWidgets.QSpacerItem(0, 10, QtWidgets.QSizePolicy.Expanding)
        self.vbox.insertSpacerItem(0, spacer)

        self.props_df = None

        self.block_signals_list = [self.xs_combo, self.ys_combo, self.checkbox_percent]

    @BasePlotWidget.signal_blocker
    def swap_x_y(self, *args, **kwargs):
        xs_opt = self.xs_combo.currentText()
        ys_opt = self.ys_combo.currentText()

        ix_x = self.xs_combo.findText(ys_opt)
        self.xs_combo.setCurrentIndex(ix_x)

        ix_y = self.ys_combo.findText(xs_opt)
        self.ys_combo.setCurrentIndex(ix_y)
        # self._block = False

        self.update_plot()

    @BasePlotWidget.signal_blocker
    def set_input(self, transmission: Transmission):
        super(ProportionsWidget, self).set_input(transmission)
        cols = self.transmission.df

        dcols, ccols, ucols = organize_dataframe_columns(cols)

        self.xs_combo.clear()
        self.xs_combo.addItems(ccols)

        self.ys_combo.clear()
        self.ys_combo.addItems(ccols)

    def get_plot_opts(self, drop: bool = False):
        xs_name = self.xs_combo.currentText()
        ys_name = self.ys_combo.currentText()

        opts = dict(xs_name=xs_name, ys_name=ys_name,
                    xs=self.transmission.df[xs_name],
                    ys=self.transmission.df[ys_name],
                    percentages=self.checkbox_percent.isChecked())
        if drop:
            for k in self.drop_opts:
                opts.pop(k)
        return opts

    @BasePlotWidget.signal_blocker
    def set_plot_opts(self, opts: dict):
        ix_x = self.xs_combo.findText(opts['xs_name'])
        self.xs_combo.setCurrentIndex(ix_x)

        ix_y = self.ys_combo.findText(opts['ys_name'])
        self.ys_combo.setCurrentIndex(ix_y)

        self.checkbox_percent.setChecked(opts['percentages'])

    @present_exceptions('Plot error', 'Cannot plot, make sure you have selected appropriate data columns')
    def update_plot(self, *args, **kwargs):
        self.ax.cla()

        opts = self.get_plot_opts()

        if opts['xs_name'] == opts['ys_name']:
            self.message_label.setText('Must choose different X and Y columns')
            return
        self.message_label.clear()

        ys = self.transmission.df[opts['ys_name']]

        show_percents = opts['percentages']

        self.props_df = get_proportions(**opts)

        n_labels = len(ys.unique())

        if n_labels < 11:
            cmap = 'tab10'
        elif 10 < n_labels < 21:
            cmap = 'tab20'
        elif 20 < n_labels < 211:
            cmap = 'nipy_spectral'
        else:
            raise ValueError('Cannot generate colormap for greater than 210 labels.\n'
                             'Why would you have > 210 labels?')

        colors = auto_colormap(n_labels, cmap)

        self.props_df.plot(kind='bar', stacked=True, ax=self.ax, color=colors)

        if show_percents:
            label = 'percentages'
        else:
            label = 'raw counts'

        self.ax.set_ylabel(label)
        self.ax.set_xlabel(opts['xs_name'])

        self.ax.legend(bbox_to_anchor=(0.0, 1.02, 1.0, 0.102), loc='upper center', ncol=int(sqrt(len(set(ys)))),
                       mode='expand')

        self.draw()
        self.toolbar.update()

    @present_exceptions('Export error', 'The following error occurred.')
    def export(self):
        if self.props_df is None:
            return
        if self.transmission is None:
            return

        try:
            proj_path = self.transmission.get_proj_path()
        except ValueError:
            proj_path = ''

        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save file as', proj_path, '(*.csv)')
        if path == '':
            return

        path = path[0]
        if not path.endswith('.csv'):
            path = f'{path}.csv'

        self.props_df.to_csv(path)
