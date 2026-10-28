# Medical document assistant

Upload medical PDFs, ask questions about them, get answers that cite the file and page they came
from. Every claim in an answer carries a number you can click to see the exact text it came from,
including the row of a lab table. If the documents do not contain the answer, it says so instead of
guessing.

## Setup

You need Docker, Python 3.11 or newer, Node 18 or newer, and an Anthropic API key.

A fresh clone has no `.env`, only `.env.example`. Create one before you start the backend, or the
app will index documents happily and then fail on the first question with a 401 from Anthropic.

On windows:

```
copy .env.example .env
```

On mac and linux:

```
cp .env.example .env
```

Now open `.env` in an editor and paste your key after `ANTHROPIC_API_KEY=`, replacing the
placeholder. The line should read `ANTHROPIC_API_KEY=sk-ant-...` with no quotes and no spaces around
the `=`. The other values in the file work as they are.

Start Qdrant:

```
docker compose up -d
```

Backend:

```
cd backend
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

On mac and linux the interpreter is at `.venv/bin/python` instead.

The first start downloads the embedding model, about 130 MB. It can take a minute and prints
download progress. It is not stuck.

Frontend, in a second terminal:

```
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## How to use it

Drop the three PDFs from `sample_docs/` onto the upload area, or click to pick them. Each one takes
a few seconds to index and the panel names the file it is working on. Once something is indexed the
chat box turns on.

Ask something the documents can answer, for example "what was the ferritin result and its reference
range". The answer comes back with small numbered chips in the text. Click a chip, or a row in the
Sources list, to open the snippet it came from. For a table the snippet shows the header and the
matching row, so you can check the number yourself.

Try an unanswerable question too, for example asking for a blood group. It will tell you the
documents do not contain it.

## Sample documents

The three PDFs in `sample_docs/` are synthetic. I generated them with `scripts/make_samples.py`
using reportlab. The patients, the clinic and every value are invented, and each file says so on its
first line. There is no real patient data anywhere in this repository.

That matters here. A medical project needs test data you can commit, share and screenshot without
touching anyone's records.

The set covers the three shapes that behave differently: a lab report whose ruled table runs past
one page, a discharge summary that is mostly prose with a small medication table, and a radiology
report that is prose only.

## Architecture

A PDF is split into chunks that each remember the file, the page and whether they came from a table
or from prose. Those chunks are embedded locally and stored in Qdrant. A question is embedded the
same way, the closest five chunks go to Claude in a numbered context block, and the `[n]` markers in
the answer are parsed back out and mapped to the chunks they refer to. That is where a citation's
file name and page come from.

[ARCHITECTURE.md](ARCHITECTURE.md) has the full flow, the reasoning behind each choice, and what a
chunk carries.

## Evaluation

`backend/eval/questions.yaml` holds 15 questions written against the real content of the three
samples, each with the file and page that answers it. Several can only be answered from a table,
including the medication table in the discharge summary. Questions marked as table questions only
count as a hit when the retrieved chunk is the table, not the prose on the same page.

Run it with Qdrant up:

```
cd backend
.venv\Scripts\python.exe -m eval.run_eval
```

It ingests the samples, runs every question twice, once with reranking off and once on, and prints
recall@3, recall@5 and MRR side by side, plus the top three results per question so you can tell a
miss from a near miss. It is not part of the test suite and `pytest` never collects it.

| metric   | no rerank | rerank |
|----------|-----------|--------|
| recall@3 | 0.933     | 0.867  |
| recall@5 | 1.000     | 0.933  |
| MRR      | 0.883     | 0.769  |

## Reranking

I built a cross-encoder reranker and measured it against plain vector search. It lost on every
metric in the table above, and it failed to fix the case I built it for, the medication table losing
to prose on a question about discharge medication. So it ships off.
[ARCHITECTURE.md](ARCHITECTURE.md#where-the-reranker-sits-and-why-it-is-off) explains why it lost.

To try it yourself, install the extra dependency at the bottom of `requirements.txt` and set
`RERANK_ENABLED=true`. A default install does not include it, which keeps torch out of the project.

## Limitations

A table that continues onto the next page is read as two separate tables, and only the first one
carries the header row. The samples repeat the header on each page so this does not show there, but
a real PDF often will not.

The eval numbers are flattering. The whole corpus is 15 chunks, so the top 5 covers about a third of
everything indexed.

The first version of the eval counted a hit on filename and page alone, and both paths scored almost
perfectly. The medication table and the prose that outranks it sit on the same page of the discharge
summary, so page level ground truth could not see the exact failure I was measuring. I tightened it
so a table question only counts a table chunk as a hit. The numbers above are from the stricter
version.

There is no streaming, so an answer appears all at once after a few seconds. There is no
authentication and no notion of users. Everyone pointing at the same backend sees the same
documents.

## Privacy and data handling

PDFs are parsed on your machine and uploaded files are not kept, only the extracted chunks. Those
chunks live in the Qdrant collection, which is stored in `qdrant_storage/` next to the repository.

The text of the retrieved chunks is sent to the Anthropic API to generate the answer. Nothing else
leaves the machine.

To wipe everything, use the Clear all button, or:

```
curl -X DELETE http://localhost:8000/documents
```

To remove the storage completely, stop the container and delete the folder:

```
docker compose down
rmdir /s /q qdrant_storage
```

On mac and linux use `rm -rf qdrant_storage`.

## Not medical advice

This is a demonstration of document retrieval. It is not medical advice and must not be used for
clinical decisions.
