"""Execute notebook cells in a fresh IPython process without socket transport.

This is a reproducible fallback for build environments that cannot launch a
Jupyter kernel. It checks cell behavior, not the notebook web interface.
"""
from pathlib import Path
import argparse,json,subprocess,sys,time
import nbformat
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--one',type=Path);p.add_argument('--learners',action='store_true');a=p.parse_args()
if a.one:
    path=a.one.resolve(); nb=nbformat.read(path,as_version=4)
    shell=InteractiveShell.instance(); index=0
    for cell in nb.cells:
        if cell.cell_type!='code':continue
        index+=1
        with capture_output() as captured:
            result=shell.run_cell(cell.source,store_history=False)
        outputs=[]
        if captured.stdout:outputs.append(nbformat.v4.new_output('stream',name='stdout',text=captured.stdout))
        if captured.stderr:outputs.append(nbformat.v4.new_output('stream',name='stderr',text=captured.stderr))
        for output in captured.outputs:
            outputs.append(nbformat.v4.new_output('display_data',data=output.data,metadata=output.metadata))
        cell.outputs=outputs;cell.execution_count=index
        error=result.error_before_exec or result.error_in_exec
        if error:raise RuntimeError(f'{path.name}: code cell {index}: {error}') from error
        if 'check' in cell.metadata.get('tags',[]) and not a.learners:
            assert 'Exercise passed.' in captured.stdout,f'{path.name}: exercise incomplete'
    nb.metadata['verification']={'backend':'Fresh IPython process, sequential cells','jupyter_ui_tested':False}
    nbformat.write(nb,path)
    print(json.dumps({'notebook':str(path.relative_to(ROOT)),'passed':True,'code_cells':index}))
else:
    directory=ROOT/('notebooks' if a.learners else 'solutions'); results=[]
    for path in sorted(directory.glob('**/*.ipynb')):
        start=time.perf_counter();args=[sys.executable,__file__,'--one',str(path)]
        if a.learners:args.append('--learners')
        completed=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,timeout=240)
        if completed.returncode==0:
            item=json.loads(completed.stdout.strip().splitlines()[-1])
        else:item={'notebook':str(path.relative_to(ROOT)),'passed':False,'error':completed.stderr[-2400:]}
        item['seconds']=round(time.perf_counter()-start,2);results.append(item);print(json.dumps(item),flush=True)
    report={'python':sys.version,'backend':'Fresh IPython process per notebook, sequential cell execution','scope':'Executable cell behavior verified. Jupyter TCP and IPC transports are unavailable in the build environment; browser UI and external endpoints not tested.','results':results}
    (ROOT/'reports'/('learner_execution.json' if a.learners else 'notebook_execution.json')).write_text(json.dumps(report,indent=2)+'\n')
    sys.exit(0 if all(x['passed'] for x in results) else 1)
