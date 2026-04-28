# Sources: Chapter 70 - The Energy Grid Collision

## Verification Key

- Green: direct support from official report, company statement, or primary
  technical/industry document.
- Green/Yellow: company framing or forecast range that must be attributed.
- Yellow: context/source-discovery support only.
- Red: not supported; do not draft.

## Primary / Near-Primary Source Spine

| Source | Use In Chapter | Anchor Notes |
|---|---|---|
| International Energy Agency, "Energy demand from AI," Energy and AI report, 2025. https://www.iea.org/reports/energy-and-ai/energy-demand-from-ai | Global demand, physical data-center components, regional concentration. | Green: web lines 243-255 define data centers, servers, storage, networking, cooling, UPS/generators; lines 278-286 estimate data-center electricity at about 415 TWh / 1.5% global electricity in 2024, project about 945 TWh / under 3% in 2030, and identify accelerated servers as AI-driven; lines 295-308 identify U.S./China/Europe growth and note localized concentration makes grid integration harder; lines 314-318 give sensitivity cases. |
| International Energy Agency, "Energy supply for AI," Energy and AI report, 2025. https://www.iea.org/reports/energy-and-ai/energy-supply-for-ai | Supply mix, renewables/gas/coal/nuclear, contractual vs physical mix. | Green: web lines 246-252 project data-center electricity generation from 460 TWh in 2024 to over 1,000 TWh in 2030, renewables nearly half of growth, gas/coal over 40% of additional demand to 2030, SMRs later, and physical vs contractual mix distinction; lines 262-266 cover U.S. gas/renewables/nuclear and tech companies financing more than 20 GW of SMRs; lines 280-285 cover sensitivity cases and fossil-fuel role. |
| Electric Power Research Institute, "Scaling Intelligence: The Exponential Growth of AI's Power Needs," Aug. 2025. PDF: https://restservice.epri.com/publicattachment/94532 | Frontier-training power, U.S. AI capacity, flexibility. | Green: local extraction lines 55-65 say frontier training drives renewed demand, current training runs consume about 100-150 MW and could reach 1-2 GW by 2028 and above 4 GW by 2030; lines 88-116 say training centers cannot keep doubling locally, distributed training is a strategy, U.S. AI capacity is about 5 GW today and could exceed 50 GW by 2030, and planning must account for concentrated/distributed loads and flexibility; lines 778-804 describe extreme localized loads and U.S. 2023 data-center TWh context; lines 990-1007 cite Berkeley Lab 6.7-12% U.S. 2028 and EPRI up to 9.1% by 2030; lines 1023-1032 discuss inference flexibility; lines 1095-1100 summarize 2.2x-2.9x annual training-power growth and 4-16 GW by 2030. |
| U.S. Department of Energy, "DOE Releases New Report Evaluating Increase in Electricity Demand from Data Centers," Dec. 20, 2024. https://www.energy.gov/node/4847688 | U.S. baseline and LBNL report release. | Green: search/open summary says the LBNL report finds data centers consumed about 4.4% of U.S. electricity in 2023 and are expected to consume approximately 6.7-12% by 2028. Use for official DOE/LBNL framing; if prose needs page anchors, fetch LBNL PDF through an accessible mirror or use EPRI's quotation of the same figures. |
| Constellation Energy, "Constellation to Launch Crane Clean Energy Center..." Sept. 20, 2024. https://www.constellationenergy.com/news/2024/Constellation-to-Launch-Crane-Clean-Energy-Center-Restoring-Jobs-and-Carbon-Free-Power-to-The-Grid.html | Microsoft/Three Mile Island restart scene. | Green/Yellow: web lines 343-348 say Constellation signed a 20-year PPA with Microsoft to restart TMI Unit 1 / Crane Clean Energy Center and add about 835 MW carbon-free energy; lines 351-354 say restart requires NRC/state/local approvals, expected online 2028, and adds 800+ MW; lines 365-366 say the plant had 837 MW generating capacity before 2019 closure. Company framing; approval/timing caveats required. |
| Google, "New nuclear clean energy agreement with Kairos Power," Oct. 14, 2024. https://blog.google/company-news/outreach-and-initiatives/sustainability/google-kairos-power-nuclear-energy-agreement/ | Google/Kairos SMR orderbook scene. | Green/Yellow: web lines 264-280 say Google signed the first corporate agreement to purchase nuclear energy from multiple SMRs, first Kairos SMR intended by 2030, additional deployments through 2035, up to 500 MW of 24/7 carbon-free power, and grid needs for AI; lines 283-290 explain portfolio and advanced-reactor timing claims. Company framing; future deployment not guaranteed. |
| Meta, "Meta and Constellation Partner on Clean Energy Project," June 3, 2025. https://about.fb.com/news/2025/06/meta-constellation-partner-clean-energy-project/ | Meta/Clinton nuclear preservation scene. | Green/Yellow: web lines 277-283 say Meta values nuclear for reliable firm electricity and signed a 20-year agreement starting 2027 to secure Clinton Clean Energy Center operation, 1,121 MW emissions-free nuclear energy, and 30 MW incremental capacity; lines 286-290 discuss Meta's nuclear RFP and demand signal. Company framing. |
| Constellation, "Constellation, Meta Sign 20-Year Deal..." June 3, 2025. https://www.constellationenergy.com/news/2025/constellation-meta-sign-20-year-deal-for-clean-reliable-nuclear-energy-in-illinois.html | Confirmation of Meta/Clinton terms and physical-grid caveat. | Green/Yellow: web lines 343-350 confirm 20-year PPA, 1,121 MW, June 2027 start, Clinton relicensing/continued operation, and that the plant continues to flow power to the local grid while Meta buys clean-energy attributes. Use this to avoid false "direct powering" language. |
| Wikipedia pages on AI data centers, Three Mile Island, SMRs, power purchase agreements, and data-center energy. | Source discovery only. | Yellow: useful for names and chronology. Do not cite as evidence in prose. |

## Scene-Level Claim Table

| Claim | Scene | Primary Anchor | Confirmation | Status | Notes |
|---|---|---|---|---|---|
| Data centers are physical facilities with servers, storage, networking, cooling, UPS batteries, backup generators, and grid connections. | Cloud To Load | IEA demand lines 243-255 | IEA demand lines 276-286 | Green | Opening demystification. |
| IEA estimates data centers used about 415 TWh, or 1.5% of global electricity, in 2024 and projects about 945 TWh / under 3% in 2030. | Aggregate/Local | IEA demand lines 278-284 | IEA supply lines 246-252 | Green | Use to prevent overclaiming. |
| Accelerated servers, mainly AI-driven, are projected by IEA to grow 30% annually in the Base Case and account for almost half of net data-center electricity increase. | Aggregate/Local | IEA demand lines 283-286 | EPRI lines 55-65 | Green | Good bridge from data centers to AI. |
| IEA projects U.S. and China account for nearly 80% of global data-center electricity-consumption growth to 2030, and local concentration makes grid integration harder. | Aggregate/Local | IEA demand lines 295-308 | IEA supply lines 262-277 | Green | Local vs global distinction. |
| EPRI forecasts frontier training runs around 100-150 MW now, 1-2 GW by 2028, and above 4 GW by 2030 in high scenarios. | Training Spike | EPRI lines 55-65 | EPRI lines 1095-1100 | Green | Keep uncertainty/range. |
| EPRI estimates U.S. AI power capacity around 5 GW today and potentially above 50 GW by 2030. | Training Spike | EPRI lines 96-116 | EPRI lines 990-1007 | Green | Forecast, not fact. |
| Berkeley Lab/DOE found U.S. data centers were about 4.4% of U.S. electricity in 2023 and could reach 6.7-12% in 2028; EPRI's prior forecast says up to 9.1% by 2030. | U.S. Share | DOE/LBNL summary; EPRI lines 990-1001 | EPRI lines 803-804 | Green | Use ranges, not single point. |
| IEA says data centers can be operational in two to three years, but energy infrastructure requires longer planning, build time, and investment. | Timing Mismatch | IEA demand lines 280-283 | EPRI lines 106-116 | Green | Core structural tension. |
| IEA expects renewables to meet nearly half of additional data-center demand to 2030, while gas and coal together meet over 40%. | Fuel Mix | IEA supply lines 246-252 | IEA supply lines 280-285 | Green | Physical supply, not PPA claims. |
| IEA distinguishes physical electricity consumed from contractual mix claimed by data-center operators. | Fuel Mix | IEA supply lines 246-249 | Constellation/Meta lines 343-350 | Green | Essential guardrail. |
| Microsoft/Constellation signed a 20-year PPA intended to restart TMI Unit 1 / Crane Clean Energy Center and add about 835 MW to the grid, subject to approvals. | Nuclear Procurement | Constellation TMI lines 343-354 | Constellation TMI lines 365-366 | Green/Yellow | Company release; future restart caveat. |
| Google/Kairos announced a corporate agreement for multiple SMRs, first by 2030, up to 500 MW by 2035. | Nuclear Procurement | Google lines 264-280 | Google lines 283-290 | Green/Yellow | Company future plan. |
| Meta/Constellation signed a 20-year Clinton agreement starting 2027 for 1,121 MW emissions-free nuclear energy and 30 MW incremental capacity. | Nuclear Procurement | Meta lines 277-283 | Constellation/Meta lines 343-350 | Green/Yellow | Note clean attributes/local grid. |
| EPRI says inference may be more real-time/geographically flexible than training, allowing query routing by local grid load and renewable penetration when latency allows. | Flexibility | EPRI lines 1023-1032 | EPRI lines 112-116 | Green | Partial mitigation only. |

## Conflict Notes

- Global share and local stress are different claims. The chapter should say
  "localized grid integration can be hard" rather than "AI uses too much
  global electricity."
- Company nuclear announcements are not completed generation. Date them and use
  "announced," "intended," "expected," or "subject to approval" where needed.
- Clean-energy attributes and PPAs do not always mean direct physical delivery.
  Constellation/Meta explicitly says Clinton power continues to flow to the
  local grid while Meta buys attributes.
- EPRI's high-end single-training-cluster projections are scenarios. Do not
  present 4-16 GW by 2030 as certain.
