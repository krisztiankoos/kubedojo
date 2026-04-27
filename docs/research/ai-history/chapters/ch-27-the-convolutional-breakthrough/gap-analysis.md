# Gap Analysis: Chapter 27 - The Convolutional Breakthrough

Source: Gemini gap analysis on PR #410, recorded 2026-04-27.

## Current Verdict

Research contract approved, but not prose-ready. The chapter has a strong stretch path because LeNet sits at the intersection of architecture, datasets, Bell Labs engineering, document workflows, and deployment constraints. The stretch depends on exact page anchors, especially for LeCun 1998 production-pipeline details.

## Claims Still Yellow or Red

| Claim Area | Status | Why |
|---|---|---|
| Fukushima as architectural prehistory | Yellow | Needs exact passages on hierarchical architecture and shift tolerance. |
| USPS dataset details | Yellow | Needs data specifics from LeCun 1989 and a clean distinction from later MNIST/NIST history. |
| LeNet-5 production pipeline | Yellow | Needs exact operational claims about preprocessing, segmentation, check/document recognition, and system placement. |
| Architecture reducing search space | Yellow | Interpretive claim needs careful support from LeCun 1989/1998 and later retrospectives. |
| Check-volume numbers, hardware, deployment timeline | Red | Unsafe until explicitly anchored. |
| "First CNN" language | Red | Avoid unless a strongly qualified source supports it; current safer framing is lineage plus breakthrough. |

## Required Anchors Before Prose Readiness

- Fukushima 1980: shift-invariance and hierarchical architecture passages.
- LeCun et al. 1989: domain constraint, USPS dataset, network architecture, and performance passages.
- LeCun et al. 1990: network diagram/architecture and training details.
- LeCun et al. 1998: LeNet-5 architecture, check/document-recognition pipeline, deployment or throughput stats, preprocessing steps.
- MNIST page: dataset origin details distinguishing MNIST/NIST from original USPS data.

## Scene Strength

| Scene | Strength | Notes |
|---|---|---|
| Pixels With Structure | Thin | Needs LeCun 1989/1998 architecture passages. |
| From Neocognitron to Backprop | Thin | Needs Fukushima passages to avoid overclaiming. |
| The Postal Code Laboratory | Medium | Conceptually grounded; needs USPS data and training/test statistics. |
| Checks, Throughput, and Engineering | Thin to medium | Strong if LeCun 1998 deployment, preprocessing, throughput, and hardware anchors are found. |
| Why It Waited | Medium | Later retrospective exists, but needs careful transition sourcing. |

## Word Count Assessment

- Core range today: 2,500-3,500 words.
- Stretch range with production/hardware/data anchors: 4,000-6,000 words.

The chapter can responsibly grow if it becomes a system story, not a generic CNN tutorial. Without deployment and pipeline anchors, it should stay closer to the core range.

## Responsible Expansion Path

To reach 4,000-7,000 words without bloat, source:

- exact production throughput or deployment metrics from LeCun 1998
- hardware and compute context for the 1989 and 1998 systems
- document-recognition pipeline details: image capture, normalization, segmentation, recognition, downstream business rules
- USPS/NIST/MNIST dataset chronology and sizes
- optional Bell Labs archival demo/video material for color only after primary claims are anchored

## Handoff Requests

- Retrieve PDFs for Fukushima 1980, LeCun 1989, LeCun 1990, and LeCun 1998.
- Extract page numbers and passages listed in the anchor worklist.
- Search for archival Bell Labs demos only as supporting context, not primary proof.
- Verify whether Denker et al. 1988/1989 should be added to strengthen Bell Labs lineage.
