"""Behavioral release checks: failures distinguish different semantic contracts."""
from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ontology_lab import *
from rdflib.compare import isomorphic
from rdflib.plugins.sparql.parser import parseQuery

checks=[]
def check(name,condition):
    assert condition,name
    checks.append({'name':name,'passed':True})
def extra(body):
    return Graph().parse(data='''@prefix ex: <https://example.org/health/ontology/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix bfo: <http://purl.obolibrary.org/obo/> .
'''+body,format='turtle')

manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
check('Source subset checksum',digest(ROOT/'data/encounters.csv')==manifest['subset_sha256'])
check('Source strata retained', {c:sum(r['diag_1']==c for r in rows()) for c in ['250.02','428','493']}=={'250.02':20,'428':20,'493':20})
g=build_asserted();first=record_iri(rows()[0]); patient=RES['patient/'+rows()[0]['patient_nbr']]
check('No unsupported new code assignment',all(str(o).startswith(str(CODE)) for o in g.objects(None,EX.primaryCode)))
check('Source tokens preserve punctuation',CODE['250.02'] in set(g.objects(None,EX.primaryCode)))
check('No result category manufactured for missing tests',len(list(g.triples((None,EX.a1cCategory,None))))==18)
check('Baseline SHACL',validate(g)[0])
v=vocabulary();check('Taxonomy editorial checks',skos_issues(v)==[])
check('Proposal does not assert a mapping',(CODE['493'],SKOS.closeMatch,CM.J45) not in v)
check('Accepted mapping direction',set(v.objects(CODE['493'],SKOS.broadMatch))=={LOCAL.respiratory})
bad=vocabulary();bad.add((LOCAL.clinical,SKOS.broader,LOCAL.respiratory))
check('Hierarchy cycle rejected',any(i[0]=='broader-cycle' for i in skos_issues(bad)))
bad=vocabulary();bad.add((LOCAL.respiratory,SKOS.prefLabel,Literal('Respiratory group',lang='en')))
check('Duplicate preferred label rejected',bool(skos_issues(bad)))
rep,derived=reasoning(object_probe=(first,EX.aboutPatient,patient))
check('Complete import closure includes BFO',any('bfo' in s for s in rep['imports']))
check('OWL 2 DL profile accepted',rep['DL']['in_profile'])
check('RL profile correctly rejected',not rep['RL']['in_profile'])
check('Baseline consistency and satisfiability',rep['consistent'] and not rep['unsatisfiable'])
check('Named review answers exact',members(derived,EX.ReviewCandidate)=={str(record_iri(r)) for r in rows() if r['diag_1']=='493'})
check('Union class named answers',len(members(derived,EX.CardiopulmonaryRecord))==40)
check('Property chain entailed by direct reasoner API',rep['object_probe_entailed'])
check('Type export does not claim full object-property closure',len(list(derived.triples((None,EX.aboutPatient,None))))==0)
check('Record aligned to BFO generically dependent continuant',(first,RDF.type,BFO.BFO_0000031) in derived)
missing=build_asserted();missing.remove((first,EX.documents,None)); rr,_=reasoning(source=missing)
check('Existential witness need not be named in graph',rr['consistent'] and not validate(missing)[0])
empty_class=extra('ex:Impossible a owl:Class ; rdfs:subClassOf bfo:BFO_0000002, bfo:BFO_0000003 .')
rr,_=reasoning(extra=empty_class)
check('Unsatisfiable class can leave ontology consistent',rr['consistent'] and str(EX.Impossible) in rr['unsatisfiable'])
empty_class.add((first,RDF.type,EX.Impossible));rr,_=reasoning(extra=empty_class)
check('Instance of unsatisfiable class causes inconsistency',rr['consistent'] is False)
bad_profile=extra('ex:BadChainLimit a owl:Class ; rdfs:subClassOf [ a owl:Restriction ; owl:onProperty ex:aboutPatient ; owl:maxCardinality "1"^^xsd:nonNegativeInteger ] .')
rr,_=reasoning(extra=bad_profile)
check('Cardinality on a chain superproperty rejected',rr['DL']['in_profile'] is False)
one=extra('ex:OneCode a owl:Class ; rdfs:subClassOf [ a owl:Restriction ; owl:onProperty ex:primaryCode ; owl:maxCardinality "1"^^xsd:nonNegativeInteger ] .')
one.add((first,RDF.type,EX.OneCode));one.add((first,EX.primaryCode,CODE['493']))
rr,_=reasoning(extra=one)
check('No unique-name assumption; equality can satisfy max one',rr['consistent'])
one.add((CODE['250.02'],OWL.differentFrom,CODE['493']));rr,_=reasoning(extra=one)
check('Explicit difference clashes with max one',rr['consistent'] is False)
rr,expanded=reasoning(extension=True)
check('Extension adds exactly cardiac records',members(expanded,EX.ReviewCandidate)-members(derived,EX.ReviewCandidate)=={str(record_iri(r)) for r in rows() if r['diag_1']=='428'})
removed=next(r for r in rows() if r['diag_1']=='493'); changed=build_asserted();changed.remove((record_iri(removed),EX.primaryCode,None));rr,rebuilt=reasoning(source=changed)
check('Rebuild removes unsupported conclusion',str(record_iri(removed)) not in members(rebuilt,EX.ReviewCandidate) and len(members(rebuilt,EX.ReviewCandidate))==19)
ds=dataset(derived)
check('Default graph remains empty',len(list(query(ds,'SELECT ?r WHERE { ?r a ex:EncounterRecord }')))==0)
check('Named graph evidence join',len(list(query(ds,'SELECT ?r WHERE { GRAPH <urn:graph:derived:v1> { ?r a ex:ReviewCandidate } GRAPH <urn:graph:asserted:v1> { ?r ex:encounterId ?id } }')))==20)
check('OWL list structure survives RDF round trip',isomorphic(schema(),Graph().parse(data=schema().serialize(format='turtle'),format='turtle')))
q='SELECT ?r WHERE { ?r a ex:EncounterRecord FILTER NOT EXISTS { ?r ex:a1cCategory ?a } }'
check('Missing-value query exact',len(list(query(g,q)))==42)
check('SQL and SPARQL agree at source grain',dict(sql_connection().execute('SELECT diag_1,COUNT(*) FROM encounters GROUP BY diag_1'))=={str(c).rsplit('/',1)[-1]:int(n) for c,n in query(g,'SELECT ?c (COUNT(?r) AS ?n) WHERE { ?r ex:primaryCode ?c } GROUP BY ?c')})
result={'checks':checks,'passed':len(checks),'scope':'Local RDFLib, OWLAPI/HermiT and pySHACL checks. No external endpoint or human pilot tested.'}
(ROOT/'reports/semantic_checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'passed':len(checks),'failed':0}))
