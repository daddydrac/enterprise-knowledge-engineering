from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from ontology_lab import *
from rdflib.plugins.sparql.parser import parseQuery
queries=[
('01_source_records','asserted','SELECT ?id ?code WHERE { ?r ex:encounterId ?id; ex:primaryCode ?code } ORDER BY ?id',60),
('02_record_count','asserted','SELECT (COUNT(?r) AS ?n) WHERE { ?r a ex:EncounterRecord }',1),
('03_respiratory_records','asserted','SELECT ?id WHERE { ?r ex:encounterId ?id; ex:primaryCode <https://example.org/health/icd9-source/493> } ORDER BY ?id',20),
('04_optional_a1c','asserted','SELECT ?r ?a WHERE { ?r a ex:EncounterRecord OPTIONAL { ?r ex:a1cCategory ?a } }',60),
('05_missing_a1c','asserted','SELECT ?r WHERE { ?r a ex:EncounterRecord FILTER NOT EXISTS { ?r ex:a1cCategory ?a } }',42),
('06_minus_shared','asserted','SELECT ?r WHERE { ?r a ex:EncounterRecord MINUS { ?r ex:a1cCategory ?a } }',42),
('07_minus_unshared','asserted','SELECT ?r WHERE { ?r a ex:EncounterRecord MINUS { ?other ex:a1cCategory ?a } }',60),
('08_filter_inside_optional','asserted','SELECT ?r ?a WHERE { ?r a ex:EncounterRecord OPTIONAL { ?r ex:a1cCategory ?a FILTER(?a = ">8") } }',60),
('09_filter_outside_optional','asserted','SELECT ?r ?a WHERE { ?r a ex:EncounterRecord OPTIONAL { ?r ex:a1cCategory ?a } FILTER(?a = ">8") }',13),
('10_count_bound','asserted','SELECT (COUNT(*) AS ?records) (COUNT(?a) AS ?available) WHERE { ?r a ex:EncounterRecord OPTIONAL { ?r ex:a1cCategory ?a } }',1),
('11_group_counts','asserted','SELECT ?c (COUNT(DISTINCT ?r) AS ?n) WHERE { ?r ex:primaryCode ?c } GROUP BY ?c HAVING(COUNT(?r) >= 20) ORDER BY ?c',3),
('12_bind_and_values','asserted','SELECT ?id ?band WHERE { ?r ex:encounterId ?id; ex:primaryCode ?c; ex:stayDays ?d VALUES ?c { <https://example.org/health/icd9-source/493> } BIND(IF(?d >= 7,"longer","shorter") AS ?band) }',20),
('13_coalesce','asserted','SELECT ?r (COALESCE(?a,"not recorded") AS ?display) WHERE { ?r a ex:EncounterRecord OPTIONAL { ?r ex:a1cCategory ?a } }',60),
('14_path_plus','vocabulary','SELECT ?x WHERE { <https://example.org/health/reporting/respiratory> skos:broader+ ?x }',1),
('15_path_star','vocabulary','SELECT ?x WHERE { <https://example.org/health/reporting/respiratory> skos:broader* ?x }',2),
('16_accepted_mappings','vocabulary','SELECT ?source ?target WHERE { ?source skos:broadMatch ?target } ORDER BY ?source',3),
('17_unapproved_mapping','vocabulary','SELECT ?x WHERE { <https://example.org/health/icd9-source/493> skos:closeMatch ?x }',0),
('18_english_labels','vocabulary','SELECT ?c ?label WHERE { ?c skos:prefLabel ?label FILTER(LANGMATCHES(LANG(?label),"en")) } ORDER BY ?c',17),
('19_review_evidence','dataset','SELECT ?id ?code WHERE { GRAPH <urn:graph:derived:v1> { ?r a ex:ReviewCandidate } GRAPH <urn:graph:asserted:v1> { ?r ex:encounterId ?id; ex:primaryCode ?code } } ORDER BY ?id',20),
('20_empty_default','dataset','SELECT ?r WHERE { ?r a ex:EncounterRecord }',0),
('21_union_members','schema','PREFIX owl: <http://www.w3.org/2002/07/owl#> SELECT ?member WHERE { ex:CardiopulmonaryRecord owl:equivalentClass/owl:unionOf/rdf:rest*/rdf:first ?member }',2),
('22_asserted_path_limit','asserted_schema','SELECT ?r WHERE { ?r rdf:type/rdfs:subClassOf* ex:ReviewCandidate }',0),
('23_subquery','asserted','SELECT ?code ?n WHERE { { SELECT ?code (COUNT(?r) AS ?n) WHERE { ?r ex:primaryCode ?code } GROUP BY ?code } FILTER(?n = 20) }',3),
('24_construct_evidence','asserted','CONSTRUCT { ?r ex:encounterId ?id } WHERE { ?r ex:encounterId ?id }',60),
('25_ask_records','asserted','ASK { ?r a ex:EncounterRecord }',True),
('26_union','asserted','SELECT DISTINCT ?r WHERE { { ?r ex:primaryCode <https://example.org/health/icd9-source/493> } UNION { ?r ex:primaryCode <https://example.org/health/icd9-source/428> } }',40),
]
report,derived=reasoning();graphs={'asserted':build_asserted(),'vocabulary':vocabulary(),'schema':schema(),'asserted_schema':build_asserted()+schema(),'dataset':dataset(derived)}
results=[]
for name,scope,q,expected in queries:
    text=PREFIX+q;parseQuery(text);result=graphs[scope].query(text)
    actual=bool(result) if result.type=='ASK' else len(result.graph) if result.type in {'CONSTRUCT','DESCRIBE'} else len(list(result))
    assert actual==expected,(name,actual,expected)
    (ROOT/'queries'/(name+'.rq')).write_text(f'# Dataset view: {scope}\n# Expected {"boolean" if result.type=="ASK" else "rows or triples"}: {expected}\n'+text+'\n')
    results.append({'query':name+'.rq','scope':scope,'form':result.type,'expected':expected,'actual':actual,'passed':True})
(ROOT/'reports/query_checks.json').write_text(json.dumps({'engine':'RDFLib 7.6.0','results':results},indent=2)+'\n')
(ROOT/'queries/README.md').write_text('''# Query bank

Each file states the dataset view and expected answer size. The offline release check executes every query with RDFLib. `asserted` is the adapter output, `vocabulary` is the SKOS graph, `schema` is the domain axioms, and `dataset` has explicit named graphs plus the selected DL membership export. Use the matching graph; loading a different view changes the question.

Query 18 includes preferred labels of schemes as well as concepts. The code verifies the exact selected vocabulary size. Query 22 demonstrates a deliberate limitation: a subclass path does not classify restriction-defined records. Query 25 returns a boolean; query 24 returns a graph. Do not treat those result types as SELECT bindings.
''')
print('Executed',len(results),'query files')
