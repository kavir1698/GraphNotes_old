Improvements TODO:
    1. Possibility to edit entries (High priority).
    2. When entering new data, show suggestions based on previously added data (High priority).
    3. Add a field for sub-category, instead of the current "parent" category.
    4. Make executables for different platforms.
    5. Advanced search: search also within other fields than the "concept" field, e.g. references.
    6. Show a list of all references.
    8. A better reference input method. A new pop up window that has a set of different fields, e.g. author name, journal/book name, etc. Currently only there is a single field for the user to type in the reference (High priority).
    9. Possibility to read references from a Bibtex file; and the possibility to export references to as Bibtex file.


What each field means:
    The code makes a graph from concepts. Each concept makes a node in the graph, and relationships between the concepts makes the edges of the graph. The code either describes one "concept", or connects two "concepts". The concepts are named concept 1 and concept 2. There are fields for "synonymous" names of the concepts. searching for any synonymous name shows the same result. The "description" field, describes the concept/node. The "relation" field, is a relationship between two concepts, that makes the edge between the two nodes. Each node and each edge can have multiple descriptions. Each description is accompanied by a "reference", in the reference field. The study field specified the type of the study in the reference. The "parent" field should be replaced by a subcategory field for the "concept" field. The purpose of the subcategory is for better writing the concepts. For example, if a node/concept is light, it can have subcategories such as speed (for speed of light) and reflection (for reflection of light). This makes easier to add and retrieve information.