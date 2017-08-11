'''
Main @ ui

The main user interface for the Maya checklist

=========================================================
@command:
-----------------------
import mayaChecklist.ui.main
mayaChecklist.ui.main.main()
-----------------------

@requires: 
*   Qt.py file from https://github.com/mottosso/Qt.py (MIT license)


@todo: 
*   Rename tab functionality
*   Sort by check/archive checks
*   Sort by frame
*   Add color functionality
*   Reorder checklist item functionality
*   Save to/load from
*   Create template checklists

=========================================================
Maya Tanaka
'''

import maya.cmds as mc
import pymel.core as pm

import json

from maya import OpenMayaUI as omui
from Qt import QtWidgets, QtCore, QtGui
import Qt

#    logging lets us define many different inputs and outputs
#    It is a print statement on steroids
import logging
#    Any logging errors go to standard error output, and anything else
#    just goes to output
logging.basicConfig()
logger = logging.getLogger('MayaChecklist')
logger.setLevel(logging.DEBUG)


if Qt.__binding__ == 'PySide':
    #    shiboken converts Qt elements into PySide elements
    from shiboken import wrapInstance
elif Qt.__binding__.startswith('PyQt'):
    #    sip converts Qt elements into PyQt
    from sip import wrapinstance as wrapInstance
else:
    from shiboken2 import wrapInstance


def get_maya_main_window():
    #    Get the memory address of the main window
    win = omui.MQtUtil_mainWindow()

    #    Convert it into a wrap instance
    mainWindowPointer = wrapInstance(long(win), QtWidgets.QMainWindow)
    return mainWindowPointer


class MayaChecklistUI(QtWidgets.QMainWindow):

    WINDOWTITLE = 'Maya Checklist'
    OBJECTNAME = 'mayaChecklistUI'

    TABS = dict()

    def __init__(self, parent = None):

        #   Delete previous windows
        try:
            pm.deleteUI(self.OBJECTNAME)
        except:
            print('No previous window')

        super(MayaChecklistUI, self).__init__(parent = parent)
        
        self._build_ui()


    def _build_ui(self):

        self.setObjectName(self.OBJECTNAME)
        self.setWindowTitle(self.WINDOWTITLE)
        self.setMinimumWidth(320)
        self.setMinimumHeight(500)

        #    Base vertical layout

        base_widget = QtWidgets.QWidget()
        self.base_layout = QtWidgets.QVBoxLayout(base_widget)
        self.layout().addWidget(base_widget)

        #    Menu Bar
        menu_bar = QtGui.QMenuBar()
        file_menu = menu_bar.addMenu('File') 
        help_menu = menu_bar.addMenu('Help') 

        file_new = QtGui.QAction('New', self)
        file_new.setStatusTip('Create a new checklist')
        file_new.triggered.connect(self._add_tab)

        file_open = QtGui.QAction('Open', self)
        file_open.setStatusTip('Load Checklist')
        file_open.triggered.connect(self._load_checklist) 

        file_save = QtGui.QAction('Save', self)  
        file_save.setStatusTip('Save Checklist')
        file_save.triggered.connect(self._save_checklist) 

        file_presets = QtGui.QAction('Presets', self) 
        file_presets.triggered.connect(self.test) 

        file_exit = QtGui.QAction('Quit', self) 
        file_exit.triggered.connect(self.test2) 

        file_menu.addAction(file_new)
        file_menu.addAction(file_open)
        file_menu.addAction(file_save)
        file_menu.addAction(file_presets)
        file_menu.addAction(file_exit)

        self.base_layout.addWidget(menu_bar)

        #    Tabbed Layout
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setMaximumWidth(300)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self._delete_tab)
        self.tab_widget.setMovable(True)
        self._add_tab()
        self.base_layout.addWidget(self.tab_widget)
    
    def test(self):
        print('Tabs dict: {}'.format(self.TABS))

        for i, each in enumerate(self.TABS):
            print('Tab no: {}'.format(i))
            print('Tab: {}'.format(self.TABS[i]))
            print('Checklist items: {}'.format(self.TABS[i].ITEMS))

        pass

    def test2(self):
        
        print('Current checklist index: {}'.format(self.TABS[self.tab_widget.currentIndex()]))
        print('Current checklist index items: {}'.format(self.TABS[self.tab_widget.currentIndex()].ITEMS))
        print('Checklist dict: ')


        for each in self.TABS[self.tab_widget.currentIndex()].ITEMS:
            each_dict = {}
            each_dict['frame'] = each.frame
            each_dict['text'] = each.text
            each_dict['check'] = each.check

            print(each_dict)


        
        pass

    def _add_tab(self, tab_name = 'Untitled'):
        '''
        Adds a tab
        '''
        tab = ChecklistTab(layout = self.tab_widget, tab_name = tab_name)

        #   Add to master dictionary
        self.TABS[self.tab_widget.count() - 1] = tab

        #   Switch to new tab
        self.tab_widget.setCurrentIndex(self.tab_widget.count() - 1)

        #   Return newly created tab
        return tab

    def _delete_tab(self, index):
        '''
        Deletes specified tab
        '''
        self.tab_widget.removeTab(index)

        #   Remove from master dictionary
        # print('deleting {}'.format(index))
        # print(self.TABS.items())
        del self.TABS[index]
        #   Shift all the other tabs in dictionary by 1
        for key, value in self.TABS.items():
            if (key > index):
                # print('setting {} to {}'.format(key, key - 1))
                self.TABS[key - 1] = self.TABS[key]
            elif (key == 0):
                # print('setting {} to {}'.format(key + 1, key))
                self.TABS[key + 1] = self.TABS[key]
        # print('also deleting {}'.format(max(self.TABS.keys())))
        if self.TABS:
            del self.TABS[max(self.TABS.keys())]

    def _save_checklist(self):
        '''
        Saves current checklist
        '''

        print('Current index: {}'.format(self.tab_widget.currentIndex()))
        print('Dictionary: {}'.format(self.TABS[self.tab_widget.currentIndex()]))

        #    Get current scene directory
        currentSceneName = mc.workspace(query = True, dir = True)
        
        #    Open dialog box
        selectedFile = QtWidgets.QFileDialog.getSaveFileName(
            self, 
            'Save file',
            currentSceneName,
            "JSON Files (*.json)"
            )
        
        #    Set export.csv directory text field
        export_file = selectedFile[0]

        with open(export_file, 'w') as outfile:

            data = []

            for each in self.TABS[self.tab_widget.currentIndex()].ITEMS:
                each_dict = {}
                each_dict['frame'] = each.frame
                each_dict['text'] = each.text
                each_dict['check'] = each.check

                print(each_dict)
                data.append(each_dict)
                # json.dump(each_dict, outfile)

            json.dump(data, outfile)

    def _load_checklist(self):
        '''
        Loads checklist
        '''
        #   Open new tab
        tab = self._add_tab()

        #    Get current scene directory
        currentSceneName = mc.workspace(query = True, dir = True)
        
        #    Open dialog box
        selectedFile = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            'Open file',
            currentSceneName,
            "JSON Files (*.json)"
            )
        
        #    Set export.csv directory text field
        import_file = selectedFile[0]

        with open(import_file) as infile:
            data = infile.read()
            imported_checklist = json.loads(data)

            #   Add checklist items to new tab
            for checklist_item in imported_checklist:
                tab._add_item(frame = checklist_item['frame'], text = checklist_item['text'], check = checklist_item['check'])




class ChecklistTab(QtWidgets.QWidget):

    ITEMS = []

    def __init__(self, layout, tab_name):
        logger.debug('Checklist tab!')

        super(ChecklistTab, self).__init__()

        self.base_layout = layout
        self.tab_name = tab_name
        self.ITEMS = []
        
        self._build_ui()


    def _build_ui(self):
        '''
        Create the main ui
        '''
        tab_layout = QtWidgets.QVBoxLayout(self)
        size_policy = (QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.base_layout.addTab(self, self.tab_name)

        #   Create add checklist item button
        add_checklist_widget = QtWidgets.QWidget(self)
        add_checklist_layout = QtWidgets.QHBoxLayout(add_checklist_widget)

        self.checklist_text = QtWidgets.QLineEdit(self)
        self.checklist_frame = QtWidgets.QLineEdit(self)
        # self.checklist_frame.setMinimumWidth(20)
        self.checklist_frame.setMaximumWidth(50)
        add_button = QtWidgets.QPushButton(self)
        add_button.setText('+')
        add_button.clicked.connect(self._add_item)

        add_checklist_layout.addWidget(self.checklist_frame)
        add_checklist_layout.addWidget(self.checklist_text)
        add_checklist_layout.addWidget(add_button)
        
        tab_layout.addWidget(add_checklist_widget)

        #   Create scroll area
        scroll_widget = QtWidgets.QWidget()
        #    This makes sure the scroll doesn't act weird when there are only a few items
        scroll_widget.setSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Maximum)        
        self.scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)

        #   Scroll Area
        scroll_area = QtWidgets.QScrollArea()
        
        #    Make resizable
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)
        tab_layout.addWidget(scroll_area)

    def _add_item(self, frame = None, text = None, check = False):
        '''
        Adds a checklist item
        '''
        #   Check if text and frame are specified
        if (not frame):
            frame = self.checklist_frame.text()
        if (not text):
            text = self.checklist_text.text()

        item = ChecklistItem(checklist = self, layout = self.scroll_layout, frame = frame, text = text, check = check)

        #   Add to main dictionary
        # print('Adding {} to {}!'.format(item, self))
        # self.ITEMS.append(item)
        # print('Dict: {}'.format(self.ITEMS))


        #   Reset text
        self.checklist_frame.setText('')
        self.checklist_text.setText('')

    def _delete_item(self):
        '''
        Delete item from checklist
        '''
        pass

class ChecklistItem(QtWidgets.QWidget):
    
    PALETTE = {
        'default' : QtCore.Qt.lightGray,
        'disabled' : QtCore.Qt.gray,
        'white' : QtCore.Qt.white,
        'yellow' : QtCore.Qt.yellow,
        'red' : QtCore.Qt.red,
        'cyan' : QtCore.Qt.cyan,
        'green' : QtCore.Qt.green
        }

    def __init__(self, checklist, layout, frame = None, text = None, check = False, color = 'default'):
        logger.debug('Checklist item!')

        super(ChecklistItem, self).__init__()

        self.checklist = checklist
        self.base_layout = layout

        if (not frame.isdigit()):
            frame = None
        self.text = text
        self.frame = frame
        self.check = check
        self.color = color

        #   Add to checklist dictionary
        self.checklist.ITEMS.append(self)

        self._build_ui()

    def _build_ui(self):
        
        #    Base horizontal layout
        item_layout = QtWidgets.QHBoxLayout(self)
        self.base_layout.addWidget(self)

        # ---------------------------------------------------------------------#
        #    Main Content
        # ---------------------------------------------------------------------#
        #   Check box
        self.check_box = QtWidgets.QCheckBox()
        self.check_box.setMinimumWidth(15)
        self.check_box.setMaximumWidth(15)
        item_layout.addWidget(self.check_box)

        #    Frame block
        self.frame_block = QtWidgets.QPushButton(self.frame)
        self.frame_block.setMinimumWidth(30)
        self.frame_block.setMaximumWidth(30)
        self.frame_block.clicked.connect(self._jump_to_frame)
        item_layout.addWidget(self.frame_block)

        #    Text block
        self.text_block = QtWidgets.QLabel(self.text)
        self.text_block.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text_block.customContextMenuRequested.connect(self._right_click_menu)
        self.text_block.setWordWrap(True)
        self.text_block.setMinimumWidth(120)
        self.text_block.setMaximumWidth(180)
        item_layout.addWidget(self.text_block)

        #    Palette
        self.palette = QtGui.QPalette()
        self.palette.setColor(QtGui.QPalette.Foreground, self.PALETTE[self.color])
        self.frame_block.setPalette(self.palette)
        self.text_block.setPalette(self.palette)

        
        self.check_box.stateChanged.connect(self._toggle_widget)
        self.check_box.setChecked(self.check)

 
    def _destroy(self):
        '''
        Delete Checklist item instance
        '''
        logger.debug('Deleting item!')

        #   Remove from dictionary


        #    Remove widget from UI
        self.setParent(None)
        self.setVisible(False)

        #    Theoretically, this line should be enough, but since there is 
        #    often a time lag, the above 2 methods are also recommended
        self.deleteLater()

        return

    def _jump_to_frame(self):
        '''
        Jump to frame in Maya Timeline
        '''
        mc.currentTime(self.frame)

    def _right_click_menu(self, point):
        '''
        Show right click menu
        '''
        menu = QtGui.QMenu()

        edit_menu = menu.addAction('Edit')
        menu.addSeparator()
        delete_menu = menu.addAction('Delete')

        action = menu.exec_(self.mapToGlobal(point))
        
        if action == edit_menu:
            print('edit!')
            
        elif action == delete_menu:
            print('delete!')
            self._destroy()

    def _toggle_widget(self):
        '''
        Toggle the wigets on and off depending on check state
        '''
        # print('Item: {}'.format(self.text))
        if (self.check_box.checkState()):
            self.check = True
            self.frame_block.setEnabled(False)
            self.palette.setColor(QtGui.QPalette.Foreground, self.PALETTE['disabled'])
            self.text_block.setPalette(self.palette)
        else:
            self.check = False
            self.frame_block.setEnabled(True)
            self.palette.setColor(QtGui.QPalette.Foreground, self.PALETTE[self.color])
            self.text_block.setPalette(self.palette)


def main():
    dialog = MayaChecklistUI(parent = get_maya_main_window())
    dialog.show()