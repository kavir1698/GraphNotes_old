from os import path

from PyQt5.Qt import Qt, QIcon, QListWidgetItem, QMessageBox
from PyQt5.QtWidgets import (QGridLayout, QLabel, QLineEdit, QMenu, QAction, QInputDialog,
                             QDialog, QPushButton, QFileDialog, QListWidget,
                             QCompleter, QTextEdit, QComboBox, QGroupBox, QSplitter)

from bibtex import *
from db_managment import *
from richtext_widget import *
from common import *


def showError(text):
    msg = QMessageBox()
    msg.setWindowTitle("Error")
    msg.setText(str(text))
    msg.setIcon(QMessageBox.Warning)
    msg.exec()
    
def hasSlelectedItems(target_list):
    return target_list.currentIndex().isValid() and target_list.selectedItems()

class NewDBDialog(QDialog):
    """
    Dialog that opens when setting or db in setting doesn't exist
    """

    def __init__(self):
        super().__init__(flags=Qt.Dialog | Qt.MSWindowsFixedSizeDialogHint)
        self.path = None
        self._createUI()

    def _createUI(self):
        self.open_button = QPushButton("Open", self)
        self.create_button = QPushButton("Create", self)
        self._configWidgets()
        self._configLayout()

    def _configWidgets(self):
        self.setWindowTitle("Open or create database")
        self.open_button.clicked.connect(self.openDatabase)
        self.create_button.clicked.connect(self.createDatabase)

    def _configLayout(self):
        grid = QGridLayout()
        label = QLabel("Would you prefer: create or open existing database?")
        label.setAlignment(Qt.AlignHCenter)
        grid.addWidget(label, 0, 1, 0, 2, Qt.AlignTop)
        grid.addWidget(QLabel(""), 1, 0)
        grid.addWidget(QLabel(""), 2, 0)
        grid.addWidget(self.open_button, 3, 1, Qt.AlignHCenter)
        grid.addWidget(self.create_button, 3, 2, Qt.AlignHCenter)

        self.setLayout(grid)

    def openDatabase(self):
        """ Method opens file dialog that returns path to file """
        dlg = QFileDialog()
        selected_path = dlg.getOpenFileName(caption='Open file',
                                            filter="Database files (*.db);; All files (*.*)")[0]
        if not (selected_path == ""):
            self.path = selected_path
            self.accept()

    def createDatabase(self):
        """ This method opens file dialog, that returns path to file,
        creates a database and accepts this dialog.
        """
        dlg = QFileDialog(self)  #
        selected_path = dlg.getSaveFileName(caption='New database', directory='new.db',
                                            filter="Database files (*.db);; All files (*.*)")[0]
        if not (selected_path == ""):
            Graph(selected_path).close_connection()
            self.path = selected_path
            self.accept()


class EditReferenceOrDescription(QDialog):
    def __init__(self, obj):
        """
        :param obj: Object that would be edited
        """
        super().__init__(flags=Qt.WindowCloseButtonHint
                         | Qt.WindowMaximizeButtonHint
                               | Qt.WindowMinimizeButtonHint)
        self.return_class = type(obj)
        self.obj = obj

        self.text_label = QLabel("Text", self)
        self.text_line = RichTextWidget(self)
        self.commit_button = QPushButton("Commit changes", self)
        self.grid = QGridLayout(self)
        self._configWidgets()

    def _configWidgets(self):
        self.setWindowTitle("Edit reference")
        self.resize(900, 700)
        text = self.obj.text
        if self.return_class in [ConceptReference, RelationReference]:
            text = prepareBibHTML(text)
        self.text_line.setHtml(text)
        self.commit_button.clicked.connect(self._commitChanges)

        self.grid.addWidget(self.commit_button, 1, 1, Qt.AlignRight)
        self.grid.addWidget(self.text_label, 1, 0)
        self.grid.addWidget(self.text_line, 2, 0, 1, 2)

    def getValue(self):
        if self.return_class == Description:
            return self.return_class(id=self.obj.id, text=self.text_line.toHtml(), subcategory_id=self.obj.subcategory_id)
        elif self.return_class == RelationReference:
            return self.return_class(id=self.obj.id, text=self.text_line.toHtml(), relation_id=self.obj.relation_id)
        else:
            return self.return_class(id=self.obj.id, text=self.text_line.toHtml(), node_id=self.obj.node_id)


    def _commitChanges(self):
        self.accept()


class EditRelationDialog(QDialog):
    def __init__(self, parent, relation):
        super().__init__(parent=parent,
                         flags=Qt.WindowCloseButtonHint
                         | Qt.WindowMaximizeButtonHint
                         | Qt.WindowMinimizeButtonHint)

        self.relation = relation

        self.commit_button = QPushButton("Commit changes", self)

        self.relation_label = QLabel("Relation", self)
        self.relation_line = RichTextWidget(self)

        self.study_label = QLabel("Study", self)
        self.study_line = QLineEdit(self)

        self.references_label = QLabel("Reference", self)
        self.references_line = QListWidget(self)

        self._setValue()
        self.grid = QGridLayout()
        self._configWidgets()
        self.setLayout(self.grid)

    def _configWidgets(self):
        self.setWindowTitle("Edit relation")
        self.resize(900, 700)

        # Binding
        self.commit_button.clicked.connect(self._commitChanges)
        self.references_line.setContextMenuPolicy(Qt.CustomContextMenu)
        self.references_line.customContextMenuRequested.connect(self._showReferenceMenu)
        self.grid.setSizeConstraint(QGridLayout.SetMinimumSize)

        # Grid Layout
        self.grid.addWidget(self.relation_label, 2, 0, Qt.AlignTop)
        self.grid.addWidget(self.relation_line, 2, 1)
        self.grid.addWidget(self.study_label, 3, 0)
        self.grid.addWidget(self.study_line, 3, 1)
        self.grid.addWidget(self.references_label, 4, 0, Qt.AlignTop)
        self.grid.addWidget(self.references_line, 4, 1)
        self.grid.addWidget(self.commit_button, 7, 1, Qt.AlignRight)

    def _addReference(self):
        dialog = NewReferenceDialog(self.parent().db, RelationReference)
        if dialog.exec_():
            references = dialog.getValues()
            for reference in references:
                reference.relation_id = self.relation.id
                self.parent().db.commit(reference)
                item = QListWidgetItem()
                item.setData(Qt.UserRole, reference)
                item_text = getBibRenderFromHTML(reference.text)
                item.setText("{}".format(item_text))
                self.references_line.insertItem(0, item)

    def _editReference(self):
        if hasSlelectedItems(self.references_line):
            reference = self.references_line.selectedItems()[0].data(Qt.UserRole)
            dlg = EditReferenceOrDescription(reference)
            if dlg.exec_():
                reference = dlg.getValue()
                self.references_line.selectedItems()[0].data(Qt.UserRole).text = reference.text
                item_text = getBibRenderFromHTML(reference.text)
                self.references_line.selectedItems()[0].setText(item_text)
                self.parent().db.update_reference(reference)

    def _deleteReference(self):
        if hasSlelectedItems(self.references_line):
            reference = self.references_line.selectedItems()[0].data(Qt.UserRole)
            self.parent().db.delete(reference)
            item = self.references_line.selectedItems()[0]
            self.references_line.takeItem(self.references_line.row(item))

    def _showReferenceMenu(self, pos):
        edit_reference_action = QAction("&Edit", self)
        edit_reference_action.triggered.connect(self._editReference)
        delete_reference_action = QAction("&Delete", self)
        delete_reference_action.triggered.connect(self._deleteReference)
        add_reference_action = QAction("&Add new", self)
        add_reference_action.triggered.connect(self._addReference)

        global_position = self.references_line.mapToGlobal(pos)
        my_menu = QMenu()
        my_menu.addAction(edit_reference_action)
        my_menu.addAction(delete_reference_action)
        my_menu.addAction(add_reference_action)
        my_menu.exec(global_position)

    def _setValue(self):
        self.relation_line.setText(self.relation.description)
        self.study_line.setText(self.relation.study)
        references = self.relation.reference
        for ref in references:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, ref)
            item_text = getBibRenderFromHTML(ref.text)
            item.setText("{}".format(item_text))
            self.references_line.insertItem(0, item)

    def getValue(self):
        description = self.relation_line.toHtml()
        study = self.study_line.text()
        return Relation(id=self.relation.id, description=description, study=study)

    def _commitChanges(self):
        self.accept()


class EditConceptDialog(QDialog):
    def __init__(self, parent, concept, subcategory):
        super().__init__(parent=parent,
                         flags=Qt.WindowCloseButtonHint 
                         | Qt.WindowMaximizeButtonHint 
                         | Qt.WindowMinimizeButtonHint)

        self.concept = concept
        self.subcategory = subcategory

        self.commit_button = QPushButton("Commit changes", self)

        self.concept_label = QLabel("Concept", self)
        self.concept_field = QLineEdit(self)

        self.subcategory_label = QLabel("Subcategory", self)
        self.subcategory_field = QLineEdit(self)

        self.synonyms_label = QLabel("Synonyms", self)
        self.synonyms_field = QLineEdit(self)

        self.description_label = QLabel("Description", self)
        self.description_field = QListWidget(self)

        self.study_label = QLabel("Study", self)
        self.study_field = QLineEdit(self)

        self.references_label = QLabel("References", self)
        self.references_field = QListWidget(self)

        self.add_relation_button = QPushButton("Add relation", self)
        self.relation_status_label = QLabel("", self)

        self.grid = QGridLayout()
        self._configWidgets()
        self.setValue()
        self.description_field.setCurrentRow(0)

    def _configWidgets(self):
        self.resize(900, 700)
        self.setWindowTitle("Edit concept")

        self.description_field.selectionModel().selectionChanged.connect(self.showReferences)
        
        self.references_field.setContextMenuPolicy(Qt.CustomContextMenu)
        self.references_field.customContextMenuRequested.connect(self._showReferenceMenu)
        self.description_field.setContextMenuPolicy(Qt.CustomContextMenu)
        self.description_field.customContextMenuRequested.connect(self._showDescriptionMenu)
        self.commit_button.clicked.connect(self.commitChanges)
        self.add_relation_button.clicked.connect(self.addRelation)

        
        self.grid.addWidget(self.concept_label, 2, 0)
        self.grid.addWidget(self.concept_field, 2, 1)
        self.grid.addWidget(self.subcategory_label, 3, 0)
        self.grid.addWidget(self.subcategory_field, 3, 1)
        self.grid.addWidget(self.synonyms_label, 4, 0)
        self.grid.addWidget(self.synonyms_field, 4, 1)
        self.grid.addWidget(self.description_label, 5, 0)
        self.grid.addWidget(self.description_field, 5, 1)
        self.grid.addWidget(self.study_label, 6, 0)
        self.grid.addWidget(self.study_field, 6, 1)
       
        self.grid.addWidget(self.references_label, 7, 0, Qt.AlignTop)
        self.grid.addWidget(self.references_field, 7, 1)
        self.grid.addWidget(self.add_relation_button, 8, 0, Qt.AlignLeft)
        self.grid.addWidget(self.relation_status_label, 8, 1, Qt.AlignLeft)
        self.grid.addWidget(self.commit_button, 8, 1, Qt.AlignRight)
        self.grid.setSizeConstraint(QGridLayout.SetMinimumSize)
        self.setLayout(self.grid)

    def addRelation(self):
        db = self.parent().db
        dlg = NewDataDialog(db, self.concept, self.subcategory)
        if dlg.exec_():
            self.relation_status_label.setText("   New relation was added!")
        else:
            self.relation_status_label.setText("")


    def showReferences(self):
        
        if hasSlelectedItems(self.description_field):
            description = self.description_field.selectedItems()[0].data(Qt.UserRole)
            self.setReferenceList(description.reference)

    def setReferenceList(self, result):
        self.references_field.clear()
        for ref in result:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, ref)
            item_text = getBibRenderFromHTML(ref.text)
            item.setText("{}".format(item_text))
            self.references_field.insertItem(0, item)

    def setValue(self):
        self.concept_field.setText(self.concept.name)
        self.synonyms_field.setText(self.concept.synonyms)
        self.subcategory_field.setText(self.subcategory.subcategory)
        self.study_field.setText(self.subcategory.study)
        descriptions = self.subcategory.description
        for des in descriptions:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, des)
            item_text = getPlainText(des.text)
            item.setText("{}".format(item_text))
            self.description_field.insertItem(0, item)

    def addReference(self):
        if hasSlelectedItems(self.description_field):
            description_id = self.description_field.selectedItems()[0].data(Qt.UserRole).id
            dialog = NewReferenceDialog(self.parent().db, ConceptReference)
            if dialog.exec_():
                references = dialog.getValues()
                for reference in references:
                    reference.node_id = description_id
                    self.parent().db.commit(reference)
                    item = QListWidgetItem()
                    item.setData(Qt.UserRole, reference)
                    item_text = getBibRenderFromHTML(reference.text)
                    item.setText("{}".format(item_text))
                    self.references_field.insertItem(0, item)

    def editReference(self):
        if hasSlelectedItems(self.references_field):
            reference = self.references_field.selectedItems()[0].data(Qt.UserRole)
            dlg = EditReferenceOrDescription(reference)
            if dlg.exec_():
                reference = dlg.getValue()
                self.references_field.selectedItems()[0].data(Qt.UserRole).text = reference.text
                item_text = getBibRenderFromHTML(reference.text)
                self.references_field.selectedItems()[0].setText(item_text)
                self.parent().db.update_reference(reference)

    def deleteReference(self):
        if hasSlelectedItems(self.references_field):
            reference = self.references_field.selectedItems()[0].data(Qt.UserRole)
            self.parent().db.delete(reference)
            item = self.references_field.selectedItems()[0]
            self.references_field.takeItem(self.references_field.row(item))

    def addDescription(self):
        dlg = EditReferenceOrDescription(Description(text="", subcategory_id=self.subcategory.id))
        dlg.setWindowTitle("Edit description")
        if dlg.exec_():
            description = dlg.getValue()
            self.parent().db.update_description(description)
            item = QListWidgetItem()
            item.setData(Qt.UserRole, description)
            item_text = getPlainText(description.text)
            item.setText("{}".format(item_text))
            self.description_field.insertItem(0, item)
            self.references_field.clear()

    def editDescription(self):
        if hasSlelectedItems(self.description_field):
            description = self.description_field.selectedItems()[0].data(Qt.UserRole)
            dlg = EditReferenceOrDescription(description)
            dlg.setWindowTitle("Edit description")
            if dlg.exec_():
                description = dlg.getValue()
                self.description_field.selectedItems()[0].data(Qt.UserRole).text = description.text
                item_text = getPlainText(description.text)
                self.description_field.selectedItems()[0].setText(item_text)
                self.parent().db.update_description(description)

    def deleteDescription(self):
        if hasSlelectedItems(self.description_field):
            description = self.description_field.selectedItems()[0].data(Qt.UserRole)
            self.parent().db.delete(description)
            item = self.description_field.selectedItems()[0]
            self.description_field.takeItem(self.description_field.row(item))
            self.references_field.clear()

    def _showReferenceMenu(self, pos):

        edit_reference_action = QAction("&Edit", self)
        edit_reference_action.triggered.connect(self.editReference)
        delete_reference_action = QAction("&Delete", self)
        delete_reference_action.triggered.connect(self.deleteReference)
        add_reference_action = QAction("&Add new", self)
        add_reference_action.triggered.connect(self.addReference)

        global_position = self.references_field.mapToGlobal(pos)
        my_menu = QMenu()
        my_menu.addAction(edit_reference_action)
        my_menu.addAction(delete_reference_action)
        my_menu.addAction(add_reference_action)
        my_menu.exec(global_position)

    def _showDescriptionMenu(self, pos):
        edit_description_action = QAction("&Edit", self)
        edit_description_action.triggered.connect(self.editDescription)
        delete_description_action = QAction("&Delete", self)
        delete_description_action.triggered.connect(self.deleteDescription)
        add_description_action = QAction("&Add new", self)
        add_description_action.triggered.connect(self.addDescription)

        global_position = self.description_field.mapToGlobal(pos)
        my_menu = QMenu()
        my_menu.addAction(edit_description_action)
        my_menu.addAction(delete_description_action)
        my_menu.addAction(add_description_action)
        my_menu.exec(global_position)

    def getValue(self):
        concept_name = self.concept_field.text()
        synonyms = self.synonyms_field.text()
        subcategory = self.subcategory_field.text()
        study = self.study_field.text()
        return (Concept(id=self.concept.id, name=concept_name, synonyms=synonyms),
                Subcategory(id=self.subcategory.id, subcategory=subcategory, study=study))

    def commitChanges(self):
        self.accept()


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent,
                         flags=Qt.WindowCloseButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowMinimizeButtonHint)
        view = QTextEdit(self)
        self.setWindowTitle("Help")
        with open(path.join("help", "index.html")) as f:
            text = f.read()
            view.setText(text)
        self.resize(500, 600)
        view.setReadOnly(True)
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(view)
        self.setLayout(grid)
        self.exec()


class NewDataDialog(QDialog):
    def __init__(self, db, concept=None, subcategory=None):
        super().__init__(flags=Qt.Window)

        self.setWindowIcon(QIcon("logo.png"))
        self.db = db
        self.reference_list1 = []
        self.reference_list2 = []
        self.reference_list3 = []

        #self.import_button = QPushButton("Import from file")

        self.concept_splitter = QSplitter()
        self.relation_splitter = QSplitter(self)
        self.concept1 = ConceptBox(self.db)
        self.concept2 = ConceptBox(self.db)
        self.relation = RelationBox()

        self.commit_button = QPushButton("Commit", self)

        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.configWidgets()
        if subcategory and concept:
            self.setInitialValue(concept, subcategory)        

    def setInitialValue(self, concept, subcategory):
        self.concept1.setValueInitValue(concept, subcategory)
        self.concept1.setDisabled(True)

    def configWidgets(self):
        self.resize(900, 700)
        self.concept1.setTitle("Concept1")
        self.concept2.setTitle("Concept2")

        self.relation_splitter.setOrientation(Qt.Vertical)
        self.commit_button.clicked.connect(self.commitChanges)

        #self.grid.addWidget(self.import_button, 6, 0, Qt.AlignLeft)
        self.concept_splitter.addWidget(self.concept1)
        self.concept_splitter.addWidget(self.concept2)
        self.relation_splitter.addWidget(self.concept_splitter)
        self.relation_splitter.addWidget(self.relation)
        self.grid.addWidget(self.relation_splitter, 1, 0, 1, 4)
        self.grid.addWidget(self.commit_button, 6, 3, 1, 1, Qt.AlignRight)
        self.setWindowTitle("Add new data")
        self.grid.setSpacing(5)

    def commitChanges(self):
        relation, relation.reference = self.relation.getData()
        concept1, subcategory1, description1 = self.concept1.getData()
        concept2, subcategory2, description2 = self.concept2.getData()

        # Left concept
        concept1 = self.db.get_similar(concept1)
        self.db.add_and_flush(concept1)
        subcategory1.concept_id = concept1.id
        subcategory1 = self.db.get_similar(subcategory1)
        self.db.add_and_flush(subcategory1)
        if description1 is not None:
            description1.subcategory_id = subcategory1.id
            self.db.add_and_flush(description1)

        # Right concept
        concept2 = self.db.get_similar(concept2)
        self.db.add_and_flush(concept2)
        subcategory2.concept_id = concept2.id
        subcategory2 = self.db.get_similar(subcategory2)
        self.db.add_and_flush(subcategory2)
        if description2 is not None:
            description2.subcategory_id = subcategory2.id
            self.db.add_and_flush(description2)

        relation.node1_id = subcategory1.id
        relation.node2_id = subcategory2.id
        self.db.add_and_flush(relation)

        # Check commit
        node1 = relation.node1
        node2 = relation.node2
        if not relation.isEmpty():
            if node1.concept.isEmpty() or node2.concept.isEmpty():
                showError("Concept field is empty!")
                return
            else:
                self.db.commit(relation)
        else:
            self.db.delete(relation)

            if not node1.isEmpty() and node1.concept.isEmpty():
                self.db.delete(node1)
                self.db.delete(concept1)                
                showError("Left concept field is empty!")
                return
            if not node2.isEmpty() and node2.concept.isEmpty():
                self.db.delete(node2)
                self.db.delete(concept2)                
                showError("Right concept filed is empty!")
                return

            self.db.commit()
        self.accept()

    


class ConceptBox(QGroupBox):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.reference_list = []

        # Concept field
        # =======================
        self.concept_label = QLabel("Concept:", self)
        self.concept_filed = QLineEdit(self)

        # Subcategory field
        # =======================
        self.subcategory_label = QLabel("Subcategory:", self)
        self.subcategory_field = QLineEdit(self)

        # Synonyms names field
        # =======================
        self.synonyms_label = QLabel("Synonyms:", self)
        self.synonyms_field = QLineEdit(self)

        # Description field
        # =======================
        self.description_label = QLabel("Description:", self)
        self.description_field = RichTextWidget(self)

        # Reference field
        # =======================
        self.reference_label = QLabel("Reference:", self)
        self.reference_field = QListWidget(self)

        # Study field
        # ========================
        self.study_label = QLabel("Study:", self)
        self.study_field = QLineEdit(self)

        self.grid = QGridLayout()
        self.initActions()
        self._configWidgets()
        self._setCompleters()
        self.setLayout(self.grid)

    def _configWidgets(self):
        self.reference_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.reference_field.setContextMenuPolicy(Qt.CustomContextMenu)
        self.reference_field.customContextMenuRequested.connect(self.showContextMenu)
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.setSpacing(5)
        self.grid.addWidget(self.concept_label, 1, 0)
        self.grid.addWidget(self.concept_filed, 1, 1)
        self.grid.addWidget(self.subcategory_label, 2, 0)
        self.grid.addWidget(self.subcategory_field, 2, 1)
        self.grid.addWidget(self.synonyms_label, 3, 0)
        self.grid.addWidget(self.synonyms_field, 3, 1)
        self.grid.addWidget(self.description_label, 4, 0, Qt.AlignTop)
        self.grid.addWidget(self.description_field, 4, 1)
        self.grid.addWidget(self.study_label, 5, 0)
        self.grid.addWidget(self.study_field, 5, 1)
        self.grid.addWidget(self.reference_label, 6, 0, Qt.AlignTop)
        self.grid.addWidget(self.reference_field, 6, 1)

    def _setCompleters(self):
        concepts = [[c.name, c.synonyms]
                    for c in self.db.session.query(Concept).all()]
        subcategories = [[c.subcategory, c.study]
                         for c in self.db.session.query(Subcategory).all()]
        if len(concepts) != 0:
            name, synonyms = zip(*concepts)
            concept_completer = QCompleter(name)
            concept_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.concept_filed.setCompleter(concept_completer)
            synonyms_completer = QCompleter(synonyms)
            synonyms_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.synonyms_field.setCompleter(synonyms_completer)
        if len(subcategories) != 0:
            subcategory, study = zip(*subcategories)
            subcategory_completer = QCompleter(subcategory)
            subcategory_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.subcategory_field.setCompleter(subcategory_completer)
            study_completer = QCompleter(study)
            study_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.study_field.setCompleter(study_completer)

    def showContextMenu(self, pos):
        global_position = self.reference_field.mapToGlobal(pos)
        my_menu = QMenu()
        my_menu.addAction(self.new_reference_action)
        my_menu.addAction(self.delete_reference_action)
        my_menu.addSeparator()
        my_menu.exec(global_position)

    def deleteReference(self):
        if hasSlelectedItems(self.reference_field):
            item = self.reference_field.selectedItems()[0].data(Qt.UserRole)
            self.reference_list.remove(item)
            self.setReferences(self.reference_list)

    def setReferences(self, result):
        self.reference_field.clear()
        for reference in result:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, reference)
            item_text = getBibRenderFromHTML(reference.text)
            item.setText("{}".format(item_text))
            self.reference_field.insertItem(0, item)

    def createReference(self):

        dlg = NewReferenceDialog(self.parent().parent().parent().db, ConceptReference)
        if dlg.exec_():
            self.reference_list += dlg.getValues()
            self.setReferences(self.reference_list)

    def initActions(self):
        self.delete_reference_action = QAction("Delete reference", self)
        self.delete_reference_action.triggered.connect(self.deleteReference)
        self.new_reference_action = QAction("New reference", self)
        self.new_reference_action.triggered.connect(self.createReference)

    def getData(self):

        concept_name = self.concept_filed.text().strip()
        subcat = self.subcategory_field.text().strip()
        syn = self.synonyms_field.text().strip()
        description = Description(text=self.description_field.toHtml())
        description.reference = self.reference_list
        description = description if getPlainText(description.text) != "" else None
        study = self.study_field.text().strip()
        concept = Concept(name=concept_name, synonyms=syn)
        subcategory = Subcategory(subcategory=subcat, study=study)
        return concept, subcategory, description

    def setValueInitValue(self, con, sub):
        self.concept_filed.setText(con.name)
        self.synonyms_field.setText(con.synonyms)
        self.subcategory_field.setText(sub.subcategory)
        self.study_field.setText(sub.study)

class RelationBox(QGroupBox):
    def __init__(self):
        super().__init__()
        self.reference_list = []
        # Relation field
        # =======================
        self.relation_label = QLabel("Relation", self)
        self.relation_field = RichTextWidget()

        # Reference field
        # =======================
        self.reference_label = QLabel("Reference:", self)
        self.reference_field = QListWidget(self)

        # Study field
        # =======================
        self.study_label = QLabel("Study:", self)
        self.study_field = QLineEdit(self)

        self.grid = QGridLayout(self)
        # Initialization
        self._initActions()
        self._configWidgets()

    def _configWidgets(self):

        # Reference config
        self.reference_field.setMinimumWidth(70)
        self.reference_field.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.reference_field.setContextMenuPolicy(Qt.CustomContextMenu)
        self.reference_field.customContextMenuRequested.connect(self._showContextMenu)

        # Grid layout
        self.grid.setAlignment(Qt.AlignTop)
        self.grid.addWidget(self.relation_label, 1, 0, Qt.AlignTop)
        self.grid.addWidget(self.relation_field, 1, 1)
        self.grid.addWidget(self.study_label, 2, 0)
        self.grid.addWidget(self.study_field, 2, 1)
        self.grid.addWidget(self.reference_label, 3, 0, Qt.AlignTop)
        self.grid.addWidget(self.reference_field, 3, 1)
        self.grid = QGridLayout()
        self.grid.setSpacing(5)
        self.setLayout(self.grid)

    def _showContextMenu(self, pos):
        global_position = self.reference_field.mapToGlobal(pos)
        my_menu = QMenu()
        my_menu.addAction(self.new_reference_action)
        my_menu.addAction(self.delete_reference_action)
        my_menu.addSeparator()
        my_menu.exec(global_position)

    def deleteReference(self):
        if hasSlelectedItems(self.reference_field):
            item = self.reference_field.selectedItems()[0].data(Qt.UserRole)
            self.reference_list.remove(item)
            self._setReferences(self.reference_list)

    def _setReferences(self, result):
        self.reference_field.clear()
        for reference in result:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, reference)
            item_text = getBibRenderFromHTML(reference.text)
            item.setText("{}".format(item_text))
            self.reference_field.insertItem(0, item)

    def createReference(self):

        dlg = NewReferenceDialog(self.parent().parent().db, RelationReference)
        if dlg.exec_():
            self.reference_list += dlg.getValues()
            self._setReferences(self.reference_list)

    def _initActions(self):
        self.delete_reference_action = QAction("Delete reference", self)
        self.delete_reference_action.triggered.connect(self.deleteReference)
        self.new_reference_action = QAction("New reference", self)
        self.new_reference_action.triggered.connect(self.createReference)

    def getData(self):
        relation = self.relation_field.toHtml()
        study = self.study_field.text().strip()
        return Relation(description=relation, study=study), self.reference_list


class NewReferenceDialog(QDialog):
    def __init__(self, db, reference_class, parent=None):
        super().__init__(parent=parent,
                         flags=Qt.WindowCloseButtonHint
                         | Qt.WindowMaximizeButtonHint
                         | Qt.WindowMinimizeButtonHint)

        # Object variables
        self.reference_class = reference_class
        self.db = db
        self.result_text = []

        # Widgets
        self.frame = ReferenceGroup()
        self.import_button = QPushButton("Import BiBteX file", self)
        self.search_ref = QPushButton("Select Reference", self)
        self.doi_button = QPushButton("By DOI")

        self.apply_button = QPushButton("Apply", self)
        self.grid = QGridLayout()

        # Initialization
        self._configWidgets()

    def setFromFile(self):
        dlg = QFileDialog()
        file_path = dlg.getOpenFileName(self, "Open BiBteX file")[0]
        if not (file_path == ""):
            # todo: check readBibsFromFile
            try:
                self.result_text += readBibsFromFile(path=file_path)
            except Exception as error:
                showError(error)
            # todo: some error if empty
            self.accept()

    def setFromBox(self):
        self.result_text += [self.frame.getText()]
        self.accept()

    def setExisting(self):
        dlg = SearchReference(self.db, self.reference_class)
        if dlg.exec_():
            self.result_text += [dlg.result_value]
            self.accept()

    def getValues(self):
        return [self.reference_class(text=x) for x in self.result_text]

    def setFromDoi(self):
        text, ok = QInputDialog.getText(self, "DOI", "Enter DOI")
        if ok:

            try:
                ref = getRefByDOI(text)
                if not ref:
                    raise Exception
            except Exception as e:
                showError("Failed retrieving references using DOI: \n{}".format(str(e)))
            self.result_text += [ref]
            self.accept()

    def _configWidgets(self):
        self.setWindowTitle("New reference")
        self.resize(900, 80)

        # Binding
        self.apply_button.clicked.connect(self.setFromBox)
        self.import_button.clicked.connect(self.setFromFile)
        self.doi_button.clicked.connect(self.setFromDoi)
        self.search_ref.clicked.connect(self.setExisting)

        # Grid Layout
        self.grid.addWidget(self.import_button, 0, 0, Qt.AlignLeft)
        self.grid.addWidget(self.doi_button, 0, 0, Qt.AlignCenter)
        self.grid.addWidget(self.search_ref, 0, 0, Qt.AlignRight)

        self.grid.addWidget(self.frame, 3, 0)
        self.grid.addWidget(self.apply_button, 4, 0, Qt.AlignRight)
        self.setLayout(self.grid)


class ReferenceGroup(QGroupBox):
    def __init__(self):
        super().__init__()
        self.last_row = 1
        self.keys = [""] + ALL_BIBTEX_ATTR
        self.fields = []

        self.grid = QGridLayout()
        self._initFirstFields()
        self._configWidgets()

    def getText(self):
        # remove filed with empty text
        self.fields = [field for field in self.fields if field[0].currentText() and field[1].text()]

        # Don't know of working this: todo: check this
        d = {key.currentText(): value.text() for key, value in self.fields}
        text = convertDictToBibStr(d)
        
        return text

    def _initFirstFields(self):
        self._addFields("author")
        self._addFields("title")
        self._addFields("pages")
        self._addFields("issue")
        self._addFields("month")
        self._addFields("year")      
        self._addFields()

    def _configWidgets(self):
        self.setLayout(self.grid)

    def _createFields(self, key_value=""):

        # Key ComboBox
        key = QComboBox(self)
        key.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        key.addItems(self.keys)
        #key.setEditable(True)
        key.setMinimumWidth(150)
        key.setCurrentText(key_value)

        # Value LineEdit
        value = QLineEdit(self)
        value.editingFinished.connect(self._addFields)

        # Grid layout
        self.grid.addWidget(key, self.last_row, 0, 1, 1, Qt.AlignTop)
        self.grid.addWidget(value, self.last_row, 1, 1, 1, Qt.AlignTop)

        # After adding new row actions
        self.last_row += 1
        self.fields.append([key, value])
        key.setFocus()

    def _addFields(self, field=""):
        if self.last_row > 1:
            if not self.fields[-1][0].currentText():
                return
        self._createFields(field)


class SearchReference(QDialog):
    def __init__(self, db, reference_class):
        super().__init__(flags=Qt.WindowMaximizeButtonHint
                         | Qt.WindowMinimizeButtonHint
                               | Qt.WindowCloseButtonHint)
        # Object variables
        self.db = db
        self.reference_class = reference_class
        self.result_value = ""

        # Widgets
        self.grid = QGridLayout(self)
        self.search_line = QLineEdit(self)
        self.search_button = QPushButton("Search", self)
        self.result_list = QListWidget()
        self.apply_button = QPushButton("Apply", self)

        # Initialization
        self._configWidgets()

    def _configWidgets(self):
        self.setWindowIcon(QIcon("logo.png"))
        self.resize(900, 700)
        # Binding
        self.apply_button.clicked.connect(self.applySelection)
        self.result_list.itemDoubleClicked.connect(self.applySelection)
        self.search_line.returnPressed.connect(self.search)
        self.search_button.clicked.connect(self.search)

        # Grid layout
        self.grid.addWidget(self.search_line, 1, 0)
        self.grid.addWidget(self.search_button, 1, 1, Qt.AlignRight)
        self.grid.addWidget(self.result_list, 2, 0, 1, 2)
        self.grid.addWidget(self.apply_button, 3, 1, Qt.AlignRight)
        self.setLayout(self.grid)

    def applySelection(self):
        if hasSlelectedItems(self.result_list):
            self.result_value = self.result_list.selectedItems()[0].data(Qt.UserRole).text
            self.accept()

    def setResult(self, references):
        self.result_list.clear()
        for reference in references:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, reference)
            item_text = getBibRenderFromHTML(reference.text)
            item.setText("{}".format(item_text))
            self.result_list.insertItem(0, item)

    def search(self):
        search_text = self.search_line.text()
        result = self.db.search_references(search_text, self.reference_class)
        self.setResult(result)


if __name__ == '__main__':
    pass