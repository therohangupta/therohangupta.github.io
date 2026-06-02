# Resume Retrieval: Chunk Evidence to Candidate Ranking

Interview prompt:

> You have 2 million resumes. They are all structured differently. How would you store them and retrieve the most relevant resumes for a job query?

The important design point is that the searchable unit and the returned unit are different.

```text
resume document
  -> many searchable evidence chunks
  -> chunk retrieval
  -> group by resume_id
  -> candidate-level ranking
  -> return resumes / candidates
```

You should not assume every resume has clean fields. Some will have clear sections. Some will be PDFs with weird line breaks. Some will have tables, columns, headers, footers, OCR noise, or unconventional layouts.

## Storage Model

Store two layers.

### Resume Record

One row/object per resume:

```text
resume_id
raw_file_uri
parsed_text_uri
candidate_id if known
source
ingestion_timestamp
parser_version
permission / tenant metadata
optional extracted fields with confidence
```

The optional extracted fields may include skills, location, education, employers, seniority, or years of experience. Treat them as helpful signals, not ground truth.

### Chunk / Evidence Record

Many rows per resume:

```text
chunk_id
resume_id
chunk_text
embedding
section_hint if available
source_offsets
parser_version
embedding_model_version
quality_flags
metadata / ACLs
```

The `resume_id` link is critical. Retrieval may find chunks, but the product usually returns candidates.

## Variant A: Semi-Reliable Structure

Use this when resumes often have recognizable section labels such as `Experience`, `Education`, `Skills`, `Projects`, or `Certifications`, but not always consistently.

Ingestion:

1. Parse the raw file into text.
2. Detect likely section headers using rules and/or a classifier.
3. Create section-aware chunks.
4. Preserve parent resume and source offsets.
5. Store extracted fields with confidence scores.

Example chunks:

```text
resume_id=123
section_hint=skills
text="Python, PyTorch, Kafka, Spark, AWS..."

resume_id=123
section_hint=experience
text="Built distributed retrieval pipelines over 50M documents..."

resume_id=123
section_hint=education
text="M.S. Computer Science..."
```

Query-time:

1. Parse the job description into semantic query text plus optional filters.
2. Use filters for hard constraints only when reliable.
3. Run hybrid retrieval over chunks: dense for semantic fit, sparse for exact skills.
4. Retrieve more chunks than final candidates.
5. Group by `resume_id`.
6. Aggregate evidence across chunks.
7. Rerank top resumes against the job description.

Candidate score can combine:

```text
best matching chunk score
+ multiple matching sections
+ exact skill overlap
+ recency of relevant experience
+ section confidence
- weak evidence / parser noise
```

Do not simply return the resume with the single highest chunk if another resume has several strong pieces of evidence across experience, skills, and projects.

## Variant B: No Reliable Structure

Use this when section detection is unreliable enough that depending on it would break recall.

Ingestion:

1. Parse raw document text as well as possible.
2. Clean obvious OCR/control characters, but preserve enough text order for evidence.
3. Create overlapping token windows.
4. Optionally create multiple granularities: small windows and larger parent windows.
5. Attach `resume_id`, offsets, parser quality flags, and embedding versions.

Example:

```text
resume_id=456
chunk_001: tokens 0-250
chunk_002: tokens 200-450
chunk_003: tokens 400-650
...
```

This avoids betting on section labels. It is less elegant, but more robust.

Query-time:

1. Run dense retrieval over windows for semantic fit.
2. Run sparse retrieval for exact skills, company names, tools, credentials, and acronyms.
3. Merge candidates with rank fusion.
4. Group matching chunks by `resume_id`.
5. Pull neighboring windows around high-scoring chunks for context.
6. Rerank candidate resumes using the job description plus selected evidence snippets.

The key move is evidence aggregation:

```text
chunk hits:
  resume 456: chunk 3, chunk 4, chunk 9
  resume 981: chunk 2

candidate ranking:
  score resume-level evidence, not isolated chunks
```

This handles unstructured resumes because the final candidate score depends on the set of evidence recovered from the document, not on a perfect parse.

## Hard Filters vs Soft Signals

Be careful with structured fields.

Use as hard filters only when reliable:

* tenant or permission metadata,
* explicit candidate availability if trusted,
* location if normalized from a reliable source,
* required certification if extracted with high confidence.

Use as soft ranking signals when uncertain:

* years of experience,
* seniority,
* skill extraction,
* school or degree,
* section labels,
* inferred job titles.

If structured extraction is noisy, hard filtering can incorrectly remove good candidates. Prefer broad retrieval first, then rerank with evidence.

## Scaling Notes

Two million resumes may become tens of millions of chunks.

Scaling choices:

* use hybrid retrieval because resumes contain both semantic descriptions and exact terms,
* shard by tenant, region, or hash depending on access patterns,
* cache common job-description queries or embeddings,
* batch embedding jobs during ingestion,
* store raw files separately from parsed text and chunk metadata,
* track parser and embedding versions for reprocessing,
* monitor chunk explosion per resume so weird PDFs do not create thousands of bad chunks.

## Strong Interview Answer

Say:

> I would not rely on resumes having consistent structure. I would store the raw resume, a parsed text representation, optional extracted fields with confidence, and many searchable chunks linked by `resume_id`. If section structure is semi-reliable, I would use section-aware chunks. If structure is unreliable, I would use overlapping windows and maybe multi-granularity chunks. Retrieval happens at chunk level, but ranking and output happen at resume level: retrieve chunks, group by `resume_id`, aggregate evidence, rerank candidates against the job description, and return resumes with supporting snippets.

That answer shows the interviewer you understand both retrieval quality and production robustness.
