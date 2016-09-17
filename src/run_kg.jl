#run the KnowledgeGraph code from command line
using KnowledgeGraph
#include("KnowledgeGraph.jl")

function main()
  no_input = false
  try
    ARGS[1]
  catch LoadError
    no_input = true
    KnowledgeGraph.knowledgeGraph()
  end
  if no_input == false
    lib_file = convert(ASCIIString,ARGS[1])
    if lib_file != "--update"
      KnowledgeGraph.knowledgeGraph(lib_file)
    else
      Pkg.update()
    end
  end
end

main()
