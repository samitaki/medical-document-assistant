# Architecture

## The flow

```
pdf upload
  -> pymupdf extracts tables and prose per page, each piece keeps filename, page, kind
  -> tables pass through whole, prose is split at 800 chars with 120 overlap
  -> fastembed (bge-small-en-v1.5) embeds each chunk
  -> qdrant stores vector plus payload (filename, page, kind, chunk_index, text)

question
  -> embed the question, qdrant returns the top 5 chunks
  -> build a numbered context block, [1] to [5], each labelled with file, page and kind
  -> claude answers under rules that forbid outside knowledge and require inline [n] citations
  -> parse [n] back out of the answer, map each to its chunk, return filename, page, kind, snippet
```

The code follows that shape. `ingest/extract.py` and `ingest/chunk.py` turn a PDF into chunks,
`ingest/store.py` talks to Qdrant, `rag/retrieve.py` fetches candidates, `rag/prompt.py` builds the
context block, `rag/answer.py` calls Claude and maps citations, and `api/routes.py` wires the four
endpoints together.

## The choices

**PyMuPDF, extracting page by page.** A citation that points at the wrong page is worse than no
citation, so the page number is the thing the whole pipeline is built around. PyMuPDF gives text per
page with the page index already attached, and that number travels with the text through chunking,
embedding and storage until it comes back out in the answer. Nothing in the chain can silently
renumber a page.

**Tables stay whole.** A table is one chunk no matter how long it gets. If you split a lab table at
800 characters you separate the header from the rows, and a retrieved fragment then reads as a
column of numbers with no analyte names, no units and no reference ranges. A citation pointing at
that is useless to a reader who wants to check the value. Keeping the table whole costs some
retrieval precision, because a 30 row table is one large embedding covering many topics, but it is
the difference between a citation that proves something and one that only looks like it does.

The prose pass on each page skips the areas the tables cover. Without that, the same values are
indexed twice, once as a table row and once as loose text, and the model can cite the loose copy
where the unit has been separated from the number. A block counts as part of a table when 60 percent
or more of its area falls inside the table rectangle. It is not 100 percent because PyMuPDF block
rectangles sit slightly looser than the table rectangle it reports.

**bge-small-en-v1.5 through fastembed, running locally.** Embeddings are ONNX on CPU, so the only
API key in the project is the Anthropic one. For an assessment project that is one fewer thing for a
reviewer to obtain before the thing runs. The model is 130 MB and downloads on first start. It is
loaded once at application startup rather than per request, because loading the weights takes a few
seconds and doing that inside a request would show up as a slow first question.

**Qdrant in Docker, one collection.** A single collection with cosine distance and 384 dimensions,
taken from the embedding model rather than hardcoded. Point IDs are a UUID5 of filename plus chunk
index, which makes re-ingesting a file idempotent: the same file produces the same IDs, so an upload
of a file already indexed overwrites its points instead of adding a second copy. Uploads also delete
by filename first, which handles the case where a document has been edited and now produces fewer
chunks than before.

**Claude for generation, with the rules in the system prompt.** The prompt forbids general medical
knowledge, requires the model to say plainly when the context does not answer the question, requires
inline `[n]` at the point of each claim rather than a list at the end, and tells it to keep units
with values when reading a table row. It also forbids diagnosis, treatment advice and interpretation,
which matters more here than in a general document assistant.

**Citations are parsed, not trusted.** The model writes `[n]`. The backend finds every `[n]` in the
answer and maps each number back to the chunk that actually occupied position n in the context
block. The citation's filename and page come from the chunk payload, never from anything the model
wrote. A number with no chunk behind it is dropped silently, so an invented `[9]` produces no source
row rather than a crash or a fabricated reference. Repeats of the same number collapse to one source.

The snippet shown under a citation is built per kind. For prose it is the first 300 characters of
the chunk. For a table that is useless, because the top of a 30 row table says nothing about the row
that was cited, so instead the snippet keeps the markdown header and the rows with the best term
overlap against the question, up to the same budget. That is a plain word overlap count, no second
model and no embedding call. If no row matches, it falls back to the top of the chunk.

## What a chunk carries

Every chunk is a flat dictionary, stored as the Qdrant payload as is.

| field | why it is there |
|-------|-----------------|
| `text` | what gets embedded, what goes into the context block, and what the snippet is cut from |
| `filename` | half of the citation, and the key for replace and delete, so re-uploading a file does not duplicate it |
| `page` | the other half of the citation, 1-based so it matches what a PDF reader shows |
| `kind` | `table` or `text`. decides whether the chunker splits it, tells the model whether it is reading a table, drives the table badge in the UI and the snippet strategy |
| `chunk_index` | position within the document. makes the point ID stable, and gives a deterministic order when several chunks come from the same page |

There is no separate database of documents. `GET /documents` derives the list by scrolling the
payloads and aggregating by filename, so there is one source of truth and nothing to fall out of
sync.

## Where the reranker sits, and why it is off

The reranker is a step between retrieval and generation, nothing more:

```
retrieve(question, 20)  ->  rerank(question, candidates, 5)  ->  generate(question, chunks)
```

`retrieve` returns a plain list of chunk dictionaries and `generate` takes a plain list, so the
reranker slots in without either side knowing about it. With `RERANK_ENABLED=false` the chain is
`retrieve(question, 5) -> generate`. The import of `sentence_transformers` happens inside the
branch, so a default install does not need torch at all.

I measured both paths over the 15 question eval set. The reranker lost on every metric.

| metric   | no rerank | rerank |
|----------|-----------|--------|
| recall@3 | 0.933     | 0.867  |
| recall@5 | 1.000     | 0.933  |
| MRR      | 0.883     | 0.769  |

The antibiotics question, which was the case I wanted it to fix, went from rank 4 to rank 5. The
eGFR question went from rank 2 to outside the top 5 entirely. Two questions that had been at rank 1
dropped to 2 and 3.

There are two reasons, and they compound.

The first is the 512 token limit of `cross-encoder/ms-marco-MiniLM-L-6-v2`. Because tables are kept
whole, a long table chunk runs well past that limit, so the cross-encoder scores a truncated version
of it. The row that answers the question is frequently in the part that was cut, which means the
model is scoring a passage that genuinely does not contain the answer. The decision to keep tables
whole, which is right for citation quality, is what breaks the reranker.

The second is training data. The model was trained on MS MARCO, which is web prose and natural
language passages. A markdown table of pipes and numbers looks nothing like that, and it scores low
against a plain English question even when the answer is sitting in it. This is why prose about the
patient's hospital stay keeps beating the medication table on a question about discharge
medication.

The fix is to rerank table chunks row by row: score each row against the question, take the best
rows as the unit of comparison, and let the table compete on its strongest row rather than on a
truncated block. That is a design change to how table chunks are represented at rerank time, not a
parameter to tune, so it is out of scope for this project. The flag and the code stay in the
repository so the measurement can be repeated.
