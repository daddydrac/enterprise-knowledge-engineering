"""Publish a local, gated record-review product with source evidence."""
from pathlib import Path
import sys,json,csv
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ontology_lab import *

manifest=json.loads((ROOT/'data/source_manifest.json').read_text())
assert digest(ROOT/'data/encounters.csv')==manifest['subset_sha256']
assert validate()[0]
report,derived=reasoning()
assert report['DL']['in_profile'] and report['consistent'] and not report['unsatisfiable']
expected={str(record_iri(r)) for r in rows() if r['diag_1']=='493'}
assert members(derived,EX.ReviewCandidate)==expected
out=ROOT/'reports/product';out.mkdir(exist_ok=True)
ds=dataset(derived);ds.serialize(out/'review_product.trig',format='trig')
catalog().serialize(out/'catalog.ttl',format='turtle')
evidence=[]
for row in rows():
    if str(record_iri(row)) in expected:
        evidence.append({'record_iri':str(record_iri(row)), 'encounter_id':row['encounter_id'],
            'source_code':row['diag_1'],'source_code_system':'ICD-9-CM source token',
            'conclusion':str(EX.ReviewCandidate),
            'support':['Source primary code 493','Adapter: source token 493 belongs to RespiratoryCode',
                       'Equivalent class: EncounterRecord and primaryCode some RespiratoryCode',
                       'RespiratoryCodedRecord subclassOf ReviewCandidate'],
            'proof_kind':'Auditable proof sketch, not an automatically minimal justification',
            'source_sha256':manifest['subset_sha256'],
            'ontology_version':'1.0.0','claim_scope':'Terminology-review routing of source records'})
(out/'answer_evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
with (out/'review_queue.csv').open('w',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=['encounter_id','source_code','record_iri'],extrasaction='ignore')
    writer.writeheader();writer.writerows(evidence)
release={'version':'1.0.0','review_records':len(evidence),'dl_profile':True,'consistent':True,
         'query_coverage':report['export_coverage'],'deployment':'Local artifacts only',
         'source_sha256':manifest['subset_sha256'],'bfo':json.loads((ROOT/'ontology/bfo_source.json').read_text()),
         'artifacts':{p.name:digest(p) for p in sorted(out.iterdir()) if p.name!='release_manifest.json'},
         'human_pilot':'Not yet measured; see docs/pilot_scorecard.json'}
(out/'release_manifest.json').write_text(json.dumps(release,indent=2)+'\n')
print(json.dumps({'review_records':len(evidence),'artifact_folder':str(out.relative_to(ROOT))}))
