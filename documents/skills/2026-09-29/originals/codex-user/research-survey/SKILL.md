---
name: research-survey
description: Build an evidence-traceable literature landscape for a research topic. Use when the user asks for a literature review, deep survey, state of the art, method taxonomy, controversy map, research gap, or a source-backed orientation to an unfamiliar research direction.
---

# Research Survey

Construct an evidence map, not a pile of search results. Treat paper counts and breadth targets as coverage heuristics, never as proof of completeness.

## Start with a survey contract

Before broad searching, state:

- research question and scope boundaries;
- target time window, fields, artifact types, and languages;
- inclusion and exclusion rules;
- what would count as a useful gap;
- output artifact and stopping condition.

If the user supplied authoritative sources, use them first. For current literature or claims that may have changed, search live sources. Prefer papers, official repositories, benchmark pages, and author materials over secondary summaries.

## Build the landscape

1. Inspect any local knowledge base or source list and deduplicate known work.
2. Split the topic into 3-7 question-shaped subdirections. Avoid arbitrary keyword buckets.
3. Search across the dimensions that matter for the question:
   - foundations and problem formulation;
   - method families and their lineage;
   - empirical results and evaluation protocols;
   - failures, negative evidence, and criticism;
   - adjacent-field mechanisms that might transfer;
   - current frontier and competing approaches;
   - datasets, code, benchmarks, and infrastructure.
4. Record candidate sources before synthesizing. For each important source, retain title, year, stable URL or identifier, source type, relevance, and access date.
5. Verify important claims in the full paper, tables, appendix, or code. Search snippets and abstracts are discovery evidence only.
6. Stop when new searches mostly repeat known method families and no unresolved high-priority gap remains, or when the agreed budget is exhausted.

## Separate evidence from interpretation

Use these labels in notes and conclusions:

- `Source states`: directly supported by the cited artifact.
- `Observed`: reproduced or inspected in the current task.
- `Synthesis`: a cross-source interpretation.
- `Hypothesis`: plausible but not yet tested.
- `Unknown`: material evidence is missing or inaccessible.

Do not turn the absence of found evidence into evidence of absence. Do not report a benchmark winner without aligning version, split, metric, budget, and evaluation protocol.

## Deliverables

Produce:

1. scope and search protocol;
2. source ledger;
3. method-family map with representative papers;
4. evidence matrix: claim, supporting source, counterevidence, confidence, scope;
5. disputes and evaluation mismatches;
6. research gaps ranked by importance, tractability, and falsifiability;
7. decisive next checks and explicit stopping condition.

For a student exercise, prefer 6-12 well-chosen papers spanning foundations, different routes, frontier work, and failure evidence over a nominal target of 100 papers.

## Lineage

Adapted from Dr. Pie 1.2.2 `deep-survey`. Removed automatic ingestion, fixed paper quotas, Dr. Pie-specific tools, and prompt-only queue semantics.
