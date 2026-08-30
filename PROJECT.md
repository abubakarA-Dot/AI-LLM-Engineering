# RAG Assistant for Doroob Workforce-Development Programs

Doroob hosts multiple government workforce-development programs (Tamheer, TVTC, Hafiz, the
English Program, employer-facing services) across separate pages and PDFs, making it hard for
a job seeker or employer to quickly find which program applies to their situation or what its
exact eligibility/process requirements are. This project builds a retrieval-augmented Q&A
system over Doroob's publicly published program documentation, so a user can ask a
plain-language question ("Am I eligible for Tamheer if I'm a fresh graduate with a diploma?")
and get a grounded answer with a citation back to the source page, instead of manually
cross-referencing multiple program pages. The system is built as a Django-integrated API,
evaluated against a hand-built golden dataset rather than judged by "it looks right," and
designed to be honest about what it doesn't know.

## Data source note

All content in `data/` is copied from **publicly published** Doroob/HRDF pages and guides only
-- nothing from internal/admin-only systems. See the corpus README for sourcing details.
