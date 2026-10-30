# How I would split it into services

The code is one deployable today, with clear module boundaries. The split I would
propose when load or team ownership requires it:

| Service | Why separate | Scales on |
|---|---|---|
| Ingestion and validation | untrusted input, cheap CPU, must fail fast | request rate |
| Document processing (preprocess, detection, OCR) | CPU or small GPU, batchable | pages per second |
| GPU inference (vLLM serving LLaVA) | expensive GPUs, its own release cycle | tokens per second, queue length |
| Review and validation | user-facing, stores decisions | users |

I would not go further than that. Every extra service adds a network hop, a
deployment and one more place to look when something breaks. The test is whether
the split buys real independence: different resources, different release cadence or
different owners.
