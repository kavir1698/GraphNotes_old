import sqlite3
import tkFileDialog
import tkMessageBox as mbox
import Tkinter as tk
from itertools import product
import os
import sys


def is_sqlite3(filename):
    """
    Return True if file is an sqlite3 database, False otherwise.
    """
    from os.path import isfile, getsize

    if not isfile(filename):
        return False
    if getsize(filename) < 100: # SQLite database file header is 100 bytes
        return False

    with open(filename, 'rb') as fd:
        header = fd.read(100)

    return header[:16] == 'SQLite format 3\x00'


def get_settings():
    """
    State (last opened database and last imported file)
    are stored in './settings.txt'.
    """
    try:
        with open('settings.txt', 'r') as f:
            settings = eval(f.read())
            return settings
    except:
        return dict()


def save_settings(settings):
    """
    State (last opened database and last imported file)
    are stored in './settings.txt'.
    """
    with open('settings.txt', 'w') as f:
        f.write(str(settings))


class Inputs:
    def __init__(self, concept_1, synonymous_names_1, parent_1, description_1, concept_2, synonymous_names_2, parent_2, description_2, relation, reference, study):
        self.concept_1 = concept_1
        self.synonymous_names_1 = synonymous_names_1
        self.parent_1 = parent_1
        self.description_1 = description_1
        self.concept_2 = concept_2
        self.synonymous_names_2 = synonymous_names_2
        self.parent_2 = parent_2
        self.description_2 = description_2
        self.relation = relation
        self.reference = reference
        self.study = study


class kgraph():
    """
    Objects of this class provide an interface to concepts database.
    It allows creating such database, opening, importing data, querying it.
    """

    def __init__(self, filepath):
        self.con = sqlite3.connect(filepath)
        cur = self.con.cursor()
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS NodesDb (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Usr VARCHAR(25), Node VARCHAR(225),
                    Des VARCHAR(225), Parent VARCHAR(225),
                    Ref VARCHAR(225), Study VARCHAR(225),
                    mixed VARCHAR(500) UNIQUE ON CONFLICT IGNORE)
            """)
        cur.execute("CREATE INDEX IF NOT EXISTS node_idx ON NodesDb (Node)")
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS EdgesDb (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Usr VARCHAR(25), Node1 VARCHAR(225),
                    Node2 VARCHAR(225), Des VARCHAR(225),
                    Ref VARCHAR(225), Study VARCHAR(225),
                    mixed VARCHAR(500) UNIQUE ON CONFLICT IGNORE)
            """)
        cur.execute("CREATE INDEX IF NOT EXISTS node_idx1 ON EdgesDb (Node1)")
        cur.execute("CREATE INDEX IF NOT EXISTS node_idx2 ON EdgesDb (Node2)")
        self.con.text_factory = str

    @staticmethod
    def _read_input(inputString):
        """
        input string with the following structure:
        first concept; synonymous names(,separated);parent 1;first description;second concept;synonymous names(,separated);parent 2; second description; relation; reference (firstname1, lastname1 - firstname2, lastname2 - ...),title,journal,year);study type (experimental,computational,theoretical)

        """
        concept_1, synonymous_names_1, parent_1, description_1, concept_2, synonymous_names_2, parent_2, description_2, relation, reference, study = [i.strip() for i in inputString.strip().split(";")]

        return Inputs(concept_1, synonymous_names_1, parent_1, description_1, concept_2, synonymous_names_2, parent_2, description_2, relation, reference, study)

    @staticmethod
    def _read_file(filepath):
        """
        Each line should be the same format as inputString (see read_input function).
        Lines starting with # are ommited
        """
        all_inputs = []
        for line in open(filepath):
            if not line.startswith("#"):
                inputs = kgraph._read_input(line)
                all_inputs.append(inputs)
        return all_inputs

    def _populate_nodesdb(self, concept, syns, parent, description, reference, study, usr=""):
        with self.con:
            cur = self.con.cursor()
            command = """INSERT INTO NodesDb(Usr, Node, Ref, Parent, Des, Study, mixed)
                         VALUES(?, ?, ?, ?, ?, ?, ?)"""
            concepts = (concept + ',' + syns).split(',') if syns else [concept]
            for concept in concepts:
                mixed = "-".join([concept, description, reference])
                cur.execute(command, (usr, concept, reference, parent, description, study, mixed))

        # return cur

    def _populate_edgesdb(self, concept1, concept2, description, reference, syns1="", syns2="", study="", usr=""):
        with self.con:
            cur = self.con.cursor()
            command = """INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study, mixed)
                         VALUES (?, ?, ?, ?, ?, ?, ?)"""
            concepts1 = (concept1 + ',' + syns1).split(',') if syns1 else [concept1]
            concepts2 = (concept2 + ',' + syns2).split(',') if syns2 else [concept2]
            for concept1, concept2 in product(concepts1, concepts2):
                mixed = "-".join([concept1, concept2, description, reference])
                cur.execute(command, (usr, concept1, concept2, description, reference, study, mixed))

    def _return_node_property(self, concept, field):
        cur = self.con.cursor()
        cur.execute("SELECT ? FROM NodesDb WHERE Node=?", (field, concept))
        return cur.fetchall()

    def find_relations(self, concept):
        cur = self.con.cursor()
        cur.execute("SELECT Node1, Node2, Des, Ref From EdgesDb WHERE Node1=? OR Node2=?", (concept, concept))
        relations = {}
        for rel in cur.fetchall():
            if rel[0] == concept:
                key = rel[1]
            else:
                key = rel[0]
            relations[key] = {}
            relations[key]["relation"] = rel[2]
            relations[key]["reference"] = rel[3]
        
        return relations

    def _get_info(self, keyword):
        node = self._return_node_property(keyword, field="*")
        if node:
            relations = self._find_relations(keyword)
        else:
            node = None
            relations = None
        
        return node, relations
        
    def show_data(self, concept):
            node, relations = self._get_info(concept)
            print(node)
            print(relations)

    def add_to_graph(self, inputfile):
        inputs = kgraph._read_file(inputfile)
        for ip in inputs:
            self.add_one_to_graph(ip)

    def add_one_to_graph(self, ip):
        
        if ip.concept_1 and ip.description_1:
            self._populate_nodesdb(ip.concept_1, ip.synonymous_names_1, ip.parent_1, ip.description_1, ip.reference, ip.study)
        elif ip.concept_1 and ip.concept_2 and ip.relation:
            self._populate_nodesdb(ip.concept_1, ip.synonymous_names_1, ip.parent_1, '', '', '')

        if ip.concept_2 and ip.description_2:
            self._populate_nodesdb(ip.concept_2, ip.synonymous_names_2, ip.parent_2, ip.description_2, ip.reference, ip.study)
        elif ip.concept_2 and ip.concept_1 and ip.relation:
            self._populate_nodesdb(ip.concept_2, ip.synonymous_names_2, ip.parent_2, '', '', '')

        if ip.concept_1 and ip.concept_2 and ip.relation:
            self._populate_edgesdb(ip.concept_1, ip.concept_2, ip.relation, ip.reference, ip.synonymous_names_1, ip.synonymous_names_2, ip.study)

    def search_concepts(self, keyword):
        """Return a list of concepts that contain 'keyword'."""
        cur = self.con.cursor()
        cur.execute("SELECT Node FROM NodesDb WHERE LOWER(Node) LIKE '%' || ? || '%'", (keyword, ))
        return sorted({c for (c, ) in cur.fetchall()})

    def get_related_concepts(self, concept):
        """Return a list of concepts that are related to a certain concept."""
        cur = self.con.cursor()
        cur.execute("SELECT Node1, Node2 FROM EdgesDb WHERE Node1=? OR Node2=?", (concept, concept))
        return sorted({c2 if concept == c1 else c1 for (c1, c2) in cur.fetchall()})

    def get_description(self, concept1, concept2=None):
        """
        Return a list of (description, reference) tuples that describe either
        a relation of two given concepts or, if only one concept is given,
        just that one concept.
        """
        cur = self.con.cursor()
        if not concept1:
            return []
        elif concept2:
            cur.execute("SELECT Des, Ref FROM EdgesDb WHERE (Node1=? AND Node2=?) OR (Node2=? AND Node1=?)", (concept1, concept2, concept1, concept2))
        else:
            cur.execute("SELECT Des, Ref FROM NodesDb WHERE Node=?", (concept1, ))
        return sorted(set(cur.fetchall()))



class MainFrame(tk.Frame):
    """
    This frame represents the main logic of this program, it allows browsing the
    concepts, relations and their descriptions.
    """

    def __init__(self, parent, graph, settings):
        """
            parent - must be the root window, because it is used to set the title.
            graph - kgraph object.
            settings - a dict() of settings. It must contain a key 'last_opened'.
        """
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.settings = settings
        self.graph = graph
        self.parent.title('Browsing a database: ' + '' if 'last_opened' not in settings else settings['last_opened'])

        self.pack(fill=tk.BOTH, expand=1)

        # 'Add data' button.
        frame_add = tk.Frame(self)
        frame_add.pack(expand=1)
        self.add_button = tk.Button(frame_add, text='Add data', command=self.add_data_window)
        self.add_button.pack(padx=5, pady=5, ipadx=5, ipady=5)

        # Search entry
        frame_search = tk.Frame(self)
        frame_search.pack(fill=tk.X, expand=1, padx=5, pady=5)
        self.search_entry = tk.Entry(frame_search, width=40, justify='center')
        self.search_entry.insert(tk.END, 'Search')
        self.search_entry.focus()
        self.search_entry.selection_range(0, tk.END)
        self.search_entry.bind('<Return>', lambda _: self.update_concepts())
        self.search_entry.pack(padx=5, pady=5, ipadx=5, ipady=5)

        # A frame for selecting concept and relation.
        frame_concepts = tk.Frame(self)
        frame_concepts.pack(expand=1, padx=5, pady=5, ipadx=5, ipady=5)

        # Concept selection box.
        outer_frame1 = tk.Frame(frame_concepts)
        tk.Label(outer_frame1, text='Concepts').pack()
        outer_frame1.pack(side=tk.LEFT)
        frame1 = tk.Frame(outer_frame1)
        scrollbar1 = tk.Scrollbar(outer_frame1, orient=tk.VERTICAL)
        self.concepts_box1 = tk.Listbox(frame1, selectmode=tk.SINGLE, yscrollcommand=scrollbar1.set, width=30)
        scrollbar1.config(command=self.concepts_box1.yview)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        self.concepts_box1.configure(exportselection=False)
        self.concepts_box1.bind('<<ListboxSelect>>', self.update_related_and_description)
        self.concepts_box1.pack()
        frame1.pack(side=tk.TOP, padx=5, pady=5)

        # Related concept selection box.
        outer_frame2 = tk.Frame(frame_concepts)
        tk.Label(outer_frame2, text='Relations').pack()
        outer_frame2.pack(side=tk.LEFT)
        frame2 = tk.Frame(outer_frame2)
        scrollbar2 = tk.Scrollbar(outer_frame2, orient=tk.VERTICAL)
        self.concepts_box2 = tk.Listbox(frame2, selectmode=tk.SINGLE, yscrollcommand=scrollbar2.set, width=30)
        scrollbar2.config(command=self.concepts_box2.yview)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
        self.concepts_box2.configure(exportselection=False)
        self.concepts_box2.bind('<<ListboxSelect>>', self.update_description)
        self.concepts_box2.pack()
        frame2.pack(side=tk.TOP, padx=5, pady=5)

        # Description.
        description_frame = tk.Frame(self)
        description_frame.pack(padx=20, pady=20)
        tk.Label(description_frame, text='Descriptions').pack()
        self.description = tk.Text(description_frame, width=76)
        self.description.pack(padx=5, pady=5)


    def update_concepts(self):
        """Update concepts box based on what is written in search entry."""
        self.description.delete('1.0', tk.END)
        self.concepts_box2.delete(0, tk.END)
        concepts = self.graph.search_concepts(self.search_entry.get())
        self.concepts_box1.delete(0, tk.END)
        self.concepts_box1.insert(tk.END, *concepts)

    def update_related_and_description(self, event):
        """Update related concepts box based on what is selected in concepts box.""" 
        self.concepts_box2.delete(0, tk.END)
        self.update_description(None)
        concept_list = self.concepts_box1.curselection()
        if len(concept_list) > 0:
            concept = self.concepts_box1.get(concept_list[0])
            related_concepts = self.graph.get_related_concepts(concept)
            self.concepts_box2.insert(tk.END, *related_concepts)

    def update_description(self, event):
        """Update description box based on which concepts are selected."""
        self.description.delete('1.0', tk.END)
        idx = self.concepts_box1.curselection()
        c1 = self.concepts_box1.get(idx[0]) if idx else None
        idx = self.concepts_box2.curselection()
        c2 = self.concepts_box2.get(idx[0]) if idx else None
        descriptions = '\n\n'.join([(desc + '\n' + ref).strip() for (desc, ref) in self.graph.get_description(c1, c2) if desc or ref])
        self.description.insert(tk.END, descriptions)


    def add_data_window(self):
        """Pop a window for adding new data to the database."""
        AddDataWindow(self.graph, self, self.settings)


class NewDatabaseFrame(tk.Frame):
    """This frame allows to create a new database."""

    def __init__(self, parent, window, settings):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.settings = settings
        self.window = window
        self.window.root.title('Create a database')
        self.pack(fill=tk.BOTH, expand=1, padx=40, pady=100)

        frame1 = tk.Frame(self)
        frame1.pack(fill=tk.X)
        self.filename_entry = tk.Entry(frame1, width=60)
        self.filename_entry.bind('<Return>', lambda _: self.create_database())
        self.filename_entry.pack(fill=tk.X, expand=1, padx=30, pady=10, ipadx=5, ipady=5)

        if 'last_opened' in settings:
            self.filename_entry.insert(0, os.path.dirname(settings['last_opened']))

        frame2 = tk.Frame(self)
        frame2.pack()

        self.browse_button = tk.Button(frame2, text="Choose directory", command=self.fill_directory)
        self.browse_button.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5, ipadx=5, ipady=5)

        self.create_button = tk.Button(frame2, text="Create database", command=self.create_database)
        self.create_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5, ipady=5)

    def fill_directory(self):
        """
        This function tries to get the directory where the last opened database was
        and write this directory path to self.filename_entry.
        """
        if 'last_opened' in self.settings:
            default_dir = os.path.dirname(self.settings['last_opened'])
        else:
            default_dir = ''
        new_dir = tkFileDialog.askdirectory(initialdir=default_dir)
        if new_dir:
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, new_dir)


    def create_database(self):
        """
        This function creates a new database with a path that is written
        in self.filename_entry. If path links to an already existing file,
        show an error box.
        """

        filename = self.filename_entry.get()
        if os.path.isfile(filename):
            mbox.showerror('Error', filename + ' already exists')
        else:
            self.settings['last_opened'] = filename
            save_settings(self.settings)
            graph = kgraph(filename)
            self.pack_forget()
            self.window.main_frame = MainFrame(self.parent, graph, self.settings)
            self.window.root.title(filename)



class MainWindow:

    def __init__(self, settings):
        """
        settings - a dictionary with optional settings ('last_opened', 'last_imported').
        """
        self.create_main_window()
        self.create_main_menu()
        self.main_frame = None
        self.new_db_frame = None
        self.init_frame = None

        # Try to open last opened file. If it is unknown (or does not exist), create
        # 'Open database' and 'Create a new database' buttons.
        self.settings = settings
        if 'last_opened' in settings and os.path.isfile(settings['last_opened']) and is_sqlite3(settings['last_opened']):
            self.graph = kgraph(settings['last_opened'])
            self.create_main_frame()
        else:
            self.init_frame = tk.Frame(self.root)
            self.init_frame.pack(pady=60, padx=50)
            open_button = tk.Button(self.init_frame, text='Open database', command=self.open_database)
            open_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5, ipady=5)
            create_db_button = tk.Button(self.init_frame, text='Create a new database', command=self.create_new_db_frame)
            create_db_button.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5, ipady=5)

        self.root.mainloop()

    def create_main_window(self):
        self.root = tk.Tk()
        self.root.geometry('-400+100')
        self.root.title('Open database')

    def create_main_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        menu = tk.Menu(menu_bar)
        menu.add_command(label='Open database', command=self.open_database)
        menu.add_command(label='Create a new database', command=self.create_new_db_frame)
        menu_bar.add_cascade(label="File", menu=menu)

    def open_database(self):
        """This function opens a file picker dialog and opens the selected database."""
        if 'last_opened' in self.settings and os.path.isdir(self.settings['last_opened']):
            filename = tkFileDialog.askopenfilename(initialdir=os.path.dirname(self.settings['last_opened']))
        else:
            filename = tkFileDialog.askopenfilename()

        if filename:
            if os.path.isfile(filename):
                if is_sqlite3(filename):
                    self.settings['last_opened'] = os.path.abspath(filename)
                    save_settings(self.settings)
                    self.graph = kgraph(filename)
                    self.create_main_frame()
                    self.root.title('Browsing database: ' + filename)
                else:
                    mbox.showerror("Error", filename + " is not a sqlite3 database.")
            else:
                mbox.showerror("Error", "File " + filename + " does not exist.")

    def create_main_frame(self):
        # We want to hide the frames that are filling the window at the moment
        # before creating a new frame.
        if self.main_frame != None:
            self.main_frame.pack_forget()
        if self.new_db_frame != None:
            self.new_db_frame.pack_forget()
        if self.init_frame != None:
            self.init_frame.pack_forget()
        self.main_frame = MainFrame(self.root, self.graph, self.settings)

    def create_new_db_frame(self):
        # We want to hide the frames that are filling the window at the moment
        # before creating a new frame.
        if self.main_frame != None:
            self.main_frame.pack_forget()
        if self.new_db_frame != None:
            self.new_db_frame.pack_forget()
        if self.init_frame != None:
            self.init_frame.pack_forget()
        self.new_db_frame = NewDatabaseFrame(self.root, self, self.settings)


class AddDataWindow:
    """
    This represents the window for adding new data manually
    or importing it from a file.
    """

    def __init__(self, graph, caller, settings):
        self.graph = graph
        self.settings = settings
        self.root = tk.Tk()
        self.root.geometry('-150+180')
        self.root.title('Add data: ' + settings['last_opened'])

        submit_file_button = tk.Button(self.root, text='Add data from a file', command=self.submit_file)
        submit_file_button.grid(row=0, column=1, columnspan=2, padx=5, pady=5, ipadx=5, ipady=5)

        # This describes positions for field entries.
        # (field identifier, field entry label, row, column, column span, row span)
        self.fd = [
            ('concept_1', 'Concept 1', 1, 0, 1, 1),
            ('synonymous_names_1', 'Synonymous names 1', 2, 0, 1, 1),
            ('parent_1', 'Parent 1', 3, 0, 1, 1),
            ('description_1', 'Description 1', 4, 0, 1, 1),
            ('concept_2', 'Concept 2', 1, 2, 1, 1),
            ('synonymous_names_2', 'Synonymous names 2', 2, 2, 1, 1),
            ('parent_2', 'Parent 2', 3, 2, 1, 1),
            ('description_2', 'Description 2', 4, 2, 1, 1),
            ('relation', 'Relation', 5, 0, 3, 1),
            ('reference', 'Reference', 6, 0, 3, 1),
            ('study', 'Study', 7, 0, 3, 1)
        ]

        self.fields = []
        for key, descr, row, col, colspan, rowspan in self.fd:
            tk.Label(self.root, text=descr+':').grid(row=row, column=col, padx=5, pady=5, sticky=tk.E)
            self.fields.append(tk.Entry(self.root))
            self.fields[-1].grid(row=row, column=col+1, rowspan=rowspan, columnspan=colspan, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)



        self.submit_button = tk.Button(self.root, text='Submit', command=self.submit)
        self.submit_button.grid(row=8, column=3, padx=5, pady=5, sticky=tk.W+tk.E+tk.N+tk.S)

        self.root.mainloop()

    def submit(self):
        """
        This function reads what's written in entry boxes and adds data
        to the concepts graph.
        """
        field_input = Inputs(*[f.get() for f in self.fields])
        try:
            self.graph.add_one_to_graph(field_input)
            self.graph.con.commit()
            mbox.showinfo('Success', 'Record was added to the database.')
        except:
            mbox.showerror("Error", "Something went wrong: " + sys.exc_info()[0])
        for f in self.fields:
            f.delete(0, tk.END)

    def submit_file(self):
        """
        This function tries to data from a file to the concepts graph.
        It shows either a success or error box afterwards.
        """
        last_dir = ''
        if 'last_imported' in self.settings:
            last_dir = os.path.dirname(self.settings['last_imported'])
        filename = tkFileDialog.askopenfilename(initialdir=last_dir)
        if filename:
            try:
                self.graph.add_to_graph(filename)
                self.graph.con.commit()
                self.settings['last_imported'] = os.path.abspath(filename)
                save_settings(settings)
                mbox.showinfo("Success", "Data from %s imported." % filename)
            except:
                mbox.showerror("Error", "Something went wrong: %s" % sys.exc_info()[0])



if __name__ == '__main__':
    settings = get_settings()
    MainWindow(settings)

