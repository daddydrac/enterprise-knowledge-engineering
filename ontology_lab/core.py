from __future__ import annotations
import csv
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path
from urllib.parse import quote
from rdflib import Graph, Dataset, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL, XSD, SKOS, DCTERMS

ROOT = Path(__file__).resolve().parents[1]
EX = Namespace('https://example.org/health/ontology/')
RES = Namespace('https://example.org/health/resource/')
CODE = Namespace('https://example.org/health/icd9-source/')
LOCAL = Namespace('https://example.org/health/reporting/')
CM = Namespace('https://example.org/health/icd10cm/2026-04/')
PROV = Namespace('http://www.w3.org/ns/prov#')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
BFO = Namespace('http://purl.obolibrary.org/obo/')
ASSERTED = URIRef('urn:graph:asserted:v1')
VOCAB = URIRef('urn:graph:vocabulary:v1')
DERIVED = URIRef('urn:graph:derived:v1')
META = URIRef('urn:graph:metadata:v1')
PREFIX = f'PREFIX ex: <{EX}> PREFIX skos: <{SKOS}> PREFIX rdf: <{RDF}> PREFIX rdfs: <{RDFS}>\n'

def rows():
    with (ROOT/'data/encounters.csv').open(newline='', encoding='utf-8') as stream:
        return list(csv.DictReader(stream))

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def fresh_graph():
    g = Graph()
    for p,n in [('ex',EX),('res',RES),('code',CODE),('skos',SKOS),('bfo',BFO)]:
        g.bind(p,n)
    return g

def record_iri(row):
    return RES['record/'+quote(row['encounter_id'],safe='')]

def build_asserted(source_rows=None):
    """Map original values; local code-family types are declared derivations."""
    g = fresh_graph()
    families = {'250.02':EX.EndocrineCode,'428':EX.CardiacCode,'493':EX.RespiratoryCode}
    for row in rows() if source_rows is None else source_rows:
        record = record_iri(row)
        encounter = RES['encounter/'+row['encounter_id']]
        patient = RES['patient/'+row['patient_nbr']]
        code = CODE[row['diag_1']]
        for entity, cls in [(record,EX.EncounterRecord),(encounter,EX.HospitalEncounter),
                            (patient,EX.Patient),(code,families[row['diag_1']])]:
            g.add((entity,RDF.type,cls))
            g.add((entity,RDF.type,OWL.NamedIndividual))
        g.add((record,EX.encounterId,Literal(row['encounter_id'])))
        g.add((record,EX.documents,encounter))
        g.add((encounter,EX.hasPatient,patient))
        g.add((record,EX.primaryCode,code))
        g.add((record,EX.stayDays,Literal(int(row['time_in_hospital']),datatype=XSD.integer)))
        g.add((record,EX.labProcedureCount,Literal(int(row['num_lab_procedures']),datatype=XSD.integer)))
        g.add((record,EX.readmissionCategory,Literal(row['readmitted'])))
        # The source token 'None' means no HbA1c test in its data dictionary.
        # Preserve it in CSV and omit a result value in RDF; never turn it into zero.
        if row['A1Cresult'] != 'None':
            g.add((record,EX.a1cCategory,Literal(row['A1Cresult'])))
    return g

def schema(extension=False):
    g = fresh_graph().parse(ROOT/'ontology/clinical-core.ttl')
    if extension:
        g.parse(ROOT/'ontology/cardiac-extension.ttl')
    return g

def vocabulary():
    return fresh_graph().parse(ROOT/'ontology/taxonomies.ttl')

def dataset(inferred=None):
    ds = Dataset(default_union=False)
    for ident, graph in [(ASSERTED,build_asserted()),(VOCAB,vocabulary()),(META,catalog())]:
        for triple in graph:
            ds.graph(ident).add(triple)
    if inferred is not None:
        for triple in inferred:
            ds.graph(DERIVED).add(triple)
    return ds

def query(g, text, **kwargs):
    return g.query(PREFIX+text, **kwargs)

def sql_connection():
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE encounters (encounter_id TEXT PRIMARY KEY, patient_nbr TEXT, diag_1 TEXT, time_in_hospital INTEGER, num_lab_procedures INTEGER, A1Cresult TEXT, readmitted TEXT)')
    db.executemany('INSERT INTO encounters VALUES (?,?,?,?,?,?,?)',
                  [tuple(r[c] for c in ['encounter_id','patient_nbr','diag_1','time_in_hospital','num_lab_procedures','A1Cresult','readmitted']) for r in rows()])
    return db

def validate(g=None):
    from pyshacl import validate as check
    return check(build_asserted() if g is None else g,
                 shacl_graph=str(ROOT/'ontology/shapes.ttl'),
                 inference='none', abort_on_first=False)

def skos_issues(g):
    """Project acceptance checks; broader cycles are a local rule, not a SKOS axiom."""
    issues=[]
    for s in set(g.subjects(RDF.type,SKOS.Concept)):
        langs={}
        for label in g.objects(s,SKOS.prefLabel):
            lang=label.language or ''
            langs[lang]=langs.get(lang,0)+1
        if any(n>1 for n in langs.values()):issues.append(('preferred-label',str(s)))
        if set(g.objects(s,SKOS.prefLabel)) & set(g.objects(s,SKOS.altLabel)):
            issues.append(('overlapping-label',str(s)))
        frontier=list(g.objects(s,SKOS.broader)); seen=set()
        while frontier:
            x=frontier.pop()
            if x==s:issues.append(('broader-cycle',str(s)));break
            if x not in seen:seen.add(x);frontier.extend(g.objects(x,SKOS.broader))
    return sorted(issues)

def catalog():
    g=Graph()
    product=RES['product/encounter-code-review']
    dist=RES['distribution/encounters-v1']
    g.add((product,RDF.type,DCAT.Dataset))
    g.add((product,DCTERMS.title,Literal('Encounter code review learning product',lang='en')))
    g.add((product,DCTERMS.license,URIRef('https://creativecommons.org/licenses/by/4.0/')))
    g.add((product,DCTERMS.source,URIRef('https://www.kaggle.com/datasets/brandao/diabetes')))
    g.add((product,DCAT.version,Literal('1.0.0')))
    g.add((product,DCAT.distribution,dist))
    g.add((dist,RDF.type,DCAT.Distribution))
    g.add((dist,DCTERMS.format,Literal('text/csv')))
    g.add((dist,DCAT.downloadURL,URIRef('urn:artifact:data:encounters.csv')))
    g.add((dist,EX.sha256,Literal(digest(ROOT/'data/encounters.csv'))))
    g.add((product,PROV.wasDerivedFrom,URIRef('https://doi.org/10.24432/C5230J')))
    return g

def reasoning(source=None, extension=False, extra=None, object_probe=None):
    """Run OWLAPI profile checks and HermiT; return selected named type entailments.

    Includes the complete pinned BFO core through a local import mapper. Export
    coverage is named individuals x named classes only, not arbitrary DL queries.
    """
    import jpype, owlready2
    jar=Path(owlready2.__file__).parent/'hermit/HermiT.jar'
    if not jpype.isJVMStarted():jpype.startJVM(classpath=[str(jar)],convertStrings=True)
    J=jpype.JClass
    manager=J('org.semanticweb.owlapi.apibinding.OWLManager').createOWLOntologyManager()
    iri=J('org.semanticweb.owlapi.model.IRI')
    mapper=J('org.semanticweb.owlapi.util.SimpleIRIMapper')(
        iri.create('http://purl.obolibrary.org/obo/bfo.owl'),
        iri.create((ROOT/'ontology/bfo-core.owl').as_uri()))
    manager.addIRIMapper(mapper)
    g=schema(extension)+ (build_asserted() if source is None else source)
    if extra is not None:g+=extra
    with tempfile.TemporaryDirectory() as temp:
        path=Path(temp)/'logical-input.owl';g.serialize(path,format='xml')
        onto=manager.loadOntologyFromOntologyDocument(J('java.io.File')(str(path)))
        report={'engine':'HermiT via Owlready2 0.51 / OWLAPI',
                'scope':'Complete pinned BFO core + clinical schema + supplied ABox',
                'imports':sorted(str(x.getOntologyID()) for x in onto.getImportsClosure()),
                'export_coverage':'Named class memberships of named individuals only'}
        for profile in ['RL','DL']:
            check=J('org.semanticweb.owlapi.profiles.OWL2'+profile+'Profile')().checkOntology(onto)
            report[profile]={'in_profile':bool(check.isInProfile()),'violations':[str(x) for x in check.getViolations()]}
        derived=Graph()
        if not report['DL']['in_profile']:
            report.update(consistent=None,unsatisfiable=[]);return report,derived
        reasoner=J('org.semanticweb.HermiT.Reasoner$ReasonerFactory')().createReasoner(onto)
        try:
            report['consistent']=bool(reasoner.isConsistent())
            report['unsatisfiable']=[]
            if report['consistent']:
                report['unsatisfiable']=sorted(str(c.getIRI()) for c in reasoner.getUnsatisfiableClasses().getEntitiesMinusBottom())
                if object_probe is not None:
                    s,p,o=object_probe
                    factory=manager.getOWLDataFactory()
                    axiom=factory.getOWLObjectPropertyAssertionAxiom(
                        factory.getOWLObjectProperty(iri.create(str(p))),
                        factory.getOWLNamedIndividual(iri.create(str(s))),
                        factory.getOWLNamedIndividual(iri.create(str(o))))
                    report['object_probe_entailed']=bool(reasoner.isEntailed(axiom))
                for individual in onto.getIndividualsInSignature():
                    for cls in reasoner.getTypes(individual,False).getFlattened():
                        triple=(URIRef(str(individual.getIRI())),RDF.type,URIRef(str(cls.getIRI())))
                        if triple not in g:derived.add(triple)
            return report,derived
        finally:reasoner.dispose()

def members(g, cls):
    return {str(x) for x in g.subjects(RDF.type,cls)}

def learner_check(answer, predicate, hint):
    if answer is None:
        print('Exercise not completed. '+hint)
        return False
    assert predicate(answer),hint
    print('Exercise passed.')
    return True
