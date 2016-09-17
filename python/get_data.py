import cPickle as pickle
import nltk
from unidecode import unidecode

def porterStemmer(word):
    return unidecode(nltk.stem.porter.PorterStemmer().stem(word))


class all_data(object):
    def __init__(self,first_node,reference,second_node=None,relation=None):
        self.first_node = first_node
        self.second_node = second_node
        self.relation = relation
        self.reference = reference


class Author():
  def __init__(self,a,b):
    self.first_name = a
    self.last_name = b


class Study():
  def __init__(self,a):
    self.studyType  = a


class Reference():
  def __init__(self,title,journal,authors,year,study):
    self.title = title
    self.journal = journal
    self.authors = authors
    self.year = year
    self.study = study


class NodeDesc():
  def __init__(self,name,synonymous=None,parents=[],description=None, ID=None, children=[]):
    self.name = name
    self.synonymous = synonymous
    self.parents = parents
    self.description = description
    self.ID = ID
    self.children = children


class Edge():
  def __init__(self,relation):
    self.relation = relation


def get_edge(text_input=""):
  if len(text_input) <= 1:
    rel = get_query(message="Write the relationship: ",lower_case=False)
    return Edge(rel)
  else:
    """ input should have the following fields

    relationship

    """
    aa = text_input.split("AND")
    rel = aa[0].strip()
    return Edge(rel)


def get_node(text_input=""):
  if len(text_input) <= 1:
    concept = get_query(message="Write a concept: ")
    syn  = concept
    stem = porterStemmer(concept)
    parents = get_domain(concept)
    desc = get_query(message="If there is a description, write it here: ")
    #reference = get_reference()
    return NodeDesc(name=stem,synonymous=syn,parents=parents,description=desc)
  else:
    """ input should have the following fields, separated by "AND"

    concept ; parents ; description

    parents: Write hierarchical domain of the concept $concept, separated by ','

    """
    data = text_input.split(";")
    concept = data[0].strip()
    syn  = concept
    stem = porterStemmer(concept)
    parents = [porterStemmer(i.strip()) for i in data[2].split(",")]
    desc = data[3]
    return NodeDesc(name=stem,synonymous=syn,parents=parents,description=desc)


def get_domain(concept,ask_user=True):
  """
  param ask_user: should ask user if it doesn't find the domain?
  """
  #= use WordNet to get the domain of the concept =#
  # check if concept is noun. If so, find its domain.
  #domain_des = run(`wn $concept -domnn`)
  # if nothing found, then ask the user to write it

  if ask_user:
    uu = get_query(message="Write hierarchical domain of the concept $concept, separated by ','")
    dom = [porterStemmer(i.strip()) for i in uu.split(",")]

  return dom


def get_reference(text_input=""):
  d = {"t" : "Theoretical", "e" : "Experimental", "c" : "Computational", "theoretical" : "Theoretical", "experimental" : "Experimental", "computational" : "Computational"}
  if len(text_input) <= 1:
    rr = []
    all_ref = get_query(message="Write: reference title - journal name - authors (first name, last name and first name 2, last name 2) - year - type of study (t for theoretical, e for experimental, c for computational)",lower_case=False)
    a = all_ref.strip().split("-")

    author_list = polish_authors(a[2])
    studyType = Study(d[a[4].strip()])

  else:
    rr = []
    # order of data in the string: reference title - journal name - authors (first name, last name and first name 2, last name 2) - year - type of study (t for theoretical, e for experimental, c for computational)
    a = text_input.stirp().split(";")

    author_list = polish_authors(a[3])
    studyType = Study(d[a[5].strip()])

  ref = Reference(a[0],a[1],author_list,a[3],studyType)
  return ref


def polish_authors(authors0):
  authors = []
  for j in authors0.split("and"):
    if "," in j:
      k = j.split(",")
    else:
      k = j.split()
    first_name = k[0].strip()
    if len(k) > 1:
      last_name = k[1].strip()
    auth = Author(first_name,last_name)
    authors.append(auth)

  return authors


def get_query(lower_case=True,message=""): # get the user input
    if len(message) > 1:
      print(message+'\n')
    user_input = raw_input()
    query = user_input.strip()

    if lower_case:
      query = query.lower()

    return query


def get_data(file_path=""): # collect user data
  """
  text_input is a file that has data in every line of it.
  """
  if len(file_path) == 0:
    num = get_query(message="Do you have 2 concepts or 1? [1/2] ")
    node1 = get_node()
    if num == "2":
      node2 = get_node()
      edge = get_edge()

    else:
      node2 = None
      edge = None

    reference = get_reference()

    return all_data(first_node=node1,second_node=node2,relation=edge,reference=reference)
  else:
    """
    the file should be a ;-delimited file. lines starting with # are ommitted.
    order of columns:
    first concept; first parents(,separated); first description; second concept; second parents(,separated); second concept description;relation; reference (authors (-separated),title,journal,year,study type (experimental,computational,theoretical))
    If you don't want to fill any of the fields above, write NA.
    """
    f = open(file_path)
    all_lines = []
    for line in f:
      if not line.startswith("#"):
        fields = line.split(";")
        node1_text = ";".join(fields[0],fields[1],fields[2])
        node1 = get_node(node1_text)
        if fields[3] != "NA" and fields[3] != "na":
          node2_text = ";".join(fields[3],fields[4],fields[5])
          node2 = get_node(node2_text)
          edge = get_edge(fields[6])

        reference = get_reference(fields[7])
        alld =  all_data(first_node=node1,second_node=node2,relation=edge,reference=reference)
        all_lines.append(alld)

    return all_lines


def fill_parents(node,nodes_dict):
  """
  adds parents of a node to nodes_dict. For each parent, it adds their parents and their children
  """
  parents = node.parents
  parent_len = len(node.parents)
  if parent_len > 0:
    if parents[0] not in nodes_dict:
      nodes_dict[parents[0]] = NodeDesc(name=parents[0],children=[node.name])

    else:
      nodes_dict[parents[0]].children.append(node.name)

    if parent_len == 1:
      return nodes_dict

    else:
      if parents[-1] not in nodes_dict:
        nodes_dict[parents[-1]] = NodeDesc(name=parents[-1],children=[parents[-2]])

      else:
        nodes_dict[parents[-1]].children.append(parents[-2])

      if parent_len == 2:
        return nodes_dict

      else:
        for i,pp in enumerate(parents[1:-1]):
          if pp not in nodes_dict:
            nodes_dict[pp] = NodeDesc(name=pp,children=[parents[i]],parents = [parents[i+1:]]) # node that i is 1 less than position of pp in parents

          else:
            nodes_dict[pp].children.append(parents[i])

        return nodes_dict


def fill_dictionaries(nodes_dict, edges_dict, synonymous_dict, reference_dict, data):
  ID = len(nodes_dict) + 1 # the id of this study that is being added
  data.first_node.ID = ID
  # Filling synonymous_dict
  if data.first_node.synonymous not in synonymous_dict:
      synonymous_dict[data.first_node.synonymous] = set()
      synonymous_dict[data.first_node.synonymous].add(data.first_node.name)

  if data.second_node != None:
    if data.second_node.synonymous not in synonymous_dict:
      synonymous_dict[data.second_node.synonymous] = set()
      synonymous_dict[data.second_node.synonymous].add(data.second_node.name)
    data.second_node.ID = ID

  # Filling nodes and edges dictionaries
  if data.first_node.name in nodes_dict:
    for nn in nodes_dict[data.first_node.name]:
      if data.reference.title == nn.reference.title: # if there is a node with the same name and the same reference, it is considered as a duplicate and not added.
        print("$data.first_node.name was already in the library. Nothing added.\n")
        return nodes_dict,edges_dict,synonymous_dict

  else:
    nodes_dict[data.first_node.name] = []

  nodes_dict[data.first_node.name].append(data.first_node)
  fill_parents(data.first_node,nodes_dict)
  if data.second_node != None:
    if data.second_node.name in nodes_dict:
        nodes_dict[data.second_node.name].append(data.second_node)
    else:
        nodes_dict[data.second_node.name] = []
        nodes_dict[data.second_node.name].append(data.second_node)
    edges_dict[ID] = ["%s and %s" % (data.first_node,data.second_node),data.relation]
    fill_parents(data.second_node,nodes_dict)

  return nodes_dict,edges_dict,synonymous_dict, reference_dict


def beautiful_print(input_obj):
  if type(input_obj) == list:
    for index,i in enumerate(input_obj):
      print(" %s  %s\n" %(str(index),str(i)))

  elif type(input_obj) == str:
      print(input_obj)

  elif type(input_obj) == dict:
    for k,v in input_obj.items():
      print(" *  %s: " % str(k))
      if type(v) == str:
        print(str(v)+'\n')
      elif type(v) == list:
        print("; ".join([str(b) for b in v]))


def initial_input(nodes_dict):
  all_nodes = nodes_dict.keys()
  len_nodes = len(all_nodes)
  passed = False
  while not passed:
      query = get_query(message="What is your query? To see all available data type a")
      if query == "a":
        beautiful_print(all_nodes)
        query = get_query(message="Type the query number or name or q to quit")
        if query not in all_nodes and query != "q":
          try:
            query_num = int(query)
            if query_num < len_nodes:
              return all_nodes[query_num]
            else:
              continue
          except:
            continue
        else:
          return query

      else:
          if query not in all_nodes:
              continue
          else:
              return query


def check_query_syn(query,synonymous_dict):
    if query not in nodes_dict and query in synonymous_dict:
      query = synonymous_dict[query]
      println("This query is synonymous to %s.\n" % query)

    return query


def present(nodes_dict, edges_dict, synonymous_dict, reference_dict):
  query = initial_input(nodes_dict)

  if query == "q":
      return

  check_query_syn(query,synonymous_dict)

  beautiful_print(["d/description for description", "p/parents for more general notions", "c/children for more detailed concepts", "r/relations for relation with other concepts","n/node to change to a different concept", "a/all to print available concepts", "m/modify to modify a concept's name", "l/list for possible actions (this list)", "q to quit"])
  f = get_query()
  while f != "q":
    if f == "n" or f == "node":
      query = initial_input(nodes_dict)
      if query == "q":
        return

      check_query_syn(query,synonymous_dict)

    elif f == "list" or f == "l":
        beautiful_print(["d/description for description", "p/parents for more general notions", "c/children for more detailed concepts", "r/relations for relation with other concepts","n/node to change to a different concept", "a/all to print available concepts", "m/modify to modify a concept's name", "l/list for possible actions (this list)", "q to quit"])

    elif f == "a" or f == "all":
      beautiful_print(nodes_dict.keys())

    elif f == "d" or f == "description":
      for node in nodes_dict[query]:
        beautiful_print(["ID: %s" % str(node.ID),node.description])

      rr = get_query(message="Type an ID to see its reference, else q. ")
      if rr != "q":
        beautiful_print(reference_dict[int(rr)])

    elif f == "p" or f == "parents":
      for node in nodes_dict[query]:
        beautiful_print(["ID: %s" % str(node.ID),node.parents])

    elif f =="c" or f == "children":
      for node in nodes_dict[query]:
        beautiful_print(["ID: %s" % str(node.ID),node.children])

    elif f =="r" or f == "relations":
      ID_list = []
      for node in nodes_dict[query]:
        ID_list.append(node.ID)

      for ID in ID_list:
        beautiful_print(["ID: %s" % str(ID),edges_dict[ID]])
      rr = get_query(message="Type an ID to see its reference, else q. ")
      if rr != "q":
        beautiful_print(reference_dict[int(rr)])


def save_data(file_name, nodes_dict, edges_dict, synonymous_dict, reference_dict):
  pickle.dump([nodes_dict, edges_dict, synonymous_dict, reference_dict],open(file_name,"w"))


def read_data(file_name):
  data = pickle.load(open(file_name))
  nodes_dict,edges_dict,synonymous_dict,reference_dict = data
  return nodes_dict,edges_dict,synonymous_dict,reference_dict


def knowledgeGraph(file_name=None):
  if not file_name:
    file_name = get_query(message="No library specified. Creating a new one. Type in the file name...",lower_case=False)
    nodes_dict = {}
    edges_dict = {}
    synonymous_dict = {}
    reference_dict = {}
  else:
    nodes_dict,edges_dict,synonymous_dict,reference_dict = read_data(file_name)

  dd = get_query(message="a to add data, e to explore data, q to quit")
  while dd != "q":
    if dd == "a":
      q = get_query(message="Get data from file or input manually? (f/m)")
      if q == "m":
        data = get_data()
        nodes_dict,edges_dict,synonymous_dict, reference_dict = fill_dictionaries(nodes_dict,edges_dict,synonymous_dict,reference_dict, data)
        input_t= get_query(message="Enter to save data, else q.")
        if input_t != "q":
          save_data(file_name,nodes_dict,edges_dict,synonymous_dict, reference_dict)

      elif q == "f":
        q = get_query(message="Type the full file path ",lower_case=False)
        datas = get_data_file(q)
        for data in datas:
          nodes_dict,edges_dict,synonymous_dict, reference_dict = fill_dictionaries(nodes_dict,edges_dict,synonymous_dict, reference_dict, data)

      elif q == "q":
        continue

      else:
        q = get_query(message="Unknown input.Try again ", lower_case=False)

    elif dd == "e":
      present(nodes_dict,edges_dict,synonymous_dict,reference_dict)

    elif dd == "s":
      save_data(file_name,nodes_dict,edges_dict,synonymous_dict,reference_dict)

    beautiful_print(["a to add more data","e to explore data", "s to save the added data to file", "q to quit"])
    dd = get_query()
