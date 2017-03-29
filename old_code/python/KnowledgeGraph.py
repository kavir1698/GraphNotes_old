import cPickle as pickle

class all_data(object):
    def __init__(self,a,b,c,d,e,f,g,h,i,j):
        self.first_node = a
        self.synonymous_1 = b
        self.node_1_parents = c
        self.first_node_description = d
        self.second_node = e
        self.synonymous_2 = f
        self.node_2_parents = g
        self.second_node_description = h
        self.relation = i
        self.reference = j

def get_query(lower_case=True): # get the user input
    if lower_case:
        query = raw_input().lower().strip()
    else:
        query = raw_input().strip()
    return query

def get_data(): # collect user data
    print("Write the first notion: "); first_node = get_query()
    print("If the notion has any synonymous names, type them. "); s1 = get_query()
    if s1 != "" and s1 != "no" and s1 != "n":
        synonymous_1 = [i.strip() for i in s1.split(",")]
    else:
        synonymous_1 = []
    print("Does it have any descriptions? (y/n) "); node_description = get_query()
    if node_description == "y" or node_description == "yes":
        print("Write the description please: "); node_1_description = get_query(lower_case=False)
    else:
        node_1_description = "NA"

    node_1_parents = ["Science"]
    print("Super-categories for this notion. Start with the fields (e.g. biology,Physics,etc.), then subfield (e.g. Evolutionary biology), and then any other relevant information that fit as super-category (e.g. Mutation can be a super category for germline mutation). write a comma separated list.")
    f = [i.strip() for i in get_query().split(",")]
    node_1_parents = node_1_parents+f

    print("Is there a second notion? (y/n) ");more = get_query()
    if more != "no" and more != "n":
        print("Write the second notion: "); second_node = get_query()
        print("If the notion has any synonymous names, type them. "); s2 = get_query()
        if s2 != "" and s2 != "no" and s2 != "n":
            synonymous_2 = [i.strip() for i in s2.split(",")]
        else:
            synonymous_2 = []
        node_2_parents = ["Science"]
        print("Super-categories for this notion. Start with the fields (e.g. biology,Physics,etc.), then subfield (e.g. Evolutionary biology), and then any other relevant information that fit as super-category (e.g. Mutation can be a super category for germline mutation). write a comma separated list.")
        f = [i.strip() for i in get_query().split(",")]
        node_2_parents = node_2_parents+f

        print("Does it have any descriptions? (y/n) ")
        node_description = get_query()
        if node_description == "y" or node_description == "yes":
            print("Write the description please: ")
            node_2_description = get_query(lower_case=False)
        else:
            node_2_description = "NA"

        print("What is the relation between the first and second notion? ")
        relation = get_query(lower_case=False)
        if len(relation) == 0:
            relation = "NA"
        print("Add the reference information.")
        print("Book/Article title: ")
        Reference = {}
        Reference["title"] = get_query(lower_case=False)
        print("Journal name / Publisher: ")
        Reference["journal"] = get_query(lower_case=False)
        print("Authors: (first name, last name;first name2, last name 2)")
        authors0 = get_query(lower_case=False)
        authors = []
        for j in authors0.split(";"):
            if "," in j:
                k = j.split(",")
            else:
                k = j.split()
            first_name = k[0].strip()
            last_name = k[1].strip()
            authors.append(last_name+","+first_name)
        Reference["author"] = authors
        print("Year: ")
        Reference["year"] = get_query(lower_case=False)
        print("Was this a theoretical, computational or experimental study? (t/c/e)");study_type=get_query()
        if study_type != "t" and study_type != "e" and study_type != "c":
            print("Unknown input, type again... ");study_type= get_query()
        d = {"t" : "Theoretical", "e" : "Experimental", "c" : "Computational"}
        Reference["study_type"] = d[study_type]
        a = first_node,synonymous_1,node_1_parents,node_1_description,second_node,synonymous_2,node_2_parents,node_2_description,relation,Reference
        data = all_data(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9])
        return data
    else:
        second_node = "NA"
        node_2_description = "NA"
        node_2_parents = "NA"
        relation = "NA"
        print("Add the reference information.")
        print("Book/Article title: ")
        Reference = {}
        Reference["title"] = get_query(lower_case=False)
        print("Journal name / Publisher: ")
        Reference["journal"] = get_query(lower_case=False)
        print("Authors: (first name, last name;first name2, last name 2)")
        authors0 = get_query(lower_case=False)
        authors = []
        for j in authors0.split(";"):
            if "," in j:
                k = j.split(",")
            else:
                k = j.split()
            first_name = k[1].strip()
            last_name = k[2].strip()
            authors.append(last_name+","+first_name)
        Reference["author"] = authors
        print("Year: ")
        Reference["year"] = get_query()
        print("Was this a theoretical, computational or experimental study? (t/c/e)");study_type= get_query()
        if study_type != "t" and study_type != "e" and study_type != "c":
            print("Unknown input, type again... ");study_type= get_query()
        d = {"t" : "Theoretical", "e" : "Experimental", "c" : "Computational"}
        Reference["study_type"] = d[study_type]
        a = first_node,synonymous_1,node_1_parents,node_1_description,second_node,synonymous_2,node_2_parents,node_2_description,relation,Reference
        data = all_data(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9])
        return data

def get_data_file(file_name): # get data from a file
    """
    the file should be a ;-delimited file. lines starting with # are ommitted.
    order of columns:
    first concept; synonymous names(,separated);first parents(,separated); first description;second concept;synonymous names(,separated);second parents(,separated); second description; relation; reference (authors (-separated),title,journal,year,study type (experimental,computational,theoretical))
    If you don't want to fill any of the fields above, write NA.
    """
    f = open(file_name)
    data_lines = []
    for index,line in enumerate(f):
        if not line.startswith("#"):
            fields = line.strip().split(";")
            dat = [0 for i in range(10)]
            dat[0],dat[1],dat[2],dat[3],dat[4],dat[5],dat[6],dat[7],dat[8] = [fields[i].strip().lower() for i in range(9)]
            dat[1] = [i.strip().lower() for i in dat[1].split(",")]
            dat[2] = [i.strip().lower() for i in dat[2].split(",")]
            dat[5] = [i.strip().lower() for i in dat[5].split(",")]
            dat[6] = [i.strip().lower() for i in dat[6].split(",")]
            reference = {}
            ref = fields[9].split(",")
            authors = []
            for j in ref[0].split("-"):
                k = j.split()
                first_name = k[0].strip()
                last_name = k[1].strip()
                authors.append(last_name+","+first_name)
            reference["author"] = authors
            reference["title"] = ref[1].strip()
            reference["journal"] = ref[2].strip()
            reference["year"] = ref[3].strip()
            reference["study_type"] = ref[4].strip()
            dat[9] = reference
            #sanity check
            for kk in range(len(dat)):
                if len(dat[kk]) == 0:
                    raise Exception("Bad input: field $kk in line $index is blank.")
            data_lines.append(dat)
    datas = []
    for a in data_lines:
        data = all_data(a[0],a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9])
        datas.append(data)
    return datas

def fill_dictionaries(nodes_dict,edges_dict,synonymous_dict,data):

    # if it is a synonymous name for an already existing node
    if data.first_node in synonymous_dict:
        data.first_node = synonymous_dict[data.first_node]
    if data.second_node in synonymous_dict:
        data.second_node = synonymous_dict[data.second_node]

    #fill the dictionaries
    if data.first_node in nodes_dict:
        for ref in nodes_dict[data.first_node]["reference"]:
            if data.reference["title"] == ref["title"]: # if there is a node with the same name and the same reference, it is considered as a duplicate and not added.
                print(data.first_node+" was already in the library. Nothing added.")
                return nodes_dict,edges_dict,synonymous_dict
        nodes_dict[data.first_node]["description"].append(data.first_node_description)
        nodes_dict[data.first_node]["reference"].append(data.reference)
        if len(nodes_dict[data.first_node]["parents"]) < data.node_1_parents:
            nodes_dict[data.first_node]["parents"]= data.node_1_parents
        if len(data.synonymous_1) > 0:
            for i in data.synonymous_1:
                synonymous_dict[i] = data.first_node
    else:
        nodes_dict[data.first_node] = {"parents":[],"description" : [], "reference" : [],"children" : [],"edges" : []}
        nodes_dict[data.first_node]["description"].append(data.first_node_description)
        nodes_dict[data.first_node]["reference"].append(data.reference)
        nodes_dict[data.first_node]["parents"]= data.node_1_parents
        if len(data.synonymous_1) > 0:
            for i in data.synonymous_1:
                synonymous_dict[i] = data.first_node

    #creating entries for the parents of node 1
    for index,parent in enumerate(data.node_1_parents):
        if not parent in nodes_dict:
            nodes_dict[parent] = {"parents" : [],"description" : [], "reference" : [],"children" : [],"edges" : []}
            if len(data.node_1_parents[(index+1):]) > 0: # if it is not the most recent parent
                nodes_dict[parent]["children"].append(data.node_1_parents[(index+1):])#adding node_1 parents that are children of this parent
            nodes_dict[parent]["children"].append(data.first_node)
        else:
            for child in data.node_1_parents[(index+1):]:
                if len(child) > 0:
                    if child not in nodes_dict[parent]["children"]: #TODO, here order of children is lost!
                        nodes_dict[parent]["children"].append(child)
            nodes_dict[parent]["children"].append(data.first_node)

    if data.second_node != "NA":
        if data.second_node in nodes_dict:
            nodes_dict[data.second_node]["description"].append(data.second_node_description)
            nodes_dict[data.second_node]["reference"].append(data.reference)
            if len(nodes_dict[data.second_node]["parents"]) < len(data.node_2_parents):
                nodes_dict[data.second_node]["parents"]= data.node_2_parents
            if len(data.synonymous_2) > 0:
                for i in data.synonymous_2:
                    synonymous_dict[i] = data.second_node
        else:
            nodes_dict[data.second_node] = {"parents" : [],"description" : [], "reference" : [],"children" : [],"edges" : []}
            nodes_dict[data.second_node]["description"].append(data.second_node_description)
            nodes_dict[data.second_node]["reference"].append(data.reference)
            nodes_dict[data.second_node]["parents"]= data.node_2_parents
            if len(data.synonymous_2) > 0:
                for i in data.synonymous_2:
                    synonymous_dict[i] = data.second_node
        #creating entries for the parents of node 2
        for index,parent in enumerate(data.node_2_parents):
            if not parent in nodes_dict:
                nodes_dict[parent] = {"parents" : [],"description" : [], "reference" : [],"children" : [],"edges" : []}
                if len(data.node_2_parents[(index+1):]) > 0: # if it is not the most recent parent
                    nodes_dict[parent]["children"].append(data.node_2_parents[(index+1):])#adding node_2 parents that are children of this parent
                nodes_dict[parent]["children"].append(data.second_node)
            else:
                for child in data.node_2_parents[(index+1):]:
                    if len(child) > 0:
                        if child not in nodes_dict[parent]["children"]: #TODO, here order of children is lost!
                            nodes_dict[parent]["children"].append(child)
                nodes_dict[parent]["children"].append(data.second_node)

        edge_key = ",".join(sorted([data.first_node,data.second_node])) # sort they node names so that they key is always unique no matter which node comes first
        nodes_dict[data.first_node]["edges"].append(edge_key)
        nodes_dict[data.second_node]["edges"].append(edge_key)
        if edge_key in edges_dict:
            edges_dict[edge_key]["relation"].append(data.relation)
            edges_dict[edge_key]["reference"].append(data.reference)
        else:
            edges_dict[edge_key] = {"relation" : [], "reference" : []}
            edges_dict[edge_key]["relation"].append(data.relation)
            edges_dict[edge_key]["reference"].append(data.reference)

    return nodes_dict,edges_dict,synonymous_dict

def beautiful_print(input):
    if type(input) == list:
        for index,i in enumerate(input):
            print(" %s  %s\n" % (index,i))
    elif type(input) == dict:
        for k,v in input:
            print(" *  %s" % k)
            print(": ")
            if type(v) == str:
                print(v+'\n')
            elif typeof(v) == list:
                print(";".join(v))
                print('\n')
    else:
        raise Exception("Error: Input of wrong type.")

def present(nodes_dict,edges_dict,synonymous_dict): # show the available data
    print("What is your query? To see all available data type a");query = get_query()
    if query == "a":
        beautiful_print(nodes_dict.keys())
        print("Type the query. ");query = get_query()
    while query not in nodes_dict and  query not in synonymous_dict:
        print("Query does not exist. Type again. ")
        query = get_query()
    if query not in nodes_dict and query in synonymous_dict:
        query = synonymous_dict[query];print("This query is synonymous to %s." % query)
    #print(nodes_dict[query]["description"])
    beautiful_print(["d/description for description", "p/parents for more general notions", "c/children for more detailed concepts", "r/relations for relation with other concepts","n/node to change to a different concept", "a/all to print available concepts", "m/modify to modify a concept's name", "q to quit"]); f = get_query()
    while f != "q":
        if f == "n" or f == "node":
            print("Type the concept");query0 = get_query()
            while query0 not in nodes_dict and query0 not in synonymous_dict:
                print("Concept does not exist, type a new one...")
                query0 = get_query()
            if query0 not in nodes_dict and  query0 in synonymous_dict:
                query = synonymous_dict[query0];print("This query is synonymous to %s." % query)
            elif query0 in nodes_dict:
                query = query0
        elif f == "m" or f == "modify":
              print("Type in the notion you want to rename. "); j = get_query()
              print("Type in the new name. "); j2 = get_query()
              nodes_dict[j2] = nodes_dict[j]
              del nodes_dict[j]
              print("Done!")
        elif f == "a" or f == "all":
            beautiful_print(nodes_dict.keys())
        elif f == "d" or f == "description":
            beautiful_print (nodes_dict[query]["description"])
            des = nodes_dict[query]["description"]
            if len(des) == 1 and des[1] != "NA" and des[1] != "":
                continue
            else:
                print("Type a number to see its reference, else q. ");rr = get_query()
                if rr != "q":
                    beautiful_print(nodes_dict[query]["reference"][int(rr)])

        elif f == "p" or f == "parents":
            beautiful_print(nodes_dict[query]["parents"])
        elif f =="c" or f == "children":
            beautiful_print(nodes_dict[query]["children"])
        elif f =="r" or f == "relations":
            beautiful_print(nodes_dict[query]["edges"])
            print("If you want to see any of the relations, type its number, otherwise q");j = get_query()
            while j != "q":
                j = int(j)
                if j > len(nodes_dict[query]["edges"]):
                    print("The number is incorrect.")
                else:
                    beautiful_print(edges_dict[nodes_dict[query]["edges"][j]]["relation"])
                    print("Type a number to see its reference, else q. ");rr = get_query()
                    if rr != "q":
                        beautiful_print(edges_dict[nodes_dict[query]["edges"][j]]["reference"][int(rr)])
                print("Write more relationships, otherwise q."); j = get_query()

        print("More actions? q to quite.");f = get_query()

def save_data(file_name,nodes_dict,edges_dict,synonymous_dict):
    dat = (nodes_dict,edges_dict,synonymous_dict)
    pickle.dump(open(file_name),dat)

def read_data(file_name):
  data = pickle.load(open(file_name))
  nodes_dict,edges_dict,synonymous_dict = data
  return nodes_dict,edges_dict,synonymous_dict

def knowledgeGraph(file_name=None): # the glue function
    if not file_name:
        print("No library specified. Creating a new one. Type in the file name...")
        file_name = get_query(lower_case=False)
        nodes_dict = {}
        edges_dict = {}
        synonymous_dict = {}
    else:
        nodes_dict,edges_dict,synonymous_dict = read_data(file_name)
    print("a to add data, e to explore data, q to quite"); dd = get_query()
    while dd != "q":
        if dd == "a":
            print("Get data from file or input manually? (f/m)");q = get_query()
            if q == "m":
                data = get_data()
                fill_dictionaries(nodes_dict,edges_dict,synonymous_dict,data)
            elif q == "f":
                print("Type the file name ");q = get_query(lower_case=False)
                datas = get_data_file(q)
                for data in datas:
                    fill_dictionaries(nodes_dict,edges_dict,synonymous_dict,data)
            elif q == "q":
                continue
            else:
                print("Unknown input.Type the file name ");q = get_query(lower_case=False)
        elif dd == "e":
            present(nodes_dict,edges_dict,synonymous_dict)
        elif dd == "s":
            save_data(file_name,nodes_dict,edges_dict,synonymous_dict)
        beautiful_print(["a to add more data","e to explore data", "s to save the added data to file", "q to quite"]); dd = get_query()


def main():
    print("If you have a library file. Type its full path and name. Otherwise, enter.");q = get_query(lower_case=False)
    if q == "":
        knowledgeGraph()
    else:
        knowledgeGraph(q)

main()
