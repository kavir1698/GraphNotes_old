import os
import sys

from PyQt5.Qt import Qt, QSize, QListWidgetItem, QCheckBox, QSplitter, QLineEdit, QAction, QMenuBar, QMenu, QGroupBox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QMessageBox, QGridLayout, QListWidget, QTextEdit, QAbstractItemView, QMainWindow)

from bibtex import *
from common import *
from db_managment import *
from dialogs import *

def hasSlelectedItems(target_list):
    return target_list.currentIndex().isValid() and target_list.selectedItems()

class MainWindow(QMainWindow):
    def __init__(self, application):
        super().__init__()
        self.app = application
        self.mainWidget = MainWidget(self, application)
        self.resizeToPercent(widthPercent=0.8, heightPercent=0.9)
        self.setCentralWidget(self.mainWidget)
        self.setWindowIcon(QIcon("icons/logo.png"))
        self.setWindowTitle('GraphNotes')        
        self.show()
        
    def resizeToPercent(self, widthPercent, heightPercent):
        availableSize = self.app.desktop().availableGeometry().size()
        width = availableSize.width() * widthPercent
        height = availableSize.height() * heightPercent
        self.resize(width, height)
    
class MainWidget(QWidget):  
    """Main window class that provides logic of the program.
    Allows to search concept and to show
    information about concepts and relations """
    def __init__(self, parent=None, application=None):
        super().__init__(parent)
        self.parent = parent
        self.application = application
        self.db = self.openDatabase()
        self.initUI()


    def initActions(self):
        """initalization of actions for main windows"""

        self.help_action = QAction("&Help", self)
        self.help_action.setShortcut("F1")
        self.help_action.setStatusTip('Help')
        self.help_action.triggered.connect(lambda: HelpDialog(self))

        self.about_action = QAction("&About", self)
        self.about_action.setStatusTip('About')
        self.about_action.triggered.connect(self.showAboutMessage)        

        self.new_db_action = QAction("New DB", self)
        self.new_db_action.setShortcut("Ctrl+N")
        self.new_db_action.triggered.connect(self.openNewDB)

        self.delete_сoncept_action = QAction("&Delete", self)
        self.delete_сoncept_action.setShortcut("DEL")
        self.delete_сoncept_action.setStatusTip("Delete")
        self.delete_сoncept_action.triggered.connect(lambda: self.delete(Concept))

        self.delete_subcategory_action = QAction("&Delete subcategory", self)
        self.delete_subcategory_action.triggered.connect(lambda: self.delete(Subcategory))

        self.edit_concept_action = QAction("&Edit", self)
        self.edit_concept_action.setShortcut("F2")
        self.edit_concept_action.triggered.connect(self.editConcept)

        self.edit_relation_action = QAction("&Edit", self)
        self.edit_relation_action.setShortcut("Ctrl+F2")
        self.edit_relation_action.triggered.connect(self.editRelation)

        self.exit_action = QAction("&Exit", self)
        self.exit_action.setShortcut("ESC")
        self.exit_action.triggered.connect(self.close)

        self.select_relation_action = QAction("&Select relation", self)
        self.select_relation_action.triggered.connect(self.setRelationDescription)

        self.delete_relation_action = QAction("&Delete", self)
        self.delete_relation_action.setShortcut("Ctrl+DEL")
        self.delete_relation_action.triggered.connect(lambda: self.delete(Relation))

        
    def showAboutMessage(self):
        try:
            with open("about.txt") as f:
                text = f.read()
                QMessageBox.about(self.parent, "About application", text)
        except: pass
            
    def openNewDB(self):
        """This method deletes setting.py file and closes current application session.
        This uses for creating a new instance of Main Window.
        """
        if os.path.exists("setting.py"):
            os.remove("setting.py")
            self.parent.close()
            self.application.exit(1)
            


    def initUI(self):
        
        self.initActions()
        self.add_data_button = QPushButton("Add data", self)
        self.export_button = QPushButton("Export references", self)
        self.search_box = QGroupBox()
        self.concept_list = QListWidget(self)
        self.relation_list = QListWidget(self)
        self.result_table = QTextEdit(self)
        
        self.concept_list.selectionModel().selectionChanged.connect(self.searchRelations)
        
        self.concept_list.setSelectionMode(QAbstractItemView.ContiguousSelection)
        self.concept_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.concept_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.concept_list.customContextMenuRequested.connect(self.showConceptContextMenu)
        self.relation_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.relation_list.customContextMenuRequested.connect(self.showRelationContextMenu)
        self.relation_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
    
        self.relation_list.selectionModel().selectionChanged.connect(self.setRelationDescription)
        
        self.initSearchFrame(self.search_box)        
        self.grid = QGridLayout()
        self.result_table.setReadOnly(True)
        self.search()
        self.configWidgets()
        self.bindWidgets()
        self.show()
            
    def showConceptContextMenu(self, pos):
        if not len(self.concept_list.selectedItems()) == 1:
            return 
        global_position = self.concept_list.mapToGlobal(pos)
        my_menu = QMenu()
        my_menu.addAction(self.edit_concept_action)
        my_menu.addAction(self.delete_сoncept_action)
        my_menu.addAction(self.delete_subcategory_action)
        my_menu.addSeparator()
        my_menu.addAction(self.help_action)
        my_menu.addAction(self.exit_action)
        my_menu.exec(global_position)


    def initSearchFrame(self, frame):
        self.search_line = QLineEdit(frame)
        checkboxes = QGroupBox()
        checkboxes.setStyleSheet("border:0;")
        self.concept_checkbox = QCheckBox("Concept", checkboxes)
        self.description_checkbox = QCheckBox("Description", checkboxes)
        self.study_checkbox = QCheckBox("Study", checkboxes)
        self.reference_checkbox = QCheckBox("Reference", checkboxes)
        self.in_selected_checkbox = QCheckBox("Search in selected concepts", checkboxes)
        self.search_button = QPushButton("Search", checkboxes)
        
        
        checkboxes_layout = QGridLayout(checkboxes)
        checkboxes_layout.addWidget(self.concept_checkbox, 0, 0)
        checkboxes_layout.addWidget(self.description_checkbox, 0, 1)
        checkboxes_layout.addWidget(self.study_checkbox, 0, 2)
        checkboxes_layout.addWidget(self.reference_checkbox, 0, 3)
        checkboxes_layout.addWidget(self.in_selected_checkbox, 0, 4)
        
        checkboxes_layout.setContentsMargins(0, 0, 0, 0)
        self.concept_checkbox.setChecked(True)
        self.in_selected_checkbox.setChecked(True)
        grid = QGridLayout(frame)
        grid.addWidget(self.search_line, 1, 0)
        grid.addWidget(self.search_button, 1, 1)
        grid.addWidget(checkboxes, 2, 0, Qt.AlignLeft)
        frame.setLayout(grid)


    def getSearchData(self):
        """This method reads parameters of search line and checkboxes,
        and returns "Subcategory" class.
        None and [] uses for showing checkboxes that have been checked.
        """
        concept = self.search_line.text() if self.concept_checkbox.isChecked() else None
        
        if self.reference_checkbox.isChecked():
            reference = [
                #RelationReference(text=self.search_line.text()), 
                ConceptReference(text=self.search_line.text())
            ]  
        else:
            reference = []
        
        if self.description_checkbox.isChecked():
            description = [Description(text=self.search_line.text(), reference=reference)]
        else:
            description = [Description(reference=reference)]
    
        study = self.search_line.text() if self.study_checkbox.isChecked() else None
        
        if self.in_selected_checkbox.isChecked and len(self.concept_list.selectedItems()) > 1:
            selected_items_raw = self.concept_list.selectedItems()
            selected_items = [item.data(Qt.UserRole)[1] for item in selected_items_raw] 
        else:
            selected_items = []
        
        return Subcategory(subcategory=concept, description=description, study=study), selected_items

    # todo: doesn't work, becouse  need html + bib --> rendered bib
    def searchRelations(self):
        
        """This method triggers when the user clicked on the concept.
        This method selected ID of a subcategory from selected item in conceptions list
        and then searches and setting all information about this selected concept.
        """
        if not self.concept_list.selectedItems():
            self.setConceptDescription()
            self.setResult([], self.relation_list)
            return
        subcategory_id = self.concept_list.selectedItems()[0].data(Qt.UserRole)[1].id
        self.setConceptDescription()
        result = self.db.search_relation(subcategory_id)
        self.setResult(result, self.relation_list)


    def showRelationContextMenu(self, pos):
        global_position = self.relation_list.mapToGlobal(pos)
        my_menu = QMenu()
        my_menu.addAction(self.edit_relation_action)
        my_menu.addAction(self.delete_relation_action)
        my_menu.addSeparator()
        my_menu.exec(global_position)


    def editRelation(self):
        """This method opens dialog for editing Relation"""

        if hasSlelectedItems(self.relation_list):
            relation = self.relation_list.selectedItems()[0].data(Qt.UserRole)[2]
            dlg = EditRelationDialog(self, relation)
            if dlg.exec_():
                relation = dlg.getValue()
                self.db.update_relation(relation)
                self.select_relation_action.trigger()


    def editConcept(self):
        """This method opens dialog for editing Concept"""
        
        if hasSlelectedItems(self.concept_list):
            concept = self.concept_list.selectedItems()[0].data(Qt.UserRole)[0]
            subcategory = self.concept_list.selectedItems()[0].data(Qt.UserRole)[1]
            dlg = EditConceptDialog(self, concept, subcategory)
            
            if dlg.exec_():
                concept, subcategory = dlg.getValue()
                self.db.update_concept(concept)
                self.db.update_subcategory(subcategory)
                self.search()


    def delete(self, something):
        """This universal method for deleting something from the list and database.
        "something" parameter needs to be any of this types: Concept, Subcategory, Relation
        """
        if something == Concept:
            number = 0
            target_list = self.concept_list
        elif something == Subcategory:
            number = 1
            target_list = self.concept_list
        elif something == Relation:
            number = 2
            target_list = self.relation_list
        if hasSlelectedItems(target_list):
            something = target_list.selectedItems()[0].data(Qt.UserRole)[number]
            self.db.delete(something)
            self.search()


    # need refactoring
    def setRelationDescription(self):
        """This method retrieves information about relation,
        formats and sets it in description field.
        """
        if hasSlelectedItems(self.relation_list):
            relation = self.relation_list.selectedItems()[0].data(Qt.UserRole)[2]
            concept1 = "{}{}".format(relation.node1.concept.name,
                                     ", {}".format(relation.node1.subcategory) if relation.node1.subcategory else "")
            concept2 = "{}{}".format(relation.node2.concept.name,
                                     ", {}".format(relation.node2.subcategory) if relation.node2.subcategory else "")

            description = relation.description
            study = relation.study
            references = relation.reference

            # HTML is used for a better information formating
            text = "<b>Relation between </b> \"{}\" <b>and</b> \"{}\"<p>".format(concept1, concept2)
            text += r"<b>Description:</b>" + "<br> {} <p>".format(description)
            text += r"<b>Study:</b> {} <p>".format(study)
            text += r"<b>References:</b><ol>"
            for ref in references:
                text += " <li> {} </li>".format(getBibRenderFromHTML(ref.text))
            text += "</ol><br>"
            self.result_table.setHtml(text)
        else:
            self.result_table.clear()

    # need refactoring
    def setConceptDescription(self):
        """This method retrieves information about concept,
        formats and sets it in description field.
        """
        if not self.concept_list.selectedItems():
            self.result_table.setHtml("")
            return 
        concept = self.concept_list.selectedItems()[0].data(Qt.UserRole)[0]
        subcategory = self.concept_list.selectedItems()[0].data(Qt.UserRole)[1]
        description = subcategory.description

        # HTML is used for a better information formating
        text = "<b>Concept:</b> {}<p>".format(concept.name)
        text += "<b>Subcategory:</b> {}<p>".format(subcategory.subcategory)
        text += "<b>Synonyms:</b> {}<p>".format(concept.synonyms)
        text += "<ol>"
        for des in description:
            text += "<li> {}".format("<b>Description:</b> <br>")
            text += "  {} <p>".format(des.text)
            text += "<ol>"
            text += "<b>References: </b>"
            for ref in des.reference:
                text += "<li>"
                text += "{}".format(getBibRenderFromHTML(ref.text))
                text += "</li>"
            text += "</ol>"
            text += "</li>"
        text += "</ol>"
        self.result_table.setHtml(text)


    def setResult(self, result, list):
        """This is a universal method for showing information
        in a relation field or in a concept field.
        """
        list.clear()
        for concept, subcategory, *other in result:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, (concept, subcategory, *other))
            item.setText("{}{} {}".format(concept.name,
                                          "" if subcategory.subcategory == "" else ", ",
                                          subcategory.subcategory))
            list.insertItem(0, item)


    def search(self):
        subcategory, selected_items = self.getSearchData()
        result = self.db.search_nodes(subcategory, selected_items)
        self.setResult([], self.relation_list)
        self.setResult(result, self.concept_list)
        self.setResult([], self.relation_list)
        self.setRelationDescription()


    def configWidgets(self):
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setSpacing(5)

        self.menu_bar = QMenuBar(self)

        self.database_menu = self.menu_bar.addMenu("Database")
        self.database_menu.addAction(self.new_db_action)
        self.database_menu.addSeparator()
        self.database_menu.addAction(self.exit_action)

        self.concept_menu = self.menu_bar.addMenu("Concept")
        self.concept_menu.addAction(self.edit_concept_action)
        self.concept_menu.addAction(self.delete_сoncept_action)
        self.concept_menu.addAction(self.delete_subcategory_action)

        self.relation_menu = self.menu_bar.addMenu("Relation")
        self.relation_menu.addAction(self.edit_relation_action)
        self.relation_menu.addAction(self.delete_relation_action)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.help_menu.addAction(self.help_action)
        self.help_menu.addAction(self.about_action)

        self.grid.setMenuBar(self.menu_bar)

        self.concept_box = QGroupBox("Concepts")
        self.concept_grid = QGridLayout()
        self.concept_grid.setContentsMargins(0, 10, 0, 0)
        self.concept_grid.addWidget(self.concept_list)
        self.concept_box.setLayout(self.concept_grid)

        self.relation_box = QGroupBox("Relations")
        self.relation_grid = QGridLayout()
        self.relation_grid.setContentsMargins(0, 10, 0, 0)
        self.relation_grid.addWidget(self.relation_list)
        self.relation_box.setLayout(self.relation_grid)

        self.description_box = QGroupBox("Description")
        self.description_grid = QGridLayout()
        self.description_grid.setContentsMargins(0, 10, 0, 0)
        self.description_grid.addWidget(self.result_table)
        self.description_box.setLayout(self.description_grid)

        self.concept_splitter = QSplitter(self)
        self.concept_splitter.addWidget(self.concept_box)
        self.concept_splitter.addWidget(self.relation_box)
        self.description_splitter = QSplitter(self)
        self.description_splitter.setOrientation(Qt.Vertical)
        self.description_splitter.addWidget(self.concept_splitter)
        self.description_splitter.addWidget(self.description_box)

        self.grid.addWidget(self.add_data_button, 1, 0, Qt.AlignLeft)
        self.grid.addWidget(self.export_button, 1, 1, Qt.AlignRight)
        self.grid.addWidget(self.search_box, 2, 0, 1, 2)
        self.grid.addWidget(self.description_splitter, 5, 0, 1, 2)
        self.setLayout(self.grid)


    def bindWidgets(self):
        self.add_data_button.clicked.connect(self.addData)
        self.search_button.clicked.connect(self.search)
        self.export_button.clicked.connect(self.exportReferences)
        self.search_line.returnPressed.connect(self.search)
        
    def exportReferences(self):
        references = self.db.get_all_references()
        references = [getPlainText(ref.text) for ref in references]
        references = list(set(references))
        references = [prepareBibStr(ref) for ref in references]
        final_text = ",\n\n".join(references)
        
        dlg = QFileDialog()
        file_path = dlg.getSaveFileName(self, "Save bibtex file")[0]
        if not (file_path == ""):
            # todo: check readBibsFromFile
            try:
                with open(file_path, 'w') as f:
                    f.write(final_text)
            except Exception as error:
                showError(error)
                
        
    def addData(self):
        dlg = NewDataDialog(self.db)
        dlg.exec_()
        self.search()

    def getPath(self):
        dialog = NewDBDialog()
        if dialog.exec_():
            
            path = dialog.path
            with open("setting.py", "w") as f:
                f.write("{{ 'last': r'{0}' }}".format(path))
            return path
        else:
            self.close()


    def openDatabase(self):
        if os.path.exists("setting.py"):
            with open("setting.py") as f:
                setting = eval(f.read())
            if "last" in setting:
                if os.path.exists(setting["last"]):
                    path = setting["last"]
                else:
                    path = self.getPath()
            else:
                path = self.getPath()
        else:
            path = self.getPath()
        if path is None:
            self.close()
            exit(0)
        else:
            return Graph(path)
        
    def closeEvent(self, event):
        event.ignore()
  
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = MainWindow(app)
    while app.exec_():
        ex = MainWindow(app)