# Gap review and revision record

## Scope

Reviewed the two supplied enterprise PDFs, the enterprise lab files, the original 19-chapter SPARQL archive and the additional SPARQL_Course archive. The enterprise PDFs originally had 57 and 22 pages. The original SPARQL archive had only two notebooks of four code cells each. The additional course provides 145 numbered query exercises, a feature catalog and profile-checking material; its claimed cross-engine results are not adopted as this package's verification results.

## Core enterprise gaps and changes

| Gap | Revision | Acceptance evidence |
|---|---|---|
| Data examples lacked the requested published clinical provenance | Actual Kaggle rows, deterministic subset and source/term release manifests | Subset reproduction matches checksum |
| Vocabulary coverage did not provide a full mapping workflow | SKOS direction, scope, proposals, acceptance and regression | Pending link is absent from accepted mapping triples |
| BFO bridge was mainly a proposal | Complete pinned BFO core, local import resolution and actual bridge axioms | Full closure DL check and consistency test |
| Upper/lower terminology could conflate levels with logical bounds | Separate architectural layers, sufficient/necessary bounds and answer approximations | 20 lower / 20 baseline target / 60 named upper records |
| Labs were mostly CLI and editable files | 25 sequential learner notebooks and separate solutions | Cell execution reports with backend disclosed |
| Rule-language choice was not taught | Isolated SWRL positive join, comparison table and limits | 20 inferred record/person pairs match source |
| Product monitoring emphasized technical behavior | Product contract and pilot measures for correctness and actual use | Pilot template remains explicitly unmeasured |
| Page furniture was not book-like | Rebuilt typography, contents, bookmarks and current-chapter footer | PDF structural and visual review |

## Original SPARQL archive corrections

The original src/12.md described subclass property paths as RDFS inferencing without a configured entailment contract. The revision distinguishes graph reachability, RDFS closure and OWL DL classification. The original src/14.md uses a language suffix on a variable in federation examples, which is not valid SPARQL syntax, and omits needed prefixes in some examples. The revision uses explicit language filtering and keeps remote federation outside the offline execution gate.

The original src/15.md teaches LET syntax and lists IFNULL alongside portable functions. The revision uses BIND and COALESCE and explains expression errors and unbound values. The original helper creates a dataset during initialization, defaults to administrator credentials, lacks explicit HTTP timeouts, mixes response forms, and calls a default-graph deletion a dataset clear. The replacement separates operations, uses configured credentials, raises errors and scopes updates explicitly.

The original Docker path includes a missing Neo4j environment-file mount and a large ML notebook image unrelated to the course requirements. The revised core uses a tested local Python/Java environment. Endpoint provisioning is optional and separate; no replacement container deployment is claimed as tested.

Some original fenced blocks contain multiple comparison queries or query-plus-update examples. Parser rejection of the entire fence is not automatically a defect in each individual query. The audit distinguishes these packaging cases from the concrete syntax errors above.

## Relevant additions from the additional SPARQL course

| Upstream exercise area | Adaptation in this edition |
|---|---|
| q17 and q19: negation and optional filters | S02 paired queries on missing A1C categories |
| q25 and q92: counting and join multiplication | S03 bound-value counts and duplicate joins |
| Path, named-graph and update modules | S04–S05 explicit graph scope and reversible updates |
| Blank nodes and structural inspection | S07 RDF list traversal and graph isomorphism |
| q140–q145: inference and debugging | S06 finite entailment contract plus semantic failure tests |
| Feature catalog and engine comparisons | Revised 19-topic crosswalk and an explicit portability boundary |

Two inference overstatements are corrected rather than repeated: anonymous class expressions can be queried structurally as RDF nodes; and OWL reasoning can detect inconsistency, even though it does not replace graph-delivery validation. The source course's rule-closure examples do not establish complete OWL DL reasoning. Its RDF/SPARQL 1.2 and geospatial features remain extension-study topics because this clinical subset has no coordinates and the executed core targets SPARQL 1.1.

## Explicit limits

The core DL export covers named class membership, not arbitrary DL conjunctive queries. The R2RML file is a mapping specification; Python executes the adapter. External SPARQL services, multi-engine benchmarks, browser UI and a human adoption pilot are not verified. The requested model selection is controlled by the chat runtime; this work does not claim to have switched the active model.
