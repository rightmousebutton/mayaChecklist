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
*   Change main window from window to widget
*   Edit/Delete checklist item
*   Save as preset
*   Sort by check/archive checks
*   Sort by frame
*   Reorder checklist item functionality

=========================================================
Maya Tanaka
'''
import maya.cmds as mc
import pymel.core as pm

import os
import json

import mayaChecklist.presets.marker as marker
# print('File: {}'.format(marker.__file__))
# parentDir = os.path.abspath(os.path.join(marker.__file__, os.pardir))
# print('presets folder: {}'.format(parentDir))

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
logger.setLevel(logging.INFO)


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
            logger.debug('No previous window')

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

        file_save_as = QtGui.QAction('Save As', self)  
        file_save_as.setStatusTip('Save Checklist As')
        file_save_as.triggered.connect(self._save_as_checklist) 

        file_presets = QtGui.QMenu('Presets', self) 

        file_preset_basic = QtGui.QAction('Basic', self) 
        file_preset_basic.triggered.connect(lambda preset = 'basic': self._load_preset(preset)) 
        file_preset_polish = QtGui.QAction('Polish', self) 
        file_preset_polish.triggered.connect(lambda preset = 'polish': self._load_preset(preset)) 
        file_preset_face = QtGui.QAction('Face', self) 
        file_preset_face.triggered.connect(lambda preset = 'face': self._load_preset(preset)) 

        file_rename = QtGui.QAction('Rename', self)  
        file_rename.triggered.connect(self._rename_checklist) 

        file_exit = QtGui.QAction('Quit', self) 
        file_exit.triggered.connect(self.test2) 

        file_menu.addAction(file_new)
        file_menu.addAction(file_open)
        file_menu.addAction(file_save)
        file_menu.addAction(file_save_as)
        file_menu.addSeparator()
        file_menu.addAction(file_rename)
        file_menu.addMenu(file_presets)
        file_presets.addAction(file_preset_basic)
        file_presets.addAction(file_preset_polish)
        file_presets.addAction(file_preset_face)
        file_menu.addSeparator()
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
        Saves current checklist at stored directory
        '''

        print('Current index: {}'.format(self.tab_widget.currentIndex()))
        print('Dictionary: {}'.format(self.TABS[self.tab_widget.currentIndex()]))

        #   Get saved checklist directory
        export_file = self.TABS[self.tab_widget.currentIndex()].save_directory

        #   If save directory is blank or if it is a preset checklist, run save as function
        if (not export_file) or (self.TABS[self.tab_widget.currentIndex()].preset):
            self._save_as_checklist()
            return

        #   Write to file
        self._write_to_file(export_file)

    def _save_as_checklist(self):
        '''
        Save current checklist as new file
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
        
        export_file = selectedFile[0]

        #   Set save directory in checklist class
        self.TABS[self.tab_widget.currentIndex()].save_directory = export_file

        #   Write to file
        self._write_to_file(export_file)

    def _save_as_preset(self):
        '''
        Save current checklist as a preset
        '''
        pass

    def _write_to_file(self, export_file):
        '''
        Writes checklist data to export file
        '''
        with open(export_file, 'w') as outfile:

            data = []

            #   Create info dictionary
            logger.debug('Checklist name: {}'.format(self.TABS[self.tab_widget.currentIndex()].tab_name))
            logger.debug('Save Directory: {}'.format(self.TABS[self.tab_widget.currentIndex()].save_directory))
            logger.debug('Preset: {}'.format(self.TABS[self.tab_widget.currentIndex()].preset))

            info = {'checklist_name' : self.TABS[self.tab_widget.currentIndex()].tab_name,
                'save_directory' : self.TABS[self.tab_widget.currentIndex()].save_directory,
                'preset' : self.TABS[self.tab_widget.currentIndex()].preset}
                
            data.append(info)

            for each in self.TABS[self.tab_widget.currentIndex()].ITEMS:
                each_dict = {}
                each_dict['frame'] = each.frame
                each_dict['text'] = each.text
                each_dict['color'] = each.color
                each_dict['check'] = each.check

                logger.debug(each_dict)

                data.append(each_dict)

            json.dump(data, outfile)

    def _load_preset(self, preset):
        '''
        Load preset
        '''
        logger.info('Loading preset checklist: {}'.format(preset))

        #   Query all the lists in the presets folder
        presets_folder_directory = os.path.abspath(os.path.join(marker.__file__, os.pardir))
        all_preset_checklists = [each_file for each_file in os.listdir(presets_folder_directory) if (each_file.lower()).endswith('json')]
        logger.debug('All files in presets folder: {}'.format(all_preset_checklists))

        #   Check for specified preset in the presets folder
        preset_name = '{}.json'.format(preset)
        if not (preset_name in all_preset_checklists):
            mc.warning('Specified preset does not exist!')
            return False

        #   Generate load path
        load_checklist = os.path.join(presets_folder_directory, preset_name)

        #   Load preset
        self._load_checklist(checklist = load_checklist)

    def _load_checklist(self, checklist = None):
        '''
        Loads checklist
        '''
        #   Open new tab
        tab = self._add_tab()

        import_file = checklist
        #   If the chekclist isn't specified, load prompt dialog box
        if (not checklist):
            #    Get current scene directory
            currentSceneName = mc.workspace(query = True, dir = True)
            
            #    Open dialog box
            selectedFile = QtWidgets.QFileDialog.getOpenFileName(
                self, 
                'Open file',
                currentSceneName,
                "JSON Files (*.json)"
                )
            
            import_file = selectedFile[0]
            

        #   Set save directory
        self.TABS[self.tab_widget.currentIndex()].save_directory = import_file

        with open(import_file) as infile:
            data = infile.read()
            imported_checklist = json.loads(data)

            #   Add checklist items to new tab
            for i, checklist_item in enumerate(imported_checklist):
                
                #   Get checklist info from first dictionary item
                if (i == 0):
                    self._rename_checklist(name = checklist_item['checklist_name'])
                    tab.save_directory = checklist_item['save_directory']
                    tab.preset = checklist_item['preset']
                else:
                    print(checklist_item['text'])
                    print(checklist_item['color'])
                    tab._add_item(frame = checklist_item['frame'], 
                        text = checklist_item['text'], 
                        color = checklist_item['color'], 
                        check = checklist_item['check'])

    def _rename_checklist(self, name = None):
        '''
        Rename current checklist
        '''

        if (not name):
            #   Prompt user for new name
            input_tab_name_dialog = QtGui.QInputDialog()
            input_tab_name_dialog.setLabelText("Rename checklist")
            input_tab_name_dialog.setWindowTitle("Rename Checklist")
            input_tab_name_dialog.exec_()
            name = input_tab_name_dialog.textValue()

            print('input: {}'.format(name))

        self.TABS[self.tab_widget.currentIndex()].tab_name = name
        self.tab_widget.setTabText(self.tab_widget.currentIndex(), name)




class ChecklistTab(QtWidgets.QWidget):
    '''
    Checklist Class
    '''

    ITEMS = []

    def __init__(self, layout, tab_name, preset = False):
        logger.debug('Checklist tab!')

        super(ChecklistTab, self).__init__()

        self.base_layout = layout
        self.tab_name = tab_name
        self.ITEMS = []

        self.save_directory = ''
        self.preset = preset
        
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

        #   Color picker
        self.color = None
        self.color_picker_button = QtWidgets.QPushButton(self)
        self.color_picker_button.setMaximumWidth(30)
        self.color_picker_button.clicked.connect(lambda target = self.color_picker_button: self._pick_color(target))
        self.color_picker_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.color_picker_button.customContextMenuRequested.connect(self._color_right_click_menu)

        self.checklist_text = QtWidgets.QLineEdit(self)
        self.checklist_frame = QtWidgets.QLineEdit(self)
        # self.checklist_frame.setMinimumWidth(20)
        self.checklist_frame.setMaximumWidth(50)
        add_button = QtWidgets.QPushButton(self)
        add_button.setText('+')
        add_button.clicked.connect(self._add_item)

        add_checklist_layout.addWidget(self.color_picker_button)
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

    def _pick_color(self, target = None):
        '''
        Color picker dialog box
        '''
        color = QtGui.QColorDialog.getColor()
        self.color = color.name()
        target.setStyleSheet('QWidget { background-color: %s}' % self.color)


    def _color_right_click_menu(self, point):
        '''
        Show right click menu of color picker
        '''
        menu = QtGui.QMenu()

        menu_default = menu.addAction('Default')
        menu.addSeparator()
        menu_red = menu.addAction('Red')
        menu_blue = menu.addAction('Blue')
        menu_green = menu.addAction('Green')
        menu_yellow = menu.addAction('Yellow')

        palette_dict = {
            menu_default : None,
            menu_red : '#733230',
            menu_blue : '#002D40',
            menu_green : '#2C594F',
            menu_yellow : '#998A2F'
        }

        action = menu.exec_(self.mapToGlobal(point))
        self.color = palette_dict.get(action, None)

        self.color_picker_button.setStyleSheet('QWidget { background-color: %s}' % self.color)

    def _add_item(self, frame = None, text = None, color = None, check = False):
        '''
        Adds a checklist item
        '''
        #   Check if text and frame are specified
        if (not frame):
            frame = self.checklist_frame.text()
        if (not text):
            text = self.checklist_text.text()

        item = ChecklistItem(checklist = self, 
            layout = self.scroll_layout,
            frame = frame,
            text = text,
            color = color,
            check = check)

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

    def __init__(self, checklist, layout, frame = None, text = None, check = False, color = None):
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
        self.item_layout = QtWidgets.QHBoxLayout(self)
        self.base_layout.addWidget(self)

        # ---------------------------------------------------------------------#
        #    Main Content
        # ---------------------------------------------------------------------#
        #   Check box
        self.check_box = QtWidgets.QCheckBox()
        self.check_box.setMinimumWidth(15)
        self.check_box.setMaximumWidth(15)
        self.item_layout.addWidget(self.check_box)

        #    Frame block
        self.frame_block = QtWidgets.QPushButton(self.frame)
        self.frame_block.setMinimumWidth(30)
        self.frame_block.setMaximumWidth(30)
        self.frame_block.clicked.connect(self._jump_to_frame)
        self.item_layout.addWidget(self.frame_block)

        #    Text block
        self.text_block = QtWidgets.QLabel(self.text)
        self.text_block.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.text_block.customContextMenuRequested.connect(self._right_click_menu)
        self.text_block.setWordWrap(True)
        self.text_block.setMinimumWidth(120)
        self.text_block.setMaximumWidth(180)
        self.item_layout.addWidget(self.text_block)

        #    Palette
        self.palette = QtGui.QPalette()
        self._refresh_properties()
        
        self.check_box.stateChanged.connect(self._toggle_widget)
        self.check_box.setChecked(self.check)

    def _set_color(self):
        '''
        Set background color of item
        '''
        print(self.color)
        if (self.color):
            self.palette.setColor(QtGui.QPalette.Background, self.color)
            self.setAutoFillBackground(True)
            self.setPalette(self.palette)

    def _refresh_properties(self):
        '''
        Refresh color, frame block, text block
        '''
        #   Color
        print(self.color)
        if (self.color):
            self.palette.setColor(QtGui.QPalette.Background, self.color)
            self.setAutoFillBackground(True)
            self.setPalette(self.palette)

        #   Frame block
        self.frame_block.setText(self.frame)

        #   Text block
        self.text_block.setText(self.text)


    def _destroy(self):
        '''
        Delete Checklist item instance
        '''
        logger.debug('Deleting item!')

        #   Remove from dictionary
        self.checklist.ITEMS.remove(self)
        print(self.checklist.ITEMS)

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
            self._edit_checklist_item()
            
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

    def _edit_checklist_item(self):
        '''
        Edits the current checklist item
        '''
        logger.debug('Edit checklist item!')

        #   Hide previous widgets
        self.check_box.hide()
        self.frame_block.hide()
        self.text_block.hide()

        #   Color button
        self.edit_color_picker_button = QtWidgets.QPushButton(self)
        self.edit_color_picker_button.setMaximumWidth(30)
        self.edit_color_picker_button.clicked.connect(lambda target = self.edit_color_picker_button: self._pick_color(target))
        self.edit_color_picker_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.edit_color_picker_button.customContextMenuRequested.connect(self._color_right_click_menu)
        self.item_layout.addWidget(self.edit_color_picker_button)

        #    Frame block
        edit_frame_block = QtWidgets.QLineEdit(self.frame)
        edit_frame_block.setMinimumWidth(30)
        edit_frame_block.setMaximumWidth(30)
        self.item_layout.addWidget(edit_frame_block)

        #    Text block
        edit_text_block = QtWidgets.QLineEdit(self.text)
        edit_text_block.setMinimumWidth(120)
        edit_text_block.setMaximumWidth(180)
        self.item_layout.addWidget(edit_text_block)
        
        def _apply_edits():
            logger.debug('Applying edits!')

            #   Gather new info
            self.text = edit_text_block.text()
            frame = edit_frame_block.text()
            if (not frame.isdigit()):
                frame = None
            self.frame = frame

            #   Apply new info
            self._refresh_properties()

            #   Destroy edit widgets
            self.edit_color_picker_button.setParent(None)
            self.edit_color_picker_button.setVisible(False)
            self.edit_color_picker_button.deleteLater()

            edit_frame_block.setParent(None)
            edit_frame_block.setVisible(False)
            edit_frame_block.deleteLater()

            edit_text_block.setParent(None)
            edit_text_block.setVisible(False)
            edit_text_block.deleteLater()

            apply_edit_button.setParent(None)
            apply_edit_button.setVisible(False)
            apply_edit_button.deleteLater()

            #   Show previous widgets
            self.check_box.show()
            self.frame_block.show()
            self.text_block.show()

        apply_edit_button = QtWidgets.QPushButton(self)
        apply_edit_button.setText('OK')
        apply_edit_button.clicked.connect(_apply_edits)
        self.item_layout.addWidget(apply_edit_button)

    def _pick_color(self, target = None):
        '''
        Color picker dialog box
        '''
        color = QtGui.QColorDialog.getColor()
        self.color = color.name()
        target.setStyleSheet('QWidget { background-color: %s}' % self.color)


    def _color_right_click_menu(self, point):
        '''
        Show right click menu of color picker
        '''
        menu = QtGui.QMenu()

        menu_default = menu.addAction('Default')
        menu.addSeparator()
        menu_red = menu.addAction('Red')
        menu_blue = menu.addAction('Blue')
        menu_green = menu.addAction('Green')
        menu_yellow = menu.addAction('Yellow')

        palette_dict = {
            menu_default : None,
            menu_red : '#733230',
            menu_blue : '#002D40',
            menu_green : '#2C594F',
            menu_yellow : '#998A2F'
        }

        action = menu.exec_(self.mapToGlobal(point))
        self.color = palette_dict.get(action, None)

        self.edit_color_picker_button.setStyleSheet('QWidget { background-color: %s}' % self.color)




def main():
    dialog = MayaChecklistUI(parent = get_maya_main_window())
    dialog.show()