"""Recreate the included subset from the pinned Kaggle source CSV."""
from pathlib import Path
import argparse,csv,hashlib,io,json,urllib.request,zipfile
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--archive',type=Path);p.add_argument('--download',action='store_true');a=p.parse_args()
m=json.loads((ROOT/'data/source_manifest.json').read_text())
if a.download:
    request=urllib.request.Request(m['download_url'],headers={'User-Agent':'EnterpriseOntologyCourse/1.0'})
    with urllib.request.urlopen(request,timeout=60) as response:payload=response.read(32*1024*1024)
elif a.archive:payload=a.archive.read_bytes()
else:p.error('Supply --archive PATH or --download. The included subset already works offline.')
with zipfile.ZipFile(io.BytesIO(payload)) as z:raw=z.read('diabetic_data.csv')
if hashlib.sha256(raw).hexdigest()!=m['source_csv_sha256']:
    raise SystemExit('Source CSV differs from the reviewed version. Review the new source before rebuilding.')
source=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
chosen=[]
for code in ['250.02','428','493']:
    chosen.extend(sorted((r for r in source if r['diag_1']==code),key=lambda r:int(r['encounter_id']))[:20])
buffer=io.StringIO(newline='');w=csv.DictWriter(buffer,fieldnames=m['source_columns'],extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(chosen)
result=buffer.getvalue().encode()
if hashlib.sha256(result).hexdigest()!=m['subset_sha256']:raise SystemExit('Subset reproduction failed.')
out=ROOT/'reports/rebuilt_encounters.csv';out.write_bytes(result)
print(f'Reproduced {len(chosen)} source rows at {out.name}; checksum matches.')
