# This algorithm saves data in a database
import MySQLdb as mdb
# import os

# os.system("sudo /etc/init.d/mysql start")  # run this the first time that you start your machine.

# TODO autmatically create the testu user here, but not before.
# TODO create database here but not before.
# BUG syn names for node 2 are not in the table. Why?
# TODO add more than one classification of papers, e.g. theoretical and computational
# TODO show all available data without synonymous values
# TODO new class to present data beautifully.

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
    def __init__(self):
        self.con = kgraph._setup_db()

    @staticmethod
    def _start_db():
        # # for the first time only
        con = mdb.connect(host="localhost", user="testu", passwd="testu", db="kgDb")
        # cur.execute('CREATE DATABASE IF NOT EXISTS kgDb')
        # con = cur.execute("USE kgDb")
        return con 

    @staticmethod
    def _start_tables(con):
        # # check if table exists
        with con:
            cur = con.cursor()
            cur.execute("SHOW TABLES LIKE 'NodesDb'")
            a = cur.fetchone()
            if not a:
                cur.execute("CREATE TABLE NodesDb(Id INT PRIMARY KEY AUTO_INCREMENT, Usr VARCHAR(25), Node VARCHAR(225), Des VARCHAR(225), Parent VARCHAR(225), Ref VARCHAR(225), Study VARCHAR(225), mixed VARCHAR(500), UNIQUE (mixed))")

            cur.execute("SHOW TABLES LIKE 'EdgesDb'")
            a = cur.fetchone()
            if not a:
                cur.execute("CREATE TABLE EdgesDb(Id INT PRIMARY KEY AUTO_INCREMENT, Usr VARCHAR(25), Node1 VARCHAR(225), Node2 VARCHAR(225), Des VARCHAR(225), Ref VARCHAR(225), Study VARCHAR(225), mixed VARCHAR(500), UNIQUE (mixed))")
    
    @staticmethod
    def _setup_db():
        con = kgraph._start_db()
        kgraph._start_tables(con)
        return con
    
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

    def _populate_nodesdb(self, concept, syns, parent, description, reference, study, usr="testu"):
        with self.con:
            cur = self.con.cursor()
            mixed = "-".join([concept, description, reference])
            cmd = "INSERT INTO NodesDb(Usr, Node, Ref, Parent, Des, Study, mixed) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (usr, concept, reference, parent, description, study, mixed)
            try:
                cur.execute(cmd)
                output = "added"
            except:
                output = "failed"
            if output == "added":
                # insert synonymous values as new entries with the same data
                all_syns = syns.strip().split(",")
                if len(all_syns) > 0:
                    for ss in all_syns:
                        mixed = "-".join([ss, description, reference])
                        cmd = "INSERT INTO NodesDb(Usr, Node, Ref, Parent, Des, Study, mixed) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (usr, ss, reference, parent, description, study, mixed)
                        cur.execute(cmd)

        # return cur

    def _populate_edgesdb(self, concept1, concept2, description, reference, syns1="", syns2="", study="", usr="testu"):
        with self.con:
            cur = self.con.cursor()
            mixed = "-".join([concept1, concept2, description, reference])
            cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study, mixed) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (usr, concept1, concept2, description, reference, study, mixed)
            try:
                cur.execute(cmd)
                output = "added"
            except:
                output = "failed"
            if output == "added":
                # insert synonymous values as new entries with the same data
                all_syns1 = syns1.strip().split(",")
                all_syns2 = syns2.strip().split(",")
                if len(all_syns1) > 0 and len(all_syns2) > 0:
                    for s1 in xrange(len(all_syns1)):
                        for s2 in xrange(len(all_syns2)):
                            mixed = "-".join([all_syns1[s1], all_syns2[s2], description, reference])
                            cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study, mixed) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (usr, all_syns1[s1], all_syns2[s2], description, reference, study, mixed)
                            cur.execute(cmd)
                elif len(all_syns1) == 0 and len(all_syns2) > 0:
                    for s2 in xrange(len(all_syns2)):
                        mixed = "-".join([concept1, all_syns2[s2], description, reference])
                        cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study, mixed) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (usr, concept1, all_syns2[s2], description, reference, study, mixed)
                        cur.execute(cmd)
                elif len(all_syns1) > 0 and len(all_syns2) == 0:
                    for s1 in xrange(len(all_syns1)):
                        mixed = "-".join([all_syns1[s1], concept2, description, reference])
                        cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study, mixed) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (usr, all_syns1[s1], concept2, description, reference, study, mixed)
                        cur.execute(cmd)
        # return cur

    def _return_node_property(self, concept, field):
        with self.con:
            cur = self.con.cursor()
            cmd = "SELECT %s FROM NodesDb WHERE Node='%s'" % (field, concept)
            cur.execute(cmd)
            a = cur.fetchall()
        
        return a

    def _find_relations(self, concept):
        with self.con:
            cur = self.con.cursor()
            cmd = "SELECT Node1, Node2, Des, Ref From EdgesDb WHERE Node1='%s' OR Node2='%s'" % (concept, concept)
            cur.execute(cmd)
            a = cur.fetchall()

            relations = {}
            for rel in a:
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
            self._populate_nodesdb(ip.concept_1, ip.synonymous_names_1, ip.parent_1, ip.description_1, ip.reference, ip.study)
            if ip.concept_2 and ip.relation:
                if ip.description_2:
                    self._populate_nodesdb(ip.concept_2, ip.synonymous_names_2, ip.parent_2, ip.description_2, ip.reference, ip.study)
                self._populate_edgesdb(ip.concept_1, ip.concept_2, ip.relation, ip.reference, ip.synonymous_names_1, ip.synonymous_names_2, ip.study)
