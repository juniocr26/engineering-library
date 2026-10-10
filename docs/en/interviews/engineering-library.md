# Engineering Library interview

These conceptual comparisons do not imply runtime integration. Implemented facts, general theory and hypothetical alternatives are explicitly separated.

### Q001 — Introductory: What is Engineering Library responsible for?

**Answer:** Implemented: this repository is a bilingual Markdown collection and read-only documentation tooling. Its readers should understand project mechanisms and rehearse substantive answers without opening source repositories; evidence links permit verification and deeper inspection. It has no runtime API, database, payment flow or deployed service. Its architecture is information navigation: READMEs lead to language catalogs, categories contain dossiers/interviews/verified flows, and the validator inspects permitted documents and metadata.

Follow-up: Why retain old interview answers instead of replacing them with dossiers? Answers teach reasoning and failure analysis, while dossiers explain mechanisms; both are required. Stable additional Q IDs preserve old numbering and bilingual alignment. Follow-up: What is the cost of self-contained explanations? Shared facts are repeated between project docs and library, so source review and explicit gaps must maintain consistency. Links alone would reduce duplication but fail the interview requirement. Semantic accuracy remains manual review; a successful link check cannot prove an answer is true.

### Q002 — Challenging: How does the validator prevent documentation links from becoming unsafe reads?

**Answer:** Implemented: check_docs.py scans repository READMEs and docs/en/docs/pt-BR, plus explicit safe tools JSON configuration. It classifies lexical path components before normalizing traversal, rejects outside-workspace/restricted paths and checks components with lstat to reject symlinks. Local code links receive existence checks, not code/content reads; Markdown anchors are checked only for loaded maintained documentation. Restricted environment, keys, storage, dependency and Git paths are not read. Blocked links are reported as warnings and external links are not fetched. No application execution occurs.

Follow-up: Is it a race-free sandbox? No. lstat followed by read has a TOCTOU window in a maliciously changing filesystem; the tool assumes a cooperative local workspace. A descriptor-based no-follow traversal could strengthen that at portability cost. Follow-up: Does the Markdown parser fully match GitHub? No. It handles a documented subset of inline/reference links, headings, fences and explicit IDs. Complex nested syntax needs manual review. Exit nonzero indicates errors, JSON contains structured findings, and isolated fixtures exercise failure paths. A validator can expose coverage gaps without deciding technical truth or translation quality.

### Q003 — Intermediate: How does the collection represent and validate navigation without deploying an application?

**Answer:** Implemented: Markdown paths are the public navigation contract; the validator loads permitted pages into a dictionary, extracts anchors/link targets and builds an adjacency set for each page. Breadth-first traversal from each language index checks reachability within the same repository/language rather than letting a cross-repository link substitute for its own catalog. JSON findings separate errors, warnings and informational limits. Python standard-library tooling has no service/database lifecycle; distribution is files plus Python, and publication is outside this task. Regex parsing is maintainable but deliberately incomplete for complex Markdown.

Follow-up: What is the cost? Reading/parsing grows with documentation bytes and graph traversal with vertices/edges, plus filesystem metadata checks; no performance measurements are available. Follow-up: Can structural validation detect conflicting facts or poor translations? No. It can detect IDs/counterparts and missing answers, but source-grounded content review must judge meaning. Isolated tests prove selected safety/parser/failure contracts, not race-free operation under hostile filesystem mutation or external URL reachability.
