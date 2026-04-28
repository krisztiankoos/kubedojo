# Brief: Chapter 70 - The Energy Grid Collision

## Thesis

After Ch69's data wall, the next limit is not abstract compute. It is
electricity delivered to a specific place at a specific time. AI scaling turned
data centers from background internet infrastructure into visible grid actors:
multi-hundred-megawatt training clusters, gigawatt campus plans, nuclear PPAs,
gas buildout pressure, interconnection queues, and regional siting fights. The
chapter should avoid the lazy claim that "AI will consume all electricity."
The stronger historical point is narrower and more interesting: AI's share of
global electricity remains modest in aggregate, but its loads are large,
fast-moving, concentrated, and reliability-sensitive. That mismatch collides
with a grid built through slower planning cycles.

## Scope

- IN SCOPE: IEA 2025 Energy and AI demand/supply estimates; global data center
  demand growing from about 415 TWh in 2024 to about 945 TWh in 2030; U.S.,
  China, and Europe regional concentration; EPRI frontier-training power
  forecasts; DOE/LBNL U.S. data-center share estimates; grid connection and
  planning lead-time mismatch; Amazon/Talen/Susquehanna/FERC as the concrete
  co-located-load regulatory collision; renewables/gas/coal/nuclear supply mix;
  PPAs and nuclear preservation/restart deals by Microsoft, Google, and Meta;
  flexible load as a mitigation.
- OUT OF SCOPE: chip export controls and semiconductor geopolitics (Ch71);
  hyperscale campus architecture, water, cooling, and land as the dominant story
  (Ch72); general climate-policy essay; precise carbon accounting for every
  company; unsourced claims about "one query" electricity; claiming AI alone is
  the main global electricity-growth driver.

## Required Scenes

1. **From Cloud To Load:** Open by turning "the cloud" back into racks, servers,
   cooling, UPS batteries, backup generators, and grid connections. Use IEA's
   component description so the prose begins physically.
2. **The Aggregate Looks Small, The Local Load Is Huge:** IEA projects data
   centers at under 3% of global electricity in 2030, but also says U.S. per
   capita data-center consumption is uniquely high and data centers concentrate
   in specific locations. This is the collision.
3. **The Frontier Training Spike:** EPRI's forecast makes individual training
   clusters a power-plant-scale planning problem: 100-150 MW now, 1-2 GW by
   2028, more than 4 GW by 2030 in some scenarios. Keep uncertainty visible.
4. **The Grid Moves Slower Than The Model Race:** IEA says data centers can be
   operational in two to three years, while energy infrastructure has longer
   planning, build, and investment lead times. That mismatch is the chapter's
   structural tension.
5. **The Fuel Mix Reality:** IEA expects renewables to meet nearly half of
   incremental data-center demand to 2030, but gas and coal together to meet
   more than 40%. Nuclear grows later, especially after 2030. The prose should
   distinguish contractual clean-energy claims from physical electricity mix.
6. **The Susquehanna Collision:** The Amazon/Talen/PJM/PPL amended ISA attempted
   to increase co-located load at Susquehanna from 300 MW to 480 MW. FERC
   rejected it because PJM did not meet the high burden for non-conforming
   interconnection provisions. Commissioner Christie's concurrence names the
   policy stakes: grid reliability, consumer costs, precedent, backup service,
   and whether a data-center load can benefit from the grid while sitting behind
   a generator meter. Chairman Phillips' dissent makes the opposite case:
   rejecting the arrangement slows AI infrastructure and national-security
   buildout. This scene is the chapter's courtroom-level collision.
7. **Nuclear Becomes AI Infrastructure:** Microsoft/Constellation, Google/Kairos,
   and Meta/Constellation show hyperscalers turning energy procurement into
   infrastructure strategy: restart an existing reactor, order future SMRs,
   preserve a running plant.
8. **Flexibility As A Partial Escape:** EPRI notes inference may be more
   geographically and temporally flexible than training. Treat this as a
   mitigation lever, not a solved problem.

## Prose Capacity Plan

Target range: 5,000-6,000 words after source verification.

- 550-650 words: bridge from Ch69 to physical load and define data-center
  components.
- 650-750 words: global and regional demand: 415 TWh in 2024, about 945 TWh in
  2030, U.S./China/Europe concentration, local siting pressure.
- 650-750 words: EPRI frontier-training power and U.S. data-center share
  estimates. Keep ranges and uncertainty.
- 650-750 words: timing mismatch between tech deployment and grid buildout,
  including interconnection/planning pressure.
- 750-900 words: Susquehanna/FERC co-located-load dispute, including the 300 MW
  to 480 MW ISA amendment, grid-reliability/cost-shift concerns, Talen's
  counterargument, and the Phillips/Christie split. Keep legal nuance.
- 600-700 words: supply mix: renewables, gas, coal, nuclear, physical vs
  contractual electricity.
- 750-850 words: company procurement scenes: Microsoft/Three Mile Island,
  Google/Kairos, Meta/Clinton.
- 400-650 words: flexible load, training vs inference, and handoff to Ch71's
  chip-geopolitics and Ch72's megacampus story.

## Guardrails

- Do not claim AI/data centers dominate global electricity demand. IEA says the
  global share remains limited even under strong growth.
- Do not collapse global and local claims. The important risk is concentration:
  large loads in specific grids.
- Do not treat company clean-energy PPAs as proof that electrons physically flow
  from a named plant to a named data center unless the source says so.
- Do not speculate about exact power use of individual model runs beyond EPRI's
  scenario ranges.
- Do not use viral "one ChatGPT query equals X" claims unless they come from the
  anchored sources and are necessary. The chapter does not need them.
- Do not make this a nuclear booster chapter. Nuclear is a procurement response
  to 24/7 firm power needs, with permitting, timing, cost, and public-trust
  constraints.
- Do not flatten the FERC/Susquehanna dispute into "FERC blocked Amazon." The
  primary order rejected PJM's amended ISA on the record before it; Talen said
  the existing 300 MW campus phase could proceed while it pursued approval.
- Keep China/export-control/geopolitics for Ch71 and datacenter campus/water
  scale for Ch72.
