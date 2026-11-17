# Diagram assets — DragonStorm Triton Lab

Three vector images recreated from the three concept-flow diagrams generated in the DragonStorm discussion. Unlike the large PNGs displayed in the chat, these SVG versions are lightweight, searchable, and render as ordinary GitHub Markdown image references.

| Filename | Concept | Recommended location |
|---|---|---|
| [triton-experiment-cat-eye-overview.svg](triton-experiment-cat-eye-overview.svg) | Full experiment at a glance, validated outcomes, initial performance and possible Cat-Eye relevance | [Architecture explainer](../ARCHITECTURE.md#1-experiment-overview--why-this-matters-for-cat-eye) |
| [triton-infrastructure-architecture.svg](triton-infrastructure-architecture.svg) | Windows → Azure VM → Docker/Triton/ONNX, model-repository mount | [Infrastructure architecture](../ARCHITECTURE.md#2-infrastructure-architecture) |
| [triton-inference-pipeline-bw.svg](triton-inference-pipeline-bw.svg) | Black-and-white Python/JPEG → Triton V2 → model → detections → annotated JPEG | [Inference flow](../ARCHITECTURE.md#3-end-to-end-image-inference-flow-black-and-white) |

All three are **recreated SVG illustrations**, not original pixel-for-pixel PNG exports. They intentionally contain no private IPs, subscription IDs or SSH key material. The first diagram's performance table is the verified November 13 **exploratory** CPU benchmark, not a production SLA. The depicted architecture is an independent learning lab rather than Cat-Eye deployment evidence.

The raw dog photograph/annotated result and personally identifying Azure screenshots were deliberately not included in the public GitHub repo. See [source evidence](../journal/2026-11-13-triton-preprocessing-benchmark.md).
