# Query bank

Each file states the dataset view and expected answer size. The offline release check executes every query with RDFLib. `asserted` is the adapter output, `vocabulary` is the SKOS graph, `schema` is the domain axioms, and `dataset` has explicit named graphs plus the selected DL membership export. Use the matching graph; loading a different view changes the question.

Query 18 includes preferred labels of schemes as well as concepts. The code verifies the exact selected vocabulary size. Query 22 demonstrates a deliberate limitation: a subclass path does not classify restriction-defined records. Query 25 returns a boolean; query 24 returns a graph. Do not treat those result types as SELECT bindings.
