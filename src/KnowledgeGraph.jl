
# version 0.1

module KnowledgeGraph
using HDF5,JLD


type all_data
  first_node::ASCIIString
  synonymous_1::Array{ASCIIString}
  node_1_parents::Array{ASCIIString}
  first_node_description::ASCIIString
  second_node::ASCIIString
  synonymous_2::Array{ASCIIString}
  node_2_parents::Array{ASCIIString}
  second_node_description::ASCIIString
  relation::ASCIIString
  reference::Dict{String,Any}
end


type Node
  name::String
  synonymous::Array{ASCIIString}
  parents::Array{ASCIIString}
  reference::Array
end


Node() = Node("NA",Array{ASCIIString}(0),Array{ASCIIString}(0),Dict{String,Any})


function get_query(;lower_case::Bool=true) # get the user input
  if lower_case
    query = lowercase(strip(readline(STDIN)))
  else
    query = strip(readline(STDIN))
  end
  return query
end


function get_reference()
  println("Book/Article title: ")
  Reference = Dict{String,Any}()
  Reference["title"] = get_query(lower_case=false)
  println("Journal name / Publisher: ")
  Reference["journal"] = get_query(lower_case=false)
  println("Authors: (first name, last name and first name2, last name2)")
  authors0 = get_query(lower_case=false)
  authors = Array{String}(0)
  for j in split(authors0,"and")
    if contains(j,",")
      k = split(j,",")
    else
      k = split(j)
    end
    first_name = strip(k[1])
    if length(k) > 1
      last_name = strip( k[2])
    end
    push!(authors,string(last_name,",",first_name))
  end
  Reference["author"] = authors
  println("Year: ")
  Reference["year"] = get_query(lower_case=false)
  println("Was this a theoretical, computational or experimental study? (t/c/e)");study_type=get_query()
  if study_type != "t" && study_type != "e" && study_type != "c"
    println("Unknown input, type again... ");study_type= get_query()
  end
  d = Dict("t" => "Theoretical", "e" => "Experimental", "c" => "Computational")
  Reference["study_type"] = d[study_type]
  return Reference
end


function get_data() # collect user data
  println("Write the first notion: "); first_node = get_query()
  println("If the notion has any synonymous names, type them. "); s1 = get_query()
  if s1 != "" && s1 != "no" && s1 != "n"
    synonymous_1 = [strip(i) for i in split(s1,",")]
  else
    synonymous_1 = Array{ASCIIString}(0)
  end
  println("Does it have any descriptions? (y/n) "); node_description = get_query()
  if node_description == "y" || node_description == "yes"
    println("Write the description please: "); node_1_description = get_query(lower_case=false)
  else
    node_1_description = "NA"
  end

  node_1_parents = ["Science"]
  println("Super-categories for this notion. Start with the fields (e.g. biology,Physics,etc.), then subfield (e.g. Evolutionary biology), and then any other relevant information that fit as super-category (e.g. Mutation can be a super category for germline mutation). write a comma separated list.")
  f = [strip(i) for i in split(get_query(),",")]
  node_1_parents = [node_1_parents;f]

  println("Is there a second notion? (y/n) ");more = get_query()
  if more != "no" && more != "n"
    println("Write the second notion: "); second_node = get_query()
    println("If the notion has any synonymous names, type them. "); s2 = get_query()
    if s2 != "" && s2 != "no" && s2 != "n"
      synonymous_2 = [strip(i) for i in split(s2,",")]
    else
      synonymous_2 = Array{ASCIIString}(0)
    end
    node_2_parents = ["Science"]
    println("Super-categories for this notion. Start with the fields (e.g. biology,Physics,etc.), then subfield (e.g. Evolutionary biology), and then any other relevant information that fit as super-category (e.g. Mutation can be a super category for germline mutation). write a comma separated list.")
    f = [strip(i) for i in split(get_query(),",")]
    node_2_parents = [node_2_parents;f]

    println("Does it have any descriptions? (y/n) ")
    node_description = get_query()
    if node_description == "y" || node_description == "yes"
      println("Write the description please: ")
      node_2_description = get_query(lower_case=false)
    else
      node_2_description = "NA"
    end

    println("What is the relation between the first and second notion? ")
    relation = get_query(lower_case=false)
    if length(relation) == 0
      relation = "NA"
    end
    println("Add the reference information.")
    Reference = get_reference()
    a = first_node,synonymous_1,node_1_parents,node_1_description,second_node,synonymous_2,node_2_parents,node_2_description,relation,Reference
    data = all_data(a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9],a[10])
    return data
  else
    second_node = "NA"
    node_2_description = "NA"
    node_2_parents =  Array{ASCIIString}(0)
    synonymous_2 =  Array{ASCIIString}(0)
    relation = "NA"
    println("Add the reference information.")
    Reference = get_reference()
    a = first_node,synonymous_1,node_1_parents,node_1_description,second_node,synonymous_2,node_2_parents,node_2_description,relation,Reference
    data = all_data(a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9],a[10])
    return data
  end
end


function get_data_file(file_name::ASCIIString) # get data from a file
  #=
  the file should be a ;-delimited file. lines starting with # are ommitted.
  order of columns:
  first concept; synonymous names(,separated);first parents(,separated); first description;second concept;synonymous names(,separated);second parents(,separated); second description; relation; reference (authors (-separated),title,journal,year,study type (experimental,computational,theoretical))
  If you don't want to fill any of the fields above, write NA.
  =#
  f = open(file_name)
  data_lines = Array{Any}(0)
  for (index,line) in enumerate(eachline(f))
    if !startswith(line,"#")
      fields = split(strip(line),";")
      dat = Array{Any}(10)
      dat[1],dat[2],dat[3],dat[4],dat[5],dat[6],dat[7],dat[8],dat[9] = [lowercase(strip(fields[i])) for i in 1:9]
      dat[2] = [lowercase(strip(convert(ASCIIString,i))) for i in split(dat[2],",")]
      dat[3] = [lowercase(strip(convert(ASCIIString,i))) for i in split(dat[3],",")]
      dat[6] = [lowercase(strip(convert(ASCIIString,i))) for i in split(dat[6],",")]
      dat[7] = [lowercase(strip(convert(ASCIIString,i))) for i in split(dat[7],",")]

      dat[1] = convert(ASCIIString,dat[1])
      dat[4] = convert(ASCIIString,dat[4])
      dat[5] = convert(ASCIIString,dat[5])
      dat[8] = convert(ASCIIString,dat[8])
      dat[9] = convert(ASCIIString,dat[9])

      reference = Dict{ASCIIString,Any}()
      ref = split(fields[10],"-")
      authors = Array{ASCIIString}(0)
      for j in split(ref[1],"AND")
        k = split(j,",")
        first_name = strip(k[1])
        last_name = strip( k[2])
        push!(authors,string(last_name,",",first_name))
      end
      reference["author"] = authors
      reference["title"] = strip(ref[2])
      reference["journal"] = strip(ref[3])
      reference["year"] = strip(ref[4])
      reference["study_type"] = strip(ref[5])
      dat[10] = reference
      #sanity check
      for kk in 1:length(dat)
        if length(dat[kk]) == 0
          throw("Bad input: field $kk in line $index is blank.")
        end
      end
      push!(data_lines,dat)
    end
  end
  datas = Array{Any}(0)
  for a in data_lines
    data = all_data(a[1],a[2],a[3],a[4],a[5],a[6],a[7],a[8],a[9],a[10])
    push!(datas,data)
  end
  return datas
end


# function export_to_file(file_name::String,nodes_dict,edges_dict,synonymous_dict)
#   #=
#   first concept; synonymous names(,separated);first parents(,separated); first description;second concept;synonymous names(,separated);second parents(,separated); second description; relation; reference (authors (-separated),title,journal,year,study type (experimental,computational,theoretical))
#   If you don't want to fill any of the fields above, write NA.
#   =#
#   for node in nodes_dict
#
#   end
# end


function fill_dictionaries!(nodes_dict,edges_dict,synonymous_dict,data::all_data)

  # if it is a synonymous name for an already existing node
  if haskey(synonymous_dict,data.first_node)
    data.first_node = synonymous_dict[data.first_node]
  end
  if haskey(synonymous_dict,data.second_node)
    data.second_node = synonymous_dict[data.second_node]
  end

  #fill the dictionaries
  if haskey(nodes_dict,data.first_node)
    for ref in nodes_dict[data.first_node]["reference"]
      if data.reference["title"] == ref["title"] # if there is a node with the same name and the same reference, it is considered as a duplicate and not added.
        println("$data.first_node was already in the library. Nothing added.")
        return nodes_dict,edges_dict,synonymous_dict
      end
    end
    push!(nodes_dict[data.first_node]["description"],data.first_node_description)
    push!(nodes_dict[data.first_node]["reference"],data.reference)
    if length(nodes_dict[data.first_node]["parents"]) < length(data.node_1_parents)
      nodes_dict[data.first_node]["parents"]= data.node_1_parents
    end
    if length(data.synonymous_1) > 0
      for i in data.synonymous_1
        synonymous_dict[i] = data.first_node
      end
    end
  else
    nodes_dict[data.first_node] = Dict("parents"=>[],"description" => [], "reference" => [],"children" => [],"edges" => [])
    push!(nodes_dict[data.first_node]["description"],data.first_node_description)
    push!(nodes_dict[data.first_node]["reference"],data.reference)
    nodes_dict[data.first_node]["parents"]= data.node_1_parents
    if length(data.synonymous_1) > 0
      for i in data.synonymous_1
        synonymous_dict[i] = data.first_node
      end
    end
  end

  #creating entries for the parents of node 1
  for (index,parent) in enumerate(data.node_1_parents)
    if !haskey(nodes_dict,parent)
      nodes_dict[parent] = Dict("parents"=>[],"description" => [], "reference" => [],"children" => [],"edges" => [])
      if length(data.node_1_parents[(index+1):end]) > 0 # if it is not the most recent parent
        push!(nodes_dict[parent]["children"],data.node_1_parents[(index+1):end])#adding node_1 parents that are children of this parent
      end
      push!(nodes_dict[parent]["children"], data.first_node)
    else
      for child in data.node_1_parents[(index+1):end]
        if length(child) > 0
          if !in(child,nodes_dict[parent]["children"]) #TODO, here order of children is lost!
            push!(nodes_dict[parent]["children"],child)
          end
        end
      end
      push!(nodes_dict[parent]["children"], data.first_node)
    end
  end

  if data.second_node != "NA"
    if haskey(nodes_dict,data.second_node)
      push!(nodes_dict[data.second_node]["description"],data.second_node_description)
      push!(nodes_dict[data.second_node]["reference"],data.reference)
      if length(nodes_dict[data.second_node]["parents"]) < length(data.node_2_parents)
        nodes_dict[data.second_node]["parents"]= data.node_2_parents
      end
      if length(data.synonymous_2) > 0
        for i in data.synonymous_2
          synonymous_dict[i] = data.second_node
        end
      end
    else
      nodes_dict[data.second_node] = Dict("parents"=>[],"description" => [], "reference" => [],"children" => [],"edges" => [])
      push!(nodes_dict[data.second_node]["description"],data.second_node_description)
      push!(nodes_dict[data.second_node]["reference"],data.reference)
      nodes_dict[data.second_node]["parents"]= data.node_2_parents
      if length(data.synonymous_2) > 0
        for i in data.synonymous_2
          synonymous_dict[i] = data.second_node
        end
      end
    end
    #creating entries for the parents of node 2
    for (index,parent) in enumerate(data.node_2_parents)
      if !haskey(nodes_dict,parent)
        nodes_dict[parent] = Dict("parents"=>[],"description" => [], "reference" => [],"children" => [],"edges" => [])
        if length(data.node_2_parents[(index+1):end]) > 0 # if it is not the most recent parent
          push!(nodes_dict[parent]["children"],data.node_2_parents[(index+1):end])#adding node_2 parents that are children of this parent
        end
        push!(nodes_dict[parent]["children"], data.second_node)
      else
        for child in data.node_2_parents[(index+1):end]
          if length(child) > 0
            if !in(child,nodes_dict[parent]["children"]) #TODO, here order of children is lost!
              push!(nodes_dict[parent]["children"],child)
            end
          end
        end
        push!(nodes_dict[parent]["children"], data.second_node)
      end
    end

    edge_key = join(sort([data.first_node,data.second_node]),",") # sort they node names so that they key is always unique no matter which node comes first
    push!(nodes_dict[data.first_node]["edges"],edge_key)
    push!(nodes_dict[data.second_node]["edges"],edge_key)
    if haskey(edges_dict,edge_key)
      push!(edges_dict[edge_key]["relation"],data.relation)
      push!(edges_dict[edge_key]["reference"],data.reference)
    else
      edges_dict[edge_key] = Dict("relation" => [], "reference" => [])
      push!(edges_dict[edge_key]["relation"],data.relation)
      push!(edges_dict[edge_key]["reference"],data.reference)
    end
  end
  return nodes_dict,edges_dict,synonymous_dict
end


function beautiful_print(input::Array)
  for (index,i) in enumerate(input)
    println(" $index  $i")
  end
end


function beautiful_print(input::Dict)
  for (k,v) in input
    print(" *  $k")
    print(": ")
    if typeof(v) == ASCIIString
      println(v)
    elseif typeof(v) <: Array
      println(join(v,"; "))
    end
  end
end


function present(nodes_dict::Dict,edges_dict::Dict,synonymous_dict) # show the available data
  println("What is your query? To see all available data type a");query = get_query()
  if query == "a"
    beautiful_print(collect(keys(nodes_dict)))
    println("Type the query. ");query = get_query()
  end
  while !haskey(nodes_dict,query) && !haskey(synonymous_dict,query)
    println("Query does not exist. Type again. ")
    query = get_query()
  end
  if !haskey(nodes_dict,query) && haskey(synonymous_dict,query)
    query = synonymous_dict[query];println("This query is synonymous to $(query).")
  end
  #println(nodes_dict[query]["description"])
  beautiful_print(["d/description for description", "p/parents for more general notions", "c/children for more detailed concepts", "r/relations for relation with other concepts","n/node to change to a different concept", "a/all to print available concepts", "m/modify to modify a concept's name", "l/list for possible actions (this list)", "q to quit"]); f = get_query()
  while f != "q"
    if f == "n" || f == "node"
      println("Type the concept");query0 = get_query()
      while !haskey(nodes_dict,query0) && !haskey(synonymous_dict,query0)
        println("Concept does not exist, type a new one...")
        query0 = get_query()
      end
      if !haskey(nodes_dict,query0) && haskey(synonymous_dict,query0)
        query = synonymous_dict[query0];println("This query is synonymous to $(query).")
      elseif haskey(nodes_dict,query0)
        query = query0
      end
    elseif f == "list" || f == "l"
        beautiful_print(["d/description for description", "p/parents for more general notions", "c/children for more detailed concepts", "r/relations for relation with other concepts","n/node to change to a different concept", "a/all to print available concepts", "m/modify to modify a concept's name", "l/list for possible actions (this list)", "q to quit"])
    elseif f == "m" || f == "modify"
      println("Type in the notion you want to rename. "); j = get_query()
      println("Type in the new name. "); j2 = get_query()
      nodes_dict[j2] = nodes_dict[j]
      delete!(nodes_dict,j)
      println("Done!")
    elseif f == "a" || f == "all"
      beautiful_print(collect(keys(nodes_dict)))
    elseif f == "d" || f == "description"
      beautiful_print (nodes_dict[query]["description"])
      des = nodes_dict[query]["description"]
      if des[1] != "NA" && des[1] != ""
        println("Type a number to see its reference, else q. ");rr = get_query()
        if rr != "q"
          beautiful_print(nodes_dict[query]["reference"][parse(Int,rr)])
        end
      end
    elseif f == "p" || f == "parents"
      beautiful_print(nodes_dict[query]["parents"])
    elseif f =="c" || f == "children"
      beautiful_print(nodes_dict[query]["children"])
    elseif f =="r" || f == "relations"
      beautiful_print(nodes_dict[query]["edges"])
      println("If you want to see any of the relations, type its number, otherwise q");j = get_query()
      nonint = false
      try
        parse(Int,j)
      catch
	nonint = true
      end
      if nonint && j != "q"
        println("Invalid request.")
      else
	      while j != "q"
		j = parse(Int,j)
		if j > length(nodes_dict[query]["edges"])
		  println("The number is incorrect.")
		else
		  beautiful_print(edges_dict[nodes_dict[query]["edges"][j]]["relation"])
		  println("Type a number to see its reference, else q. ");rr = get_query()
		  if rr != "q"
		    beautiful_print(edges_dict[nodes_dict[query]["edges"][j]]["reference"][parse(Int,rr)])
		  end
		end
		println("Write more relationships, otherwise q."); j = get_query()
	      end
      end
    end
    println("More actions? q to quit.");f = get_query()
  end
end


function save_data(file_name::ASCIIString,nodes_dict::Dict,edges_dict::Dict,synonymous_dict::Dict)
  save(file_name,"library",(nodes_dict,edges_dict,synonymous_dict))
end


function read_data(file_name::ASCIIString)
  data = load(file_name,"library")
  nodes_dict,edges_dict,synonymous_dict = data
  return nodes_dict,edges_dict,synonymous_dict
end


function knowledgeGraph(file_name=nothing) # the glue function
  if file_name == nothing
    println("No library specified. Creating a new one. Type in the file name...")
    file_name = get_query(lower_case=false)
    nodes_dict = Dict{ASCIIString,Any}()
    edges_dict = Dict{ASCIIString,Any}()
    synonymous_dict = Dict{ASCIIString,ASCIIString}()
  else
    nodes_dict,edges_dict,synonymous_dict = read_data(file_name)
  end
  println("a to add data, e to explore data, q to quit"); dd = get_query()
  while dd != "q"
    if dd == "a"
      println("Get data from file or input manually? (f/m)");q = get_query()
      if q == "m"
        data = get_data()
        fill_dictionaries!(nodes_dict,edges_dict,synonymous_dict,data)
        println("Enter to save data, else q.");input= get_query()
        if input != "q"
          save_data(file_name,nodes_dict,edges_dict,synonymous_dict)
        end
      elseif q == "f"
        println("Type the file name ");q = get_query(lower_case=false)
        datas = get_data_file(q)
        for data in datas
          fill_dictionaries!(nodes_dict,edges_dict,synonymous_dict,data)
        end
      elseif q == "q"
        continue
      else
        println("Unknown input.Type the file name ");q = get_query(lower_case=false)
      end
    elseif dd == "e"
      present(nodes_dict,edges_dict,synonymous_dict)
    elseif dd == "s"
      save_data(file_name,nodes_dict,edges_dict,synonymous_dict)
    end
    beautiful_print(["a to add more data","e to explore data", "s to save the added data to file", "q to quit"]); dd = get_query()
  end
end

end #module
