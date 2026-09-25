# Rights, attribution and provenance

New book text and notebooks: © 2026 Joe Hoeller, AI Systems & Enterprise Knowledge Engineer, CC BY 4.0. New Python utilities: same copyright, MIT. Changes in this edition include healthcare data, expanded semantics, new notebooks, corrected query examples and book layouts.

The original Claude-SPARQL-tutorial-main archive is distributed under CC BY 4.0. Its supplied archive contains no named creator attribution in the README or license text. The revised topic sequence is adapted from that supplied course; the license text is preserved as CC-BY-4.0.txt. This edition does not claim the original course's authorship.

Selected teaching patterns are adapted from Peter Winstanley's SPARQL_Course (The Bookshop Trail), copyright © 2026 Peter Winstanley, MIT. The original MIT notice is preserved as PWIN-MIT.txt. The adaptations use the healthcare dataset and new queries. No original bookshop dataset, logo, browser interface, geospatial envelope data or engine binaries are redistributed. Repository: https://github.com/pwin/SPARQL_Course

The clinical data originate with John Clore, Krzysztof Cios, Jon DeShazo and Beata Strack (2014), Diabetes 130-US Hospitals for Years 1999-2008, UCI Machine Learning Repository, DOI 10.24432/C5230J, CC BY 4.0. The copy was downloaded from Kaggle brandao/diabetes version 1, maintained by Humberto Brandão. Kaggle labels its mirror CC0; this package preserves the original repository attribution and CC BY 4.0 obligations. Changes: select 60 rows and seven source columns only; original selected field values retained. Machine-readable provenance is in data/source_manifest.json.

BFO core: BFO development team, CC BY 4.0. Complete, unchanged bfo-core.owl is included from the commit recorded in ontology/bfo_source.json. The original annotations and contributor list are retained in the ontology. Repository: https://github.com/BFO-ontology/BFO-2020

ICD-10-CM: selected unchanged code labels and hierarchy links from the CDC/NCHS April 1, 2026 release. Release URL and codes are recorded in data/icd10cm_terms.csv. The course's local SKOS packaging and mappings are separate editorial material and are not an official crosswalk.

ICD-11 MMS: © World Health Organization 2025. The three code/label references are retained unchanged from the 2025-01 print release, with page locators in data/icd11_references.csv. WHO classification content is subject to CC BY-ND 3.0 IGO and its terms of use, not this book's CC BY 4.0 license. No complete WHO classification is redistributed and no modified official classification is claimed. License: https://icd.who.int/en/docs/ICD11-license.pdf

RDF, RDFS, OWL, SKOS, SHACL, SPARQL, PROV-O and DCAT terms are used by IRI. Standards text is not redistributed. Python and Java dependencies are installed separately under their respective licenses; their binaries are not included. DejaVu fonts are embedded in the PDFs; the font license accompanies the package.
