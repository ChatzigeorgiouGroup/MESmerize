#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on April 24 2018

@author: kushal

Chatzigeorgiou Group
Sars International Centre for Marine Molecular Biology

GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
"""

# from ..core.common import ViewerUtils
# from ..core.viewer_work_environment import ViewerWorkEnv
from ..core import ViewerUtils, ViewerWorkEnv
# from ...pyqtgraphCore.imageview import ImageView
from ..main_window import MainWindow as ViewerWindow
from ..core.background_tiff_compressor import Compressor as TiffCompressor
from ...common import get_sys_config, get_timestamp_str, get_window_manager
from ...common.qdialogs import *
from ...common.utils import make_runfile, make_workdir
from .pytemplates.batch_manager_pytemplate import *
import json
import pandas
from .batch_run_modules import * # DO NOT REMOVE THIS LINE
import uuid
import numpy as np
# from .common import BatchRunInterface
import pickle
import tifffile
import os
from stat import S_IEXEC
# from multiprocessing import Queue
from functools import partial
from collections import deque
import psutil
from signal import SIGKILL
import traceback
from ...misc_widgets.list_widget_dialog import ListWidgetDialog
from glob import glob
from collections import UserList
from typing import *


class ModuleGUI(QtWidgets.QWidget):
    """GUI for the Batch Manager"""
    listwchanged = QtCore.pyqtSignal()

    def __init__(self, parent, run_batch: list = None, testing: bool = False):
        print('starting batch mananger')
        QtWidgets.QWidget.__init__(self, parent)
        self._testing = testing
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.checkBoxUseWorkDir.setChecked(True)
        self.ui.checkBoxUseWorkDir.toggled.connect(self.set_workdir)
        # self.ui.lineEditWorkDir.setEnabled(True)
        self._use_workdir = False
        self.working_dir = None
        self.batch_path = None

        self.ui.listwBatch.itemDoubleClicked.connect(self.on_list_widget_batch_doubleclicked)

        self.ui.btnStart.clicked.connect(self.process_batch)
        self.ui.btnStart.setDisabled(True)
        self.ui.btnStartAtSelection.clicked.connect(lambda: self.process_batch(
            start_ix=self.ui.listwBatch.indexFromItem(self.ui.listwBatch.currentItem()).row()))
        self.ui.btnStartAtSelection.setDisabled(True)

        self.ui.btnAbort.clicked.connect(self._terminate_qprocess)
        self.ui.btnAbort.setDisabled(True)
        self.ui.btnOpen.clicked.connect(self.open_batch)
        self.ui.btnDelete.clicked.connect(self.del_item)
        self.ui.btnViewInput.clicked.connect(self.btn_view_input_slot)
        self.ui.btnNew.clicked.connect(self.ask_create_new_batch)

        listwmodel = self.ui.listwBatch.model()
        listwmodel.rowsInserted.connect(self.listwchanged.emit)
        listwmodel.rowsRemoved.connect(self.listwchanged.emit)

        self.ui.scrollAreaStdOut.setStyleSheet('background-color: #131926')
        self.ui.textBrowserStdOut.setTextColor(QtGui.QColor('#b7b7b7'))

        self.ui.scrollAreaStdOut.hide()
        self.resize(1200, 650)
        self.ui.listwBatch.currentItemChanged.connect(self.show_item_info)

        self.output_widgets = []
        self.df = pandas.DataFrame() #: pandas.DataFrame that stores a "database" of information on the batch
        self.init_batch(run_batch)

        self.move_processes = []

        # self.ui.btnCompress.clicked.connect(self.compress_all)
        self.ui.btnExportShScripts.clicked.connect(self.export_submission_scripts)

        self.lwd = None

        self.ui.lineEditFindItem.textEdited.connect(self.higlight_items)
        self.previous_list_widget_colors = None

    def higlight_items(self):
        self.reset_list_widget_colors()
        txt = self.ui.lineEditFindItem.text()
        if not txt:
            return

        items = self.ui.listwBatch.findItems(txt, QtCore.Qt.MatchContains)

        for item in items:
            item.setBackground(QtGui.QBrush(QtGui.QColor('#FF94F7')))

    def init_batch(self, run_batch):
        if not self._testing:
            if run_batch is None:
                path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose the location of an existing batch folder '
                                                                        'or a location for a new batch folder')
                if path == '':
                    return
            else:
                path = run_batch[0]
                print('Opening batch: ' + path)

            dfpath = os.path.join(path, 'dataframe.batch')
            if os.path.isfile(dfpath):
                self.open_batch_dir(path)

            else:
                self.create_new_batch_dialog(path)

        self.ui.btnStart.setEnabled(True)
        self.ui.btnStartAtSelection.setEnabled(True)
        self.set_workdir(True)

        if run_batch is not None:
            print('Running from item ' + run_batch[1])
            # ix = self.df.index[self.df['uuid'] == uuid.UUID(run_batch[1])]
            # i = int(ix.to_native_types()[0])
            i = self.get_item_index(run_batch[1])
            self.process_batch(start_ix=i, clear_viewers=True)

    def get_item_index(self, u: Union[uuid.UUID, str]) -> int:
        """
        Get DataFrame index from UUID

        :param u: UUID or str representing UUID
        :type u: Union[uuid.UUID, str]

        :return:  numerical index of the DataFrame corresponding to the UUID
        :rtype: int
        """
        ix = self.df.index[self.df['uuid'] == uuid.UUID(u)]
        i = int(ix.to_native_types()[0])
        return i

    def ask_create_new_batch(self):
        if self.ui.listwBatch.count() > 0:
            if QtWidgets.QMessageBox.warning(self, 'Create Batch?', 'Close the current batch and open another one?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose location for a batch')
        if path == '':
            return

        if any(s in path for s in [' ', '(', ')', '?']):
            QtWidgets.QMessageBox.warning(self, 'Invalid path',
                                          'Batch path cannot contain spaces or special characters')
            return

        self.create_new_batch_dialog(path)

    def create_new_batch_dialog(self, path: str):
        name, start = QtWidgets.QInputDialog.getText(self, '', 'Batch Name:', QtWidgets.QLineEdit.Normal, '')

        if any(s in name for s in [' ', '(', ')', '?']):
            QtWidgets.QMessageBox.warning(self, 'Invalid name',
                                          'Batch name can only contain alphanumeric characters')
            return

        if start and name != '':
            batch_path = os.path.join(path, name)
            self.create_new_batch(batch_path)

    def create_new_batch(self, full_path: str):
        self.batch_path = full_path
        os.makedirs(self.batch_path)
        self.ui.listwBatch.clear()

        self.df = pandas.DataFrame(columns=['module', 'input_params', 'output', 'info', 'uuid', 'compressed'])
        self.df.to_pickle(os.path.join(self.batch_path, 'dataframe.batch'))

        self.setWindowTitle('Batch Manager: ' + os.path.basename(self.batch_path))
        self.ui.labelBatchPath.setText(os.path.dirname(self.batch_path))
        self.show()

    def btn_view_input_slot(self):
        # TODO: This should ask which viewer to display output in if more than 2 are open
        s = self.ui.listwBatch.currentItem()
        UUID = s.data(3)

        r = self.df.loc[self.df['uuid'] == UUID]

        viewers = get_window_manager().viewers

        if len(viewers) > 1:
            self.lwd = ListWidgetDialog()
            self.lwd.listWidget.addItems([str(i + 1) for i in range(len(viewers))])
            self.lwd.label.setText('Viewer to show input in:')
            self.lwd.btnOK.clicked.connect(partial(self.load_item_input, viewers, r))
        else:
            self.load_item_input(viewers[0], r)

    @present_exceptions('Cannot load input', 'The following occurred when trying to load the input')
    def load_item_input(self, viewers: Union[ViewerWindow, UserList], r: pandas.Series = None, UUID: uuid.UUID = None):
        """
        Pass either the batch DataFrame row or UUID of the item of which to load the input into a viewer

        :param viewers: ViewerWindow or list of ImageView
        :type viewers:  Union[ViewerWindow, UserList]

        :param  r:    Row of batch DataFrame corresponding to the selected item
        :type   r:    pandas.Series

        :param UUID:  UUID of the item to load input from
        :type  UUID:  uuid.UUID
        """

        if (r is None) and (UUID is None):
            raise TypeError('Must pass either one of batch item UUID or DataFrame row as Series object')
        elif r is None:
            r = self.df.loc[self.df['uuid'] == UUID]
        elif UUID is None:
            UUID = r['uuid']
            if isinstance(UUID, pandas.Series):
                UUID = UUID.item()

        if isinstance(viewers, ViewerWindow):
            viewer = viewers.viewer_reference
        elif isinstance(viewers, UserList):
            if self.lwd.listWidget.currentItem() is None:
                QtWidgets.QMessageBox.warning(self, 'Nothing selected', 'You must select from the list')
                return
            i = int(self.lwd.listWidget.currentRow())
            viewer = viewers[i].viewer_reference
        else:
            raise TypeError('Must pass pyqtgraphCore.ImageView instance or list of pyqtgraphCore.ImageView instances.')

        vi = ViewerUtils(viewer_reference=viewer)

        if r['input_item'].item() is None:
            if not vi.discard_workEnv():
                return
            pikpath = os.path.join(self.batch_path, str(UUID) + '_workEnv.pik')
            tiffpath = os.path.join(self.batch_path, str(UUID) + '.tiff')
            vi.viewer.status_bar_label.showMessage('Please wait, loading input into work environment...')
            if os.path.isfile(pikpath) and os.path.isfile(tiffpath):
                vi.viewer.workEnv = ViewerWorkEnv.from_pickle(pickle_file_path=pikpath, tiff_path=tiffpath)
                vi.update_workEnv()
                vi.enable_ui(True)
                vi.viewer.status_bar_label.showMessage('Done! loaded input into work environment.')
                vi.viewer.ui.label_curr_img_seq_name.setText('Input of item: ' + r['name'].item())

            else:
                QtWidgets.QMessageBox.warning(self, 'Input file does not exist',
                                              'The input files do not exist for this item.')
                vi.viewer.status_bar_label.showMessage('Error, could not load input into work environment.')
        if self.lwd is not None:
            self.lwd.close()
            self.lwd = None

    def on_list_widget_batch_doubleclicked(self, s: QtWidgets.QListWidgetItem):
        self.ui.scrollAreaOutputInfo.show()
        UUID = s.data(3)

        r = self.df.loc[self.df['uuid'] == UUID]

        m = r['module'].item()
        # m = globals()[module]

        output = self.get_batch_item_output(UUID)

        if output is None:
            return

        if output['status'] == 1:
            viewers = get_window_manager().viewers
            if len(get_window_manager().viewers) > 1:
                self.lwd = ListWidgetDialog()
                self.lwd.listWidget.addItems([str(i + 1) for i in range(len(viewers))])
                self.lwd.label.setText('Viewer to use for output:')
                self.lwd.btnOK.clicked.connect(partial(self.load_item_output, m, viewers, UUID))
            else:
                self.load_item_output(m, viewers[0], UUID)

    def load_item_output(self, module: str, viewers: Union[ViewerWindow, UserList], UUID: uuid.UUID):
        """
        Calls subclass of BatchRunInterface.show_output()
        :param module:      The module name under /batch_run_modules that the batch item is from
        :type  module:      str

        :param viewers: ViewerWindow or list of ImageView
        :type viewers:  Union[ViewerWindow, UserList]

        :param UUID:  UUID of the item to load input from
        :type  UUID:  uuid.UUID
        """
        if len(self.output_widgets) > 3:
            try:
                w = self.output_widgets.pop(0)
                w.deleteLater()
            except:
                pass

        module = globals()[module]

        if not isinstance(viewers, UserList):
            viewer = viewers.viewer_reference
        else:
            if self.lwd.listWidget.currentItem() is None:
                QtWidgets.QMessageBox.warning(self, 'Nothing selected', 'You must select from the list')
                return
            i = int(self.lwd.listWidget.currentRow())
            viewer = viewers[i].viewer_reference
        try:
            self.output_widgets.append(module.Output(self.batch_path, UUID, viewer))
        except:
            QtWidgets.QMessageBox.warning(self, 'Error showing item output',
                                          'The following error occured while '
                                          'trying to load the output of the chosen item\n' + traceback.format_exc())
        if self.lwd is not None:
            self.lwd.close()
            self.lwd = None

    def show_item_info(self, s: QtWidgets.QListWidgetItem):
        """Shows any info (such as the batch module's params) in the meta-info label"""
        if not isinstance(s, QtWidgets.QListWidgetItem):
            return
        UUID = s.data(3)
        row = self.df.loc[self.df['uuid'] == UUID]
        meta = row['info'].item()
        info = "\n".join([": ".join([key, str(val)]) for key, val in meta.items()])

        self.ui.textBrowserItemInfo.setText(str(UUID) + '\n\n' + info)

        output = self.get_batch_item_output(UUID)

        self.ui.textBrowserOutputInfo.setText('')

        if output is None:
            self.ui.textBrowserOutputInfo.setText('Output file does not exist for selected item')
            return
        else:
            self.ui.textBrowserOutputInfo.setText(str(output))

    def disable_ui_buttons(self, b):
        self.ui.btnStart.setDisabled(b)
        self.ui.btnStartAtSelection.setDisabled(b)
        self.ui.btnDelete.setDisabled(b)
        self.ui.btnAbort.setEnabled(b)

    def process_batch(self, start_ix: Union[int, uuid.UUID] = 0, clear_viewers=False):
        """Process everything in the batch by calling subclass of BatchRunInterface.process() for all items in batch
        :param start_ix:       Either DataFrame index (int) or UUID of the item to start from.
        :type  start_ix:       Union[int, uuid.UUID]

        :param clear_viewers:  Clear work environments in all viewers that are open
        :type  clear_viewers:  sbool
        """

        if isinstance(start_ix, (str, uuid.UUID)):
            try:
                ix = uuid.UUID(start_ix)
                start_ix = self.get_item_index(ix)
            except:
                raise TypeError('Argument stat_ix only accepts types int, UUID, or str representing a UUID')

        self.ui.checkBoxUseWorkDir.setDisabled(True)

        if len(self.df.index) == 0:
            return

        if not clear_viewers:
            if QtWidgets.QMessageBox.question(self, 'Clear all viewers?',
                                                  'Would you like to clear all viewer work '
                                                  'environments before starting the batch?',
                                                  QtWidgets.QMessageBox.No,
                                                  QtWidgets.QMessageBox.Yes) == QtWidgets.QMessageBox.Yes:
                self._clear_viewers()
        else:
            self._clear_viewers()

        self.current_batch_item_index = start_ix - 1
        self.disable_ui_buttons(True)
        # self.run_next_item()
        self.ui.scrollAreaStdOut.show()
        self.ui.scrollAreaOutputInfo.show()
        self.current_std_out = deque(maxlen=100)
        self.run_batch_item()

    def set_list_widget_item_color(self, ix: int, color: str):
        if color == 'orange':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#ffb347')))
        elif color == 'green':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#77dd77')))
        elif color == 'red':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#fe0d00')))
        elif color == 'blue':
            self.ui.listwBatch.item(ix).setBackground(QtGui.QBrush(QtGui.QColor('#85e3ff')))

    def _clear_viewers(self):
        for viewer in get_window_manager().viewers:
            vi = ViewerUtils(viewer.viewer_reference)
            vi.discard_workEnv()

    @QtCore.pyqtSlot()
    def run_batch_item(self):
        if self.current_batch_item_index > -1:
            UUID = self.df.iloc[self.current_batch_item_index]['uuid']
            output = self.get_batch_item_output(UUID)

            if output is None:
                self.set_list_widget_item_color(ix=self.current_batch_item_index, color='orange')
                if self._use_workdir:
                    # cleanup workdir
                    self.move_files([], UUID)

            elif output['status']:
                if 'output_files' in output.keys() and self._use_workdir:# and os.path.isdir(self.working_dir):
                    output_files_list = output['output_files']

                    mp = self.move_files(output_files_list, UUID)
                    self.set_list_widget_item_color(ix=self.current_batch_item_index, color='blue')
                    mp.finished.connect(partial(self.set_list_widget_item_color, self.current_batch_item_index, 'green'))

                else:
                    self.set_list_widget_item_color(ix=self.current_batch_item_index, color='green')
            else:
                self.set_list_widget_item_color(ix=self.current_batch_item_index, color='red')
                if self._use_workdir:
                    # cleanup workdir
                    self.move_files([f'{UUID}.out'], UUID)

        self.current_batch_item_index += 1
        self.ui.progressBar.setValue(int(self.current_batch_item_index / len(self.df.index) * 100))

        if self.current_batch_item_index == len(self.df.index):
            self.batch_finished()
            return

        r = self.df.iloc[self.current_batch_item_index]

        self.process = QtCore.QProcess()
        self.process.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        # self.process.readyReadStandardError.connect(partial(self.print_qprocess_std_err, self.process))
        self.process.readyReadStandardOutput.connect(partial(self.print_qprocess_std_out, self.process))

        self.process.finished.connect(self.run_batch_item)

        sh_file = self.create_runscript(r, cp=True, mv=False, use_subdir=False)

        self.process.setWorkingDirectory(self.working_dir)
        self.process.start(sh_file)
        self.ui.listwBatch.item(self.current_batch_item_index).setBackground(QtGui.QBrush(QtGui.QColor('yellow')))

    def move_files(self, files: list, UUID) -> QtCore.QProcess:
        shell_str = '#!/bin/bash\n'

        for f in files:
            src = os.path.join(self.working_dir, f)
            dst = os.path.join(self.batch_path, f)
            shell_str += f'mv -n {src} {dst}\n'
        u = f'*{UUID}*'
        shell_str += f'rm {os.path.join(self.working_dir, u)}'
        move_file = os.path.join(self.working_dir, 'move.sh')

        with(open(move_file, 'w')) as sh_mv_f:
            sh_mv_f.write(shell_str)

        mv_st = os.stat(move_file)
        os.chmod(move_file, mv_st.st_mode | S_IEXEC)

        move_process = QtCore.QProcess()
        move_process.setWorkingDirectory(self.working_dir)
        move_process.start(move_file)
        self.move_processes.append(move_process)
        move_process.finished.connect(partial(self.move_processes.remove, move_process))

        return move_process

    def batch_finished(self):
        self.ui.progressBar.setValue(100)
        self.disable_ui_buttons(False)
        self.ui.checkBoxUseWorkDir.setEnabled(True)
        QtWidgets.QMessageBox.information(self, 'Batch is done!', 'Yay, your batch has finished processing!')

    def set_workdir(self, ev):
        if ev:
            try:
                self.working_dir = make_workdir('batch_manager')
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, 'Cannot create Work Dir',
                                              f'Could not create a work directory. {e}')
                self.ui.checkBoxUseWorkDir.setChecked(False)
                self.working_dir = self.batch_path
            else:
                self._use_workdir = True

        else:
            self.working_dir = self.batch_path
            self._use_workdir = False

    def create_runscript(self, r, cp: bool, mv: bool, use_subdir: bool = True) -> str:
        m = globals()[r['module']]
        module_path = os.path.abspath(m.__file__)
        u = r['uuid']

        if cp:
            files = os.path.join(self.batch_path, f"*{u}*")
            cp_str = f'cp {files} {self.working_dir}\nexport CURR_BATCH_DIR={self.batch_path}'
        else:
            cp_str = None

        if mv:
            work_files = os.path.join(self.working_dir, f'*{u}*')
            mv_str = '\n'.join([f'mv -n {work_files} {self.batch_path}', f'rm *{u}*'])
        else:
            mv_str = None

        args = f'"{self.working_dir}" "{u}"'
        if use_subdir:
            savedir = os.path.join(self.batch_path, f'jobs_{get_timestamp_str()}')
        else:
            savedir = self.batch_path

        return make_runfile(module_path=module_path,
                            savedir=savedir,
                            args_str=args,
                            filename=f'{u}.sh',
                            pre_run=cp_str,
                            post_run=mv_str)

    def export_submission_scripts(self):
        to_copy = self.ui.checkBoxUseWorkDir.isChecked()
        to_move = to_copy
        for ix, r in self.df.iterrows():
            self.create_runscript(r, cp=to_copy, mv=to_move)

        QtWidgets.QMessageBox.information(self, 'Exported',
                                          'Submission scripts for this batch '
                                          'have been exported to a jobs dir in your batch dir')

    def get_batch_item_output(self, UUID: uuid.UUID):
        if self.working_dir is not None:
            out_file = os.path.join(self.working_dir, f'{UUID}.out')
            if os.path.isfile(out_file):
                output = json.load(open(out_file, 'r'))
                return output

        out_file = os.path.join(self.batch_path, f'{UUID}.out')

        if os.path.isfile(out_file):
            output = json.load(open(out_file, 'r'))
            return output
        else:
            return None

    def _terminate_qprocess(self):
        try:
            py_proc = psutil.Process(self.process.pid()).children()[0].pid
        except psutil.NoSuchProcess:
            return
        children = psutil.Process(py_proc).children()
        os.kill(py_proc, SIGKILL)
        for child in children:
            os.kill(child.pid, SIGKILL)

    def print_qprocess_std_out(self, proc):
        text = proc.readAllStandardOutput().data().decode('utf8')
        # self.current_std_out.append(text)
        self.ui.textBrowserStdOut.append(text)

    def add_item(self, module: str, input_workEnv: ViewerWorkEnv, input_params: dict, name: str='', info: dict ='') -> uuid.UUID:
        """
        Add an item to the currently open batch

        :param  module:         The module to run from /batch_run_modules.
        :type   module:         str

        :param  input_workEnv:  Input workEnv that the module will use
        :type   input_workEnv:  ViewerWorkEnv

        :param  input_params:   Input params that the module will use. Depends on your subclass of BatchRunInterface.process() method
        :type   input_params:   dict

        :param  name:           A name for the batch item
        :param  name:           str

        :param  info:           A dictionary with any metadata information to display in the scroll area label.
        :param  info:           str

        :return:                UUID of the added item
        """
        if input_workEnv.isEmpty:
            QtWidgets.QMessageBox.warning(self, 'Work Environment is empty!', 'The current work environment is empty,'
                                                                              ' nothing to add to the batch!')
            return
        # vi = ViewerUtils(viewer_reference)
        UUID = uuid.uuid4()

        if module == 'CNMFE' or module == 'caiman_motion_correction' or module == 'CNMF':
            filename = os.path.join(self.batch_path, str(UUID) + '.tiff')
            tifffile.imsave(filename, data=input_workEnv.imgdata.seq.T, bigtiff=True)
            input_workEnv.to_pickle(self.batch_path, filename=str(UUID) + '_workEnv', save_img_seq=False, UUID=None)

        pickle.dump(input_params, open(os.path.join(self.batch_path, str(UUID) + '.params'), 'wb'), protocol=4)

        input_params = np.array(input_params, dtype=object)
        # meta = np.array(info, dtype=object)

        self.df = self.df.append({'module': module,
                                  'name': name,
                                  'input_item': None,
                                  'input_params': input_params,
                                  'info': info,
                                  'uuid': UUID,
                                  'output': None,
                                  }, ignore_index=True)

        assert isinstance(self.df, pandas.DataFrame)

        self.ui.listwBatch.addItem(module + ': ' + name)
        n = self.ui.listwBatch.count()
        item = self.ui.listwBatch.item(n - 1)
        assert isinstance(item, QtWidgets.QListWidgetItem)
        item.setData(3, UUID)

        self.df.to_pickle(self.batch_path + '/dataframe.batch')
        return UUID

    def del_item(self):
        # """Delete the currently selected item from the batch and any corresponding dependents of the item's output"""
        if QtWidgets.QMessageBox.question(self, 'Confirm deletion',
                                          'Are you sure you want to delete the selected item from the batch? '
                                          'This will also remove ALL files associated to the item',
                                          QtWidgets.QMessageBox.Yes,
                                          QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
            return
        s = self.ui.listwBatch.currentItem()
        UUID = s.data(3)

        assert isinstance(self.df, pandas.DataFrame)

        dependents = self.df.loc[self.df['input_item'] == UUID]
        if not dependents.empty:
            if QtWidgets.QMessageBox.warning(self, 'This item has dependents!',
                                             'There are other items in your batch list that are dependent on the item you '
                                             'have selected to delete. If you delete this item from the batch then all '
                                             'dependent items will also be deleted.\n\nDo you still wish to continue?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return

            for item in self.ui.listwBatch.items():
                if item.data(3) == UUID:
                    ix = self.ui.listwBatch.indexFromItem(item).row()
                    self.ui.listwBatch.takeItem(ix)

            self.df = self.df.loc[self.df['input_item'] != UUID]

        self.df = self.df[self.df['uuid'] != UUID]
        self.df.reset_index(drop=True, inplace=True)

        ix = self.ui.listwBatch.indexFromItem(s).row()
        self.ui.listwBatch.takeItem(ix)

        for file in glob(self.batch_path + '/*' + str(UUID) + '*'):
            os.remove(file)

        self.df.to_pickle(self.batch_path + '/dataframe.batch')

    def save_batch(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save Batch as', '', '(*.batch)')
        if path == '':
            return

        if path[0].endswith('.batch'):
            path = path[0]
        else:
            path = path[0] + '.batch'

        try:
            d = {'batch_path': self.batch_path,
                 'df': self.df}
            pickle.dump(d, open(path[0]))
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File save Error', 'Unable to save the file\n' + str(e))

    def open_batch(self):
        if self.ui.listwBatch.count() > 0:
            if QtWidgets.QMessageBox.warning(self, 'Open Batch', 'Close the current batch and open a new one?',
                                             QtWidgets.QMessageBox.Yes,
                                             QtWidgets.QMessageBox.No) == QtWidgets.QMessageBox.No:
                return
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Open Batch', directory='/home/')
        if path == '':
            return

        if any(s in path for s in [' ', '(', ')', '?']):
            QtWidgets.QMessageBox.warning(self, 'Invalid batch path', 'Batch path can only contain alphanumeric characters')
            return
        self.open_batch_dir(path)

    def open_batch_dir(self, path: str):
        dfpath = path + '/dataframe.batch'
        if not os.path.isfile(dfpath):
            QtWidgets.QMessageBox.warning(self, 'Invalid batch dir',
                                          'The selected directory does not appear to be a valid  batch directory '
                                          'since it does not contain a "dataframe.batch" file')
            return
        try:
            df = pandas.read_pickle(dfpath)
            self.df = df
            if 'compressed' not in self.df.columns:
                self.df['compressed'] = False * self.df.index.size
            self.batch_path = path
            self.setWindowTitle('Batch Manager: ' + os.path.basename(self.batch_path))
            self.ui.labelBatchPath.setText(os.path.dirname(self.batch_path))

            self.ui.listwBatch.clear()

            for ix, r in self.df.iterrows():
                self.ui.listwBatch.addItem(r['module'] + ': ' + r['name'])
                n = self.ui.listwBatch.count()
                item = self.ui.listwBatch.item(n - 1)
                item.setData(3, r['uuid'])

                output = self.get_batch_item_output(r['uuid'])

                if output is None:
                    continue
                elif output['status']:
                    self.ui.listwBatch.item(n - 1).setBackground(
                        QtGui.QBrush(QtGui.QColor('#77dd77'))) # green
                else:
                    self.ui.listwBatch.item(n - 1).setBackground(
                        QtGui.QBrush(QtGui.QColor('#fe0d00'))) # red

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'File open Error!',
                                          'Could not open the dataframe file.\n' + traceback.format_exc())
            return

    def reset_list_widget_colors(self):
        for ix, r in self.df.iterrows():
            item = self.ui.listwBatch.item(ix)

            output = self.get_batch_item_output(r['uuid'])

            if output is None:
                item.setBackground(QtGui.QBrush(QtGui.QColor('#FFFFFF')))
            elif output['status']:
                item.setBackground(QtGui.QBrush(QtGui.QColor('#77dd77')))  # green
            else:
                item.setBackground(QtGui.QBrush(QtGui.QColor('#fe0d00')))  # red

    def init_compressor(self):
        self.thread_pool_compressor = QtCore.QThreadPool()
        self.thread_pool_compressor.setMaxThreadCount(10)
        self.thread_pool_compressor.start()
