import MySQLdb as mdb
import os
def start_db():
    # # for the first time only
    con = mdb.connect(host="localhost", user="root", passwd="", db="kgDb")
    cur = con.cursor()
    # cur.execute('CREATE DATABASE IF NOT EXISTS kgDb')
    # cur.close ()
    # con = cur.execute("USE kgDb")
    # cur = con.cursor()
    return con, cur

def start_tables(con, cur):
    # # check if table exists
    cur.execute("SHOW TABLES LIKE 'NodesDb'")
    a = cur.fetchone()
    if not a:
        cur.execute("CREATE TABLE NodesDb(Id INT PRIMARY KEY AUTO_INCREMENT, Usr VARCHAR(25), Node VARCHAR(225), Des VARCHAR(225), Parent VARCHAR(225), Ref VARCHAR(225), Study VARCHAR(225))")

    cur.execute("SHOW TABLES LIKE 'EdgesDb'")
    a = cur.fetchone()
    if not a:
        cur.execute("CREATE TABLE EdgesDb(Id INT PRIMARY KEY AUTO_INCREMENT, Usr VARCHAR(25), Node1 VARCHAR(225), Node2 VARCHAR(225), Des VARCHAR(225), Ref VARCHAR(225), Study VARCHAR(225))")
    # cur.close ()
    # con.close ()

    return con, cur

def setup_db():
    con, cur = start_db()
    con, cur = start_tables(con, cur)
    return con, cur

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

def read_input(inputString):
    """
    input string with the following structure:
    first concept; synonymous names(,separated);parent 1;first description;second concept;synonymous names(,separated);parent 2; second description; relation; reference (firstname1, lastname1 - firstname2, lastname2 - ...),title,journal,year);study type (experimental,computational,theoretical)

    """
    concept_1, synonymous_names_1, parent_1, description_1, concept_2, synonymous_names_2, parent_2, description_2, relation, reference, study = [i.strip() for i in inputString.strip().split(";")]

    return Inputs(concept_1, synonymous_names_1, parent_1, description_1, concept_2, synonymous_names_2, parent_2, description_2, relation, reference, study)


def read_file(filepath):
    """
    Each line should be the same format as inputString (see read_input function).
    Lines starting with # are ommited
    """
    all_inputs = []
    for line in open(filepath):
        if not line.startswith("#"):
            inputs = read_input(line)
            all_inputs.append(inputs)
    return all_inputs

def populate_nodesdb(cur, concept, syns, parent, description, reference, study, usr="testu"):
    # TODO prevent duplicate entries
    cmd = "INSERT INTO NodesDb(Usr, Node, Ref, Parent, Des, Study) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (usr, concept, reference, parent, description, study)
    cur.execute(cmd)


    # insert synonymous values as new entries with the same data
    all_syns = syns.strip().split(",")
    if len(all_syns) > 0:
        for ss in all_syns:
            cmd = "INSERT INTO NodesDb(Usr, Node, Ref, Parent, Des, Study) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (usr, ss, reference, parent, description, study)
            cur.execute(cmd)

    return cur

def populate_edgesdb(cur, concept1, concept2, description, reference, syns1="", syns2="", study="", usr="testu"):
    # TODO prevent duplicate entries
    cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (usr, concept1, concept2, description, reference, study)
    cur.execute(cmd)

    # insert synonymous values as new entries with the same data
    all_syns1 = syns1.strip().split(",")
    all_syns2 = syns2.strip().split(",")
    if len(all_syns1) > 0 and len(all_syns2) > 0:
        for s1 in xrange(len(all_syns1)):
            for s2 in xrange(len(all_syns2)):
                cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (usr, all_syns1[s1], all_syns2[s2], description, reference, study)
                cur.execute(cmd)
    elif len(all_syns1) == 0 and len(all_syns2) > 0:
            for s2 in xrange(len(all_syns2)):
                cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (usr, concept1, all_syns2[s2], description, reference, study)
                cur.execute(cmd)
    elif len(all_syns1) > 0 and len(all_syns2) == 0:
        for s1 in xrange(len(all_syns1)):
            cmd = "INSERT INTO EdgesDb(Usr, Node1, Node2, Des, Ref, Study) VALUES('%s', '%s', '%s', '%s', '%s', '%s')" % (usr, all_syns1[s1], concept2, description, reference, study)
            cur.execute(cmd)
    return cur

def add_to_tables_from_file(cur, filepath, usr="testu"):
    all_inputs = read_file(filepath)
    for ip in all_inputs:
        if len(ip.description_1.strip()) > 0:
            populate_nodesdb(cur, ip.concept_1, ip.synonymous_names_1, ip.parent_1, ip.description_1, ip.reference, ip.study, usr=usr)
        if len(ip.description_2.strip()) > 0:
            populate_nodesdb(cur, ip.concept_2, ip.synonymous_names_2, ip.parent_2, ip.description_2, ip.reference, ip.study, usr=usr)
        if len(ip.relation.strip()) > 0:
            if len(ip.concept_1.strip()) == 0 or len(ip.concept_2.strip()) == 0:
                raise Warning("Error: a concept is missing")
            populate_edgesdb(cur, ip.concept_1, ip.concept_2, ip.relation, ip.reference, ip.synonymous_names_1, ip.synonymous_names_2, ip.study, usr=usr)    

def return_node_property(cur, concept, field):
    cmd = "SELECT %s FROM NodesDb WHERE Node='%s'" % (field, concept)
    cur.execute(cmd)
    a = cur.fetchall()
    return a

def find_relations(cur, concept):
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

def get_info(cur, keyword):
    node = return_node_property(cur, keyword, field="*")
    if node:
        relations = find_relations(cur, keyword)
        return node, relations
    else:
        return None, None
