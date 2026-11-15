# Assessment Requirements Matrix

**Course:** C# / .NET Cross-Platform Development
**Project:** Memory Palace — Knowledge Atlas
**Team:** Amirzhanuly Abay and Shikhiyev Alikhan

The final-project rubric contains 20 extended criteria, each worth 5% of the overall mark. The matrix connects each criterion to implementation evidence and identifies the limits of that evidence. The presentation also covers the team, topic, aim, objectives, plan, technology comparison, architecture, practical relevance, methodology, and interface mockup.

**Version alignment to confirm:** The supplied project master context names .NET 6 and EF Core 6, while this teammate branch targets .NET 10 and EF Core 10. The rubric document does not name a required framework version. Confirm that the instructor accepts the updated target before submitting; this branch cannot be built with a .NET 6-only SDK, and reverting it would require porting EF Core 7+ APIs such as `ExecuteDeleteAsync`.

| # | Criterion | Weight | Implementation and evidence | Verification or scope boundary |
|---|---|---|---|---|
| 1 | Code Structure and Design | 5% | Domain, Data, Services, State, and Components directories; `IConceptService` abstraction, DI, separate graph algorithm | Layered structure within one application, rather than separate deployment services |
| 2 | Component Reusability | 5% | `Modal`, `ConceptEditor`, `ConnectionEditor`, `KnowledgeGraph`, and `ConceptDetails`; typed parameters, callbacks, cascading state | Browser interaction scenarios are provided separately |
| 3 | Cross-Platform Compatibility | 5% | .NET 10, SQLite, OS-independent paths, browser client; CI matrix for Windows/macOS/Linux | .NET build and assertion runners confirmed on Windows and macOS; Linux and browser/device checks remain pending |
| 4 | State Management | 5% | Scoped `AtlasState`, cached snapshot/filter results, selected concept, state event and disposal cleanup | Core checks verify selection/filter consistency; cross-tab refresh is explicit |
| 5 | UI Design | 5% | Consistent dark workspace, graph/library views, category color coding, summary statistics, contextual detail panel | Visual quality still benefits from review on physical displays |
| 6 | User Experience | 5% | Search, empty-result recovery, confirmation dialogs, status feedback, labeled inputs, keyboard controls, map pan/zoom and node drag | Manual assistive-technology testing remains on the checklist |
| 7 | Responsiveness | 5% | Grid layouts, mobile media queries, wrapping controls, bounded modal size, reduced-motion support | Playwright includes a mobile viewport; physical-device checks are separate |
| 8 | Core Functionality | 5% | Concept CRUD, directed typed relationships and notes, search/categories, SQLite persistence | 29 SQLite assertions cover principal service workflows |
| 9 | Advanced Features | 5% | BFS discovery and path highlighting; versioned JSON export and transactional restore; interactive graph pan/zoom and movable nodes | No custom cross-user real-time broadcast or role-based access control |
| 10 | Error Handling and Resilience | 5% | Service-side validation, transaction boundaries, busy guards, logging, recoverable error messages | Browser disconnection/recovery requires manual verification |
| 11 | Efficiency | 5% | No-tracking reads, split detail queries, bulk deletion of incident edges, bounded graph rendering | No latency benchmark or production performance target is claimed |
| 12 | Scalability | 5% | Short-lived contexts, indexed relations/categories/titles, service contract supporting future storage changes | In-memory personal-atlas snapshot; pagination and load testing are future work |
| 13 | Resource Utilization | 5% | Cached derived state, coordinates per graph update, 60-node rendering limit, disposed contexts/subscriptions, revoked download URLs | CPU/memory profiling has not been completed |
| 14 | Testing Coverage | 5% | 18 core assertions and 29 real-SQLite assertions pass on Windows and macOS cached package assets; Playwright workflow scenarios included | 47 assertions are not a measured code-coverage percentage; fresh restore, dependency audit, and browser scenarios remain pending |
| 15 | Quality Assurance | 5% | Reproducible commands, assertion failure exit codes, manual matrix and device checklist in `QA.md` | Browser/physical-device checks remain explicitly marked pending |
| 16 | Documentation | 5% | Setup guide, user walkthrough, architecture diagrams, service contracts, backup example, QA report, defense script | Documentation reflects local-workspace scope and actual execution evidence |
| 17 | Innovation | 5% | Knowledge relationships combine semantic direction with direction-independent discovery; map and library support different exploration styles | Educational benefit is a design hypothesis, not a measured research result |
| 18 | Creative Use of Blazor/C#/.NET | 5% | Cascading state, `EventCallback<T>`, DI factories, records, LINQ, async operations, EF transactions, JS download/dialog interop | Uses the built-in Blazor circuit rather than implementing a separate transport |
| 19 | Professionalism | 5% | Consistent English materials, named team, ignored build/database artifacts, reviewable commits, CI with warning-as-error builds | Authentication and production deployment hardening are outside current scope |
| 20 | Presentation | 5% | Twelve-slide PowerPoint and PDF deck, embedded speaker notes, 15–20 minute script, technology trade-offs, architecture, live demo, Q&A | Both students must attend and be prepared to explain every part of the project |
| | **Total** | **100%** | | |

## Submission and defense checklist

See [SUBMISSION.md](SUBMISSION.md) for the exact project files to upload and packaging guidance.

- [ ] Restore the final dependencies and pass the warning-as-error build and dependency audit.
- [ ] Repeat both executable runners against the resolved final package graph.
- [ ] Complete browser and device verification in `QA.md`.
- [ ] Rehearse the 15–20 minute presentation using a separate demo workspace.
- [ ] Confirm both full names and prepare each student to explain the complete implementation.

The matrix is an evidence map for assessment, not a prediction of the final grade.
