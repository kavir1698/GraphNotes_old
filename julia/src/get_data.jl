using HDF5,JLD
using PyCall
@pyimport nltk

porterStemmer = nltk.stem[:porter][:PorterStemmer]()[:stem]



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
  reference::Dict{AbstractString,Any}
end


type Author
  firstName::AbstractString
  lastName::AbstractString
end


type Study
  studyType::ASCIIString
end


type Reference
  title::AbstractString
  journal::ASCIIString
  authors::Array{Author}
  year::ASCIIString
  study::Study
end


type NodeDesc # node description
  name::AbstractString
  synonymous::ASCIIString
  parents::Array{ASCIIString}
  id::Int
end


type Edge
  relation::ASCIIString
  id::Int
end


function get_edge()
  rel = get_query(message="Write the relationship: ",lower_case=false)
  #reference = get_reference()
  return Edge(rel)
end


function get_edge(input::AbstractString)
  #= input should have the following fields, separated by "AND"

  relationship AND reference

  order of data in the reference field: reference title;journal name; authors (first name, last name and first name 2, last name 2); year ; type of study (t for theoretical, e for experimental, c for computational)
  =#
  aa = split(input,"AND")
  rel = strip(aa[1])
  #reference = get_reference(aa[2])
  return Edge(rel)
end


function get_node()
  concept = get_query(message="Write a concept: ")
  syn  = concept
  stem = porterStemmer(concept)
  parents = get_domain(concept)
  #reference = get_reference()
  return NodeDesc(stem,syn,parents)
end


function get_node(input::AbstractString)
  #= input should have the following fields, separated by "AND"

  concept AND parents AND reference

  parents: Write hierarchical domain of the concept $concept, separated by ','

  order of data in the reference field: reference title;journal name; authors (first name, last name and first name 2, last name 2); year ; type of study (t for theoretical, e for experimental, c for computational)
  =#
  data = split(input,"AND")
  concept = strip(data[1])
  syn  = concept
  stem = porterStemmer(concept)
  parents = [strip(i) for i in split(data[2],",")]
  #reference = get_reference(data[3])
  return NodeDesc(stem,syn,parents)
end


function get_domain(concept::ASCIIString)
  #= use WordNet to get the domain of the concept =#
  # check if concept is noun
  #domain_des = run(`wn $concept -domnn`)
  # if nothing found, then ask the user to write it

  uu = get_query(message="Write hierarchical domain of the concept $concept, separated by ','")
  dom = [strip(i) for i in split(uu,",")]
  return dom
end


function get_reference()
  rr = Array{ASCIIString}(0)
  all_ref = get_query(message="Write: reference title;journal name; authors (first name, last name and first name 2, last name 2); year ; type of study (t for theoretical, e for experimental, c for computational)",lower_case=false)
  a = split(strip(all_ref),";")

  author_list = polish_authors(a[3])
  studyType = Study(d[strip(a[5])])

  d = Dict("t" => "Theoretical", "e" => "Experimental", "c" => "Computational", "theoretical" => "Theoretical", "experimental" => "Experimental", "computational" => "Computational")

  ref = Reference(a[1],a[2],author_list,a[4],studyType)
  return ref
end


function get_reference(input::AbstractString)
  rr = Array{ASCIIString}(0)
  # order of data in the string: reference title;journal name; authors (first name, last name and first name 2, last name 2); year ; type of study (t for theoretical, e for experimental, c for computational)
  a = split(strip(input),";")

  author_list = polish_authors(a[3])
  studyType = Study(d[strip(a[5])])

  d = Dict("t" => "Theoretical", "e" => "Experimental", "c" => "Computational", "theoretical" => "Theoretical", "experimental" => "Experimental", "computational" => "Computational")

  ref = Reference(a[1],a[2],author_list,a[4],studyType)
  return ref
end


function polish_authors(authors0::AbstractString)
  authors = Array{Author}(0)
  for j in split(authors0,"and")
    if contains(j,",")
      k = split(j,",")
    else
      k = split(j)
    end
    first_name = strip(k[1])
    if length(k) > 1
      last_name = strip(k[2])
    end
    auth = Author(convert(ASCIIString,first_name),convert(ASCIIString,last_name))
    push!(authors,auth)
  end
  return authors
end


function get_query(;lower_case::Bool=true,message="") # get the user input
  if length(message)> 0
    println(message)
  end

  input = readline(STDIN)
  query = strip(input)

  if lower_case
    query = lowercase(query)
  end

  return query
end


function get_data() # collect user data
  num = get_query(message="Do you have 2 concepts or 1? [1/2] ")
  node1 = get_node()
  if num == "2"
    node2 = get_node()
    relation = get_edge()
  end
  reference = get_reference()


  println("Does it have any descriptions? (y/n) "); node_description = get_query()
  if node_description == "y" || node_description == "yes"
    println("Write the description please: "); node_1_description = get_query(lower_case=false)
  else
    node_1_description = "NA"
  end



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
