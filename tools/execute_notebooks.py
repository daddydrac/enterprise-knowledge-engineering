"""Execute solution notebooks from fresh kernels and keep an honest test report."""
from pathlib import Path
import argparse,json,sys,time
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('--track',choices=['enterprise','sparql','all'],default='all')
parser.add_argument('--learners',action='store_true')
parser.add_argument('--transport',choices=['tcp','ipc'],default='tcp')
args=parser.parse_args()
base=ROOT/('notebooks' if args.learners else 'solutions')
results=[]
for path in sorted(base.glob('**/*.ipynb')):
    if args.track!='all' and path.parent.name!=args.track:continue
    start=time.perf_counter(); nb=nbformat.read(path,as_version=4)
    try:
        km=KernelManager(kernel_name='ontology-lab',transport=args.transport)
        try:
            NotebookClient(nb,km=km,timeout=180,kernel_name='ontology-lab',resources={'metadata':{'path':str(ROOT)}}).execute()
        finally:
            if km.has_kernel:km.shutdown_kernel(now=True)
        if not args.learners:
            for cell in nb.cells:
                if 'check' in cell.metadata.get('tags',[]):
                    streams=''.join(o.get('text','') for o in cell.get('outputs',[]) if o.output_type=='stream')
                    assert 'Exercise passed.' in streams,'Solution exercise did not pass.'
        nbformat.write(nb,path)
        item={'notebook':str(path.relative_to(ROOT)),'passed':True,
              'code_cells':sum(c.cell_type=='code' for c in nb.cells),
              'seconds':round(time.perf_counter()-start,2)}
    except Exception as exc:
        item={'notebook':str(path.relative_to(ROOT)),'passed':False,'error':str(exc)[-2500:]}
    results.append(item);print(json.dumps(item),flush=True)
out=ROOT/'reports'/('learner_execution.json' if args.learners else 'notebook_execution.json')
out.write_text(json.dumps({'python':sys.version,'track':args.track,'transport':args.transport,'results':results},indent=2)+'\n')
sys.exit(0 if all(x['passed'] for x in results) else 1)
