# Enterprise Ontology Engineering — healthcare edition

© 2026 Joe Hoeller, AI Systems & Enterprise Knowledge Engineer

Start with the Primer PDF, then open E00 in notebooks/enterprise. The Workbook PDF follows the executable labs. This edition includes **25 learner notebooks and 25 separate solutions**: 15 enterprise lessons and 10 SPARQL lessons.

You will build a review workbench from 60 published Kaggle encounter records, align a small taxonomy with SKOS, import BFO, classify with OWL DL, validate with SHACL, try a bounded SWRL rule, reconcile SQL and SPARQL, and package a semantic data product. Learners will measure whether people can use the product, alongside checking whether its answers are correct.

## Setup — macOS / Linux

Install Python 3.12 and a Java 17 JDK, then run from this extracted folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --user --name ontology-lab --display-name "Ontology Lab (Python 3)"
java -version
jupyter lab
```

## Setup — Windows PowerShell

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m ipykernel install --user --name ontology-lab --display-name "Ontology Lab (Python 3)"
java -version
.venv\Scripts\jupyter.exe lab
```

Choose **Ontology Lab (Python 3)** as the notebook kernel. The core labs need no external service. Initial package installation requires internet access; source data, BFO and code references are included. If Java is not found, configure the installed JDK before launching JupyterLab. The JVM loaded by JPype cannot be restarted with a different classpath inside one kernel: restart the kernel after changing Java or reasoner versions.

## Study and verification

Each notebook has a walkthrough, an editable `answer = None` exercise, a check and a teach-back prompt. An unanswered exercise prints an incomplete message. It does not count as passed. Use the solutions after your attempt. E14 adds SWRL and can be completed before the E13 capstone.

```bash
python tools/verify_semantics.py
python tools/execute_notebooks.py
```

The normal runner uses Jupyter kernels. If the environment does not permit kernel socket transports, use the separate cell runner:

```bash
python tools/execute_cells.py
python tools/execute_cells.py --learners
```

The delivered solutions were executed in fresh IPython processes, sequentially cell by cell. TCP and IPC kernel transports are unavailable in the build environment. The reports identify the exact verification backend. Notebook cell behavior and semantic checks are verified; a Jupyter browser session, external endpoint and human pilot are not claimed as tested.

## Source and terminology boundaries

The source is Kaggle `brandao/diabetes`, version 1. The dataset's historical diagnoses use ICD-9-CM. The included ICD-10-CM and ICD-11 tables are later reference vocabularies, not reassigned source diagnoses. The requested ICD-20 label is corrected to ICD-11 for this edition. Only three source diagnosis groups are selected, with 20 rows each. This is a purposeful learning subset and is not a population estimate.

`data/source_manifest.json` contains selection details and checksums. `tools/rebuild_subset.py --download` downloads the source and reproduces the subset; `--archive PATH` uses an existing download. A changed source checksum stops the rebuild. Code-family classifications are explicit local transformations. Cross-version mapping proposals are not promoted to accepted clinical crosswalks.

## Files

| Folder | Purpose |
|---|---|
| notebooks | Editable learner notebooks |
| solutions | Completed notebooks with execution outputs |
| ontology | Full pinned BFO core, domain axioms, SKOS, SHACL and R2RML specification |
| ontology_lab | Executable Python adapter, DL bridge and optional HTTP helper |
| data | Small source subset, terminology references and provenance |
| queries | Runnable SPARQL query bank |
| docs | Gap audit, topic crosswalk, product contract and pilot plan |
| reports | Cell-execution and semantic-check evidence |
| book | Editable book Markdown and curriculum source |
| licenses | Required third-party notices |

The `requirements-lock.txt` records the verified Python environment; `requirements.txt` pins direct dependencies. `requirements-book.txt` is only needed to rebuild the PDFs.

## Rebuild the books

Edit the two files in `book/*.md`, install `requirements-book.txt`, and run `python tools/build_pdfs.py`. Install the DejaVu Serif, Sans and Sans Mono fonts first. On systems with fonts elsewhere, set `FONT_DIR` to their directory. The books use linked contents, bookmarks, chapter headings, page numbers and the chapter-specific copyright footer.

## Deployment boundary

The HermiT exporter returns named class memberships, not a complete SPARQL OWL Direct Semantics endpoint. The isolated SWRL exercise has its own supported positive rule and does not broaden the core OWL DL profile claim. The optional HTTP client is provided for a separately provisioned SPARQL endpoint. There is no automatically created cloud service, credential, production dataset or human pilot.

## License

Book text and notebooks: CC BY 4.0. Original Python utilities: MIT. Published source data, BFO, code-system content and adapted course material retain their original rights and attribution, described in `licenses/NOTICE.md`. These grants do not claim ownership of third-party clinical classifications or imply endorsement.
