# -*- coding: utf-8 -*-
from ...Qt import QtGui, QtCore, QtWidgets
from spyder.widgets.variableexplorer.objecteditor import oedit
from .common import *
import traceback
from functools import partial
from ....analysis import Transmission
from ....common import get_project_manager
import os


class LoadProjDF(CtrlNode):
    """Load raw project DataFrames as Transmission"""
    nodeName = 'Load_Proj_DF'
    uiTemplate = [('DF_Name', 'combo'),
                  ('Update', 'button', {'text': 'Update', 'toolTip': 'When clicked this node will update'
                                                                     ' from the project DataFrame'}),
                  ('Apply', 'check', {'applyBox': True, 'checked': False}),
                  ('PinDF', 'check', {'text': 'Yes', 'toolTip': 'Pin the DataFrame to the flowchart, this way\n'
                                                                'you can open another project and still propogate\n'
                                                                'the data from this node.'})]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'Out': {'io': 'out'}})
        self._loadNode = True
        self.t = None
        child_df_names = ['root'] + list(get_project_manager().child_dataframes.keys())
        self.ctrls['DF_Name'].addItems(child_df_names)
        self.ctrls['Update'].clicked.connect(self.changed)
        # print('Node Refs:')
        # print(configuration.df_refs)

    def process(self):
        if self.ctrls['Apply'].isChecked() is False:
            return self.t

        # print('#######Weak Refs Dict########')
        # print(configuration.df_refs)

        if self.ctrls['PinDF'].isEnabled():
            if self.ctrls['PinDF'].isChecked():
                # self.t = self.t.copy()
                self.ctrls['PinDF'].setDisabled(True)
                self.ctrls['Update'].setDisabled(True)
                return {'Out': self.t}

            if self.ctrls['DF_Name'].currentText() == '':
                return
            child_df_name = self.ctrls['DF_Name'].currentText()
            if child_df_name == 'root':
                df = get_project_manager().dataframe
                filter_history = None
            else:
                df = get_project_manager().child_dataframes[child_df_name]['dataframe']
                filter_history = get_project_manager().child_dataframes[child_df_name]['filter_history']
            proj_path = get_project_manager().root_dir
            # print('*****************config df ref hex ID:*****************')
            # print(hex(id(df)))
            self.t = Transmission.from_proj(proj_path, df, sub_dataframe_name=child_df_name,
                                            dataframe_filter_history={'dataframe_filter_history': filter_history})

            # print('Tranmission dataframe hexID:')
            # print(hex(id(self.t.df)))

        return {'Out': self.t}


class LoadFile(CtrlNode):
    """Load Transmission data object from pickled file"""
    nodeName = 'LoadFile'
    uiTemplate = [('load_trn', 'button', {'text': 'Open .trn File'}),
                  ('fname', 'label', {'text': ''}),
                  ('proj_path', 'button', {'text': 'Project Path'}),
                  ('proj_path_label', 'label', {'text': ''})
                  ]

    def __init__(self, name):
        CtrlNode.__init__(self, name, terminals={'Out': {'io': 'out'}})
        self.ctrls['load_trn'].clicked.connect(self.file_dialog_trn_file)
        self.ctrls['proj_path'].clicked.connect(self.dir_dialog_proj_path)

        self.t = None
        self._loadNode = True

    def file_dialog_trn_file(self):
        path = QtWidgets.QFileDialog.getOpenFileName(None, 'Import Transmission object', '', '(*.trn)')
        if path == '':
            return
        try:
            self.t = Transmission.from_hdf5(path[0])
        except:
            QtWidgets.QMessageBox.warning(None, 'File open Error!', 'Could not open the chosen file.\n' + traceback.format_exc())
            return

        self.ctrls['fname'].setText(os.path.basename(path[0]))

        proj_path = get_project_manager().root_dir
        if proj_path is not None:
            self._set_proj_path(proj_path)

        # print(self.transmission)
        # self.update()
        self.changed()

    def _set_proj_path(self, path: str):
        self.ctrls['proj_path_label'].setText(os.path.basename(path))
        self.t.set_proj_path(path)
        self.t.set_proj_config()

    def dir_dialog_proj_path(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Project Folder')

        if path == '':
            return

        try:
            self._set_proj_path(path)
            self.changed()
        except (FileNotFoundError, NotADirectoryError) as e:
            QtWidgets.QMessageBox.warning(None, 'Invalid Project Folder', 'This is not a valid Mesmerize project\n' + e)
            return

    def process(self):
        self.t.get_proj_path()
        return {'Out': self.t}


class Save(CtrlNode):
    """Save Transmission data object"""
    nodeName = 'Save'
    uiTemplate = [('saveBtn', 'button', {'text': 'OpenFileDialog'}),
                  ('path', 'label', {'text' : ''}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})
                  ]

    def __init__(self, name):
        # super(Save, self).__init__(name, terminals={'data': {'io': 'in'}})
        CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}})
        self._bypass = False
        self.bypassButton = None
        self.ctrls['saveBtn'].clicked.connect(self._fileDialog)
        self._saveNode = True
        self.saveValue = None

    def process(self, In, display=True):
        if In is not None:
            self._save(In)
        else:
            raise Exception('No incoming transmission to save!')

    def _fileDialog(self):
        path = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Transmission as', '', '(*.trn)')
        if path == '':
            return
        if path[0].endswith('.trn'):
            path = path[0]
        else:
            path = path[0] + '.trn'

        self.ctrls['path'].setText(path)

    def _save(self, transmission):
        # self.ctrls['saveBtn'].clicked.connect(self._fileDialog)
        if self.ctrls['Apply'].isChecked is False:
            return

        if self.ctrls['path'].text() != '':
            try:
                transmission.to_hdf5(self.ctrls['path'].text())
            except:
                QtWidgets.QMessageBox.warning(None, 'File save error', 'Could not save the transmission to file.\n' + traceback.format_exc())


class Merge(CtrlNode):
    """Merge transmissions"""
    nodeName = 'Merge'
    uiTemplate = [('Apply', 'check', {'checked': False, 'applyBox': True})]

    def process(self, **kwargs):
        self.transmissions = kwargs['In']
        self.transmissions_list = merge_transmissions(self.transmissions)

        self.t = Transmission.merge(self.transmissions_list)

        return {'Out': self.t}


class ViewTransmission(CtrlNode):
    """View/Edit transmission using the spyder object editor"""
    nodeName = 'ViewData'
    uiTemplate = [('No controls', 'label')]

    # def __init__(self, name):
    #     CtrlNode.__init__(self, name, terminals={'In':})

    def processData(self, transmission: Transmission):
        self.t = transmission.copy()
        edited = oedit({'dataframe': self.t.df, 'history_trace': self.t.history_trace})
        if edited is not None:
            self.t.df = edited['dataframe']
            self.t.history_trace.add_operation('all', 'object_editor', {})

        return self.t


class DropNa(CtrlNode):
    """Drop NaNs from the DataFrame"""
    nodeName = 'DropNaNs'
    uiTemplate = [('axis', 'combo', {'values': ['row', 'columns'], 'toolTip': 'Choose to drop NaNs from according to all '
                                                                              'rows, columns, or a specific column'}),
                  ('how', 'combo', {'values': ['any', 'all'], 'toolTip': 'any: drop from chosen axis if any element is NaN\n'
                                                                         'all: drop from chosen axis if all elements are NaN'}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    def __init__(self, *args, **kwargs):
        super(DropNa, self).__init__(*args, **kwargs)

    def processData(self, transmission: Transmission):
        items = ['row', 'columns'] + ['---------'] + transmission.df.columns.to_list()
        self.ctrls['axis'].setItems(items)

        if not self.ctrls['Apply'].isChecked():
            return

        self.t = transmission.copy()

        axis = self.ctrls['axis'].currentText()

        if self.ctrls['axis'].currentIndex() < 2:
            if axis == 'row':
                axis = 0
            elif axis == 'columsn':
                axis = 1

            how = self.ctrls['how'].currentText()
            self.t.df.dropna(axis=axis, how=how, inplace=True)
        else:
            how = None
            self.t.df = self.t.df[~self.t.df[axis].isna()]

        self.t.history_trace.add_operation('all', 'dropna', parameters={'axis': axis, 'how': how})

        return self.t


class iloc(CtrlNode):
    """Pass only one or multiple DataFrame Indices"""
    nodeName = 'iloc'
    uiTemplate = [('Index', 'intSpin', {'min': 0, 'step': 1, 'value': 0}),
                  ('Indices', 'lineEdit', {'text': '0', 'toolTip': 'Index numbers separated by commas'})
                  ]

    def processData(self, transmission):
        self.ctrls['Index'].setMaximum(len(transmission.df.index) - 1)
        self.ctrls['Index'].valueChanged.connect(
            partial(self.ctrls['Indices'].setText, str(self.ctrls['Index'].value())))

        indices = [int(ix.strip()) for ix in self.ctrls['Indices'].text().split(',')]
        t = transmission.copy()
        t.df = t.df.iloc[indices, :]
        t.src.append({'DF_IDX': {'indices': indices}})
        return t


class SelectRows(CtrlNode):
    pass


class SelectColumns(CtrlNode):
    pass


class TextFilter(CtrlNode):
    nodeName = 'TextFilter'
    uiTemplate = [('Column', 'combo', {'toolTip': 'Filter according to this column'}),
                  ('filter', 'lineEdit', {'toolTip': 'Filter to apply in selected column'}),
                  ('Include', 'radioBtn', {'checked': True}),
                  ('Exclude', 'radioBtn', {'checked': False}),
                  ('Apply', 'check', {'checked': False, 'applyBox': True})]

    # def __init__(self, name):
    #     CtrlNode.__init__(self, name, terminals={'In': {'io': 'in'}, 'Out': {'io': 'out', 'bypass': 'In'}})
    #     self.ctrls['ROI_Type'].returnPressed.connect(self._setAvailTags)

    def processData(self, transmission):
        self.ctrls['Column'].setItems(transmission.df.columns.to_list())
        col = self.ctrls['Column'].currentText()
        completer = QtWidgets.QCompleter(list(map(str, transmission.df[col].unique())))
        self.ctrls['filter'].setCompleter(completer)

        if self.ctrls['Apply'].isChecked() is False:
            return

        filt = self.ctrls['filter'].text()

        self.t = transmission.copy()

        include = self.ctrls['Include'].isChecked()
        exclude = self.ctrls['Exclude'].isChecked()

        params = {'column': col,
                  'filter': filt,
                  'include': include,
                  'exclude': exclude
                  }

        if include:
            self.t.df = self.t.df[self.t.df[col].astype(str) == filt]
        elif exclude:
            self.t.df = self.t.df[self.t.df[col].astype(str) != filt]

        self.t.df = self.t.df.reset_index(drop=True)

        self.t.history_trace.add_operation('all', operation='text_filter', parameters=params)

        return self.t


# class ColumnSelectNode(Node):
#     """Select named columns from a record array or MetaArray."""
#     nodeName = "ColumnSelect"
#     def __init__(self, name):
#         Node.__init__(self, name, terminals={'In': {'io': 'in'}})
#         self.columns = set()
#         self.columnList = QtGui.QListWidget()
#         self.axis = 0
#         self.columnList.itemChanged.connect(self.itemChanged)
#
#     def process(self, In, display=True):
#         if display:
#             self.updateList(In)
#
#         out = {}
#         if hasattr(In, 'implements') and In.implements('MetaArray'):
#             for c in self.columns:
#                 out[c] = In[self.axis:c]
#         elif isinstance(In, np.ndarray) and In.dtype.fields is not None:
#             for c in self.columns
#                 out[c] = In[c]
#         else:
#             self.In.setValueAcceptable(False)
#             raise Exception("Input must be MetaArray or ndarray with named fields")
#
#         return out
#
#     def ctrlWidget(self):
#         return self.columnList
#
#     def updateList(self, data):
#         if hasattr(data, 'implements') and data.implements('MetaArray'):
#             cols = data.listColumns()
#             for ax in cols:  ## find first axis with columns
#                 if len(cols[ax]) > 0:
#                     self.axis = ax
#                     cols = set(cols[ax])
#                     break
#         else:
#             cols = list(data.dtype.fields.keys())
#
#         rem = set()
#         for c in self.columns:
#             if c not in cols:
#                 self.removeTerminal(c)
#                 rem.add(c)
#         self.columns -= rem
#
#         self.columnList.blockSignals(True)
#         self.columnList.clear()
#         for c in cols:
#             item = QtGui.QListWidgetItem(c)
#             item.setFlags(QtCore.Qt.ItemIsEnabled|QtCore.Qt.ItemIsUserCheckable)
#             if c in self.columns:
#                 item.setCheckState(QtCore.Qt.Checked)
#             else:
#                 item.setCheckState(QtCore.Qt.Unchecked)
#             self.columnList.addItem(item)
#         self.columnList.blockSignals(False)
#
#
#     def itemChanged(self, item):
#         col = str(item.text())
#         if item.checkState() == QtCore.Qt.Checked:
#             if col not in self.columns:
#                 self.columns.add(col)
#                 self.addOutput(col)
#         else:
#             if col in self.columns:
#                 self.columns.remove(col)
#                 self.removeTerminal(col)
#         self.update()
#
#     def saveState(self):
#         state = Node.saveState(self)
#         state['columns'] = list(self.columns)
#         return state
#
#     def restoreState(self, state):
#         Node.restoreState(self, state)
#         self.columns = set(state.get('columns', []))
#         for c in self.columns:
#             self.addOutput(c)
#
#
#
# class RegionSelectNode(CtrlNode):
#     """Returns a slice from a 1-D array. Connect the 'widget' output to a plot to display a region-selection widget."""
#     nodeName = "RegionSelect"
#     uiTemplate = [
#         ('start', 'spin', {'value': 0, 'step': 0.1}),
#         ('stop', 'spin', {'value': 0.1, 'step': 0.1}),
#         ('display', 'check', {'value': True}),
#         ('movable', 'check', {'value': True}),
#     ]
#
#     def __init__(self, name):
#         self.items = {}
#         CtrlNode.__init__(self, name, terminals={
#             'data': {'io': 'in'},
#             'selected': {'io': 'out'},
#             'region': {'io': 'out'},
#             'widget': {'io': 'out', 'multi': True}
#         })
#         self.ctrls['display'].toggled.connect(self.displayToggled)
#         self.ctrls['movable'].toggled.connect(self.movableToggled)
#
#     def displayToggled(self, b):
#         for item in self.items.values():
#             item.setVisible(b)
#
#     def movableToggled(self, b):
#         for item in self.items.values():
#             item.setMovable(b)
#
#
#     def process(self, data=None, display=True):
#         #print "process.."
#         s = self.stateGroup.state()
#         region = [s['start'], s['stop']]
#
#         if display:
#             conn = self['widget'].connections()
#             for c in conn:
#                 plot = c.node().getPlot()
#                 if plot is None:
#                     continue
#                 if c in self.items:
#                     item = self.items[c]
#                     item.setRegion(region)
#                     #print "  set rgn:", c, region
#                     #item.setXVals(events)
#                 else:
#                     item = LinearRegionItem(values=region)
#                     self.items[c] = item
#                     #item.connect(item, QtCore.SIGNAL('regionChanged'), self.rgnChanged)
#                     item.sigRegionChanged.connect(self.rgnChanged)
#                     item.setVisible(s['display'])
#                     item.setMovable(s['movable'])
#                     #print "  new rgn:", c, region
#                     #self.items[c].setYRange([0., 0.2], relative=True)
#
#         if self['selected'].isConnected():
#             if data is None:
#                 sliced = None
#             elif (hasattr(data, 'implements') and data.implements('MetaArray')):
#                 sliced = data[0:s['start']:s['stop']]
#             else:
#                 mask = (data['time'] >= s['start']) * (data['time'] < s['stop'])
#             sliced = data[mask]
#         else:
#             sliced = None
#
#         return {'selected': sliced, 'widget': self.items, 'region': region}
#
#
#     def rgnChanged(self, item):
#         region = item.getRegion()
#         self.stateGroup.setState({'start': region[0], 'stop': region[1]})
#         self.update()
#
#
# class EvalNode(Node):
#     """Return the output of a string evaluated/executed by the python interpreter.
#     The string may be either an expression or a python script, and inputs are accessed as the name of the terminal.
#     For expressions, a single value may be evaluated for a single output, or a dict for multiple outputs.
#     For a script, the text will be executed as the body of a function."""
#     nodeName = 'PythonEval'
#
#     def __init__(self, name):
#         Node.__init__(self, name,
#             terminals = {
#                 'input': {'io': 'in', 'renamable': True, 'multiable': True},
#                 'output': {'io': 'out', 'renamable': True, 'multiable': True},
#             },
#             allowAddInput=True, allowAddOutput=True)
#
#         self.ui = QtGui.QWidget()
#         self.layout = QtGui.QGridLayout()
#         #self.addInBtn = QtGui.QPushButton('+Input')
#         #self.addOutBtn = QtGui.QPushButton('+Output')
#         self.text = QtGui.QTextEdit()
#         self.text.setTabStopWidth(30)
#         self.text.setPlainText("# Access inputs as args['input_name']\nreturn {'output': None} ## one key per output terminal")
#         #self.layout.addWidget(self.addInBtn, 0, 0)
#         #self.layout.addWidget(self.addOutBtn, 0, 1)
#         self.layout.addWidget(self.text, 1, 0, 1, 2)
#         self.ui.setLayout(self.layout)
#
#         #QtCore.QObject.connect(self.addInBtn, QtCore.SIGNAL('clicked()'), self.addInput)
#         #self.addInBtn.clicked.connect(self.addInput)
#         #QtCore.QObject.connect(self.addOutBtn, QtCore.SIGNAL('clicked()'), self.addOutput)
#         #self.addOutBtn.clicked.connect(self.addOutput)
#         self.text.focusOutEvent = self.focusOutEvent
#         self.lastText = None
#
#     def ctrlWidget(self):
#         return self.ui
#
#     #def addInput(self):
#         #Node.addInput(self, 'input', renamable=True)
#
#     #def addOutput(self):
#         #Node.addOutput(self, 'output', renamable=True)
#
#     def focusOutEvent(self, ev):
#         text = str(self.text.toPlainText())
#         if text != self.lastText:
#             self.lastText = text
#             self.update()
#         return QtGui.QTextEdit.focusOutEvent(self.text, ev)
#
#     def process(self, display=True, **args):
#         l = locals()
#         l.update(args)
#         output = None
#         ## try eval first, then exec
#         try:
#             text = str(self.text.toPlainText()).replace('\n', ' ')
#             output = eval(text, globals(), l)
#         except SyntaxError:
#             fn = "def fn(**args):\n"
#             run = "\noutput=fn(**args)\n"
#             text = fn + "\n".join(["    "+l for l in str(self.text.toPlainText()).split('\n')]) + run
#             exec(text)
#         except:
#             print("Error processing node: %s" % self.name())
#             raise
#         return output
#
#     def saveState(self):
#         state = Node.saveState(self)
#         state['text'] = str(self.text.toPlainText())
#         #state['terminals'] = self.saveTerminals()
#         return state
#
#     def restoreState(self, state):
#         Node.restoreState(self, state)
#         self.text.clear()
#         self.text.insertPlainText(state['text'])
#         self.restoreTerminals(state['terminals'])
#         self.update()
#
# class ColumnJoinNode(Node):
#     """Concatenates record arrays and/or adds new columns"""
#     nodeName = 'ColumnJoin'
#
#     def __init__(self, name):
#         Node.__init__(self, name, terminals = {
#             'output': {'io': 'out'},
#         })
#
#         #self.items = []
#
#         self.ui = QtGui.QWidget()
#         self.layout = QtGui.QGridLayout()
#         self.ui.setLayout(self.layout)
#
#         self.tree = TreeWidget()
#         self.addInBtn = QtGui.QPushButton('+ Input')
#         self.remInBtn = QtGui.QPushButton('- Input')
#
#         self.layout.addWidget(self.tree, 0, 0, 1, 2)
#         self.layout.addWidget(self.addInBtn, 1, 0)
#         self.layout.addWidget(self.remInBtn, 1, 1)
#
#         self.addInBtn.clicked.connect(self.addInput)
#         self.remInBtn.clicked.connect(self.remInput)
#         self.tree.sigItemMoved.connect(self.update)
#
#     def ctrlWidget(self):
#         return self.ui
#
#     def addInput(self):
#         #print "ColumnJoinNode.addInput called."
#         term = Node.addInput(self, 'input', renamable=True, removable=True, multiable=True)
#         #print "Node.addInput returned. term:", term
#         item = QtGui.QTreeWidgetItem([term.name()])
#         item.term = term
#         term.joinItem = item
#         #self.items.append((term, item))
#         self.tree.addTopLevelItem(item)
#
#     def remInput(self):
#         sel = self.tree.currentItem()
#         term = sel.term
#         term.joinItem = None
#         sel.term = None
#         self.tree.removeTopLevelItem(sel)
#         self.removeTerminal(term)
#         self.update()
#
#     def process(self, display=True, **args):
#         order = self.order()
#         vals = []
#         for name in order:
#             if name not in args:
#                 continue
#             val = args[name]
#             if isinstance(val, np.ndarray) and len(val.dtype) > 0:
#                 vals.append(val)
#             else:
#                 vals.append((name, None, val))
#         return {'output': functions.concatenateColumns(vals)}
#
#     def order(self):
#         return [str(self.tree.topLevelItem(i).text(0)) for i in range(self.tree.topLevelItemCount())]
#
#     def saveState(self):
#         state = Node.saveState(self)
#         state['order'] = self.order()
#         return state
#
#     def restoreState(self, state):
#         Node.restoreState(self, state)
#         inputs = self.inputs()
#
#         ## Node.restoreState should have created all of the terminals we need
#         ## However: to maintain support for some older flowchart files, we need
#         ## to manually add any terminals that were not taken care of.
#         for name in [n for n in state['order'] if n not in inputs]:
#             Node.addInput(self, name, renamable=True, removable=True, multiable=True)
#         inputs = self.inputs()
#
#         order = [name for name in state['order'] if name in inputs]
#         for name in inputs:
#             if name not in order:
#                 order.append(name)
#
#         self.tree.clear()
#         for name in order:
#             term = self[name]
#             item = QtGui.QTreeWidgetItem([name])
#             item.term = term
#             term.joinItem = item
#             #self.items.append((term, item))
#             self.tree.addTopLevelItem(item)
#
#     def terminalRenamed(self, term, oldName):
#         Node.terminalRenamed(self, term, oldName)
#         item = term.joinItem
#         item.setText(0, term.name())
#         self.update()


