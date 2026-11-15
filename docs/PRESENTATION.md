# Memory Palace — Defense Script

**Course:** C# / .NET Cross-Platform Development

**Team:** Amirzhanuly Abay and Shikhiyev Alikhan

**Format:** 12 slides, approximately 18–20 minutes including a four-minute live demo.

Open `Memory_Palace_Defense.pptx` in PowerPoint, Keynote, or a compatible presentation editor. All slide text and diagrams are editable. Speaker notes are included for every slide. Use `Memory_Palace_Defense.pdf` for a read-only copy or direct upload.

Both names are already entered on the title and closing slides. To change them, edit those text boxes and this script. To rebuild the files from source, run `python3 tools/build_presentation.py` from the repository root after installing the dependencies in `tools/presentation-requirements.txt`. The PDF and PowerPoint are built from the same layouts; the PDF is not an Office-rendered export.

Both students should rehearse the entire implementation and be ready to explain every layer. Use a separate demo workspace and consult `QA.md` for current verification status.

## Slide 1 — Memory Palace · 45 sec

Good afternoon. We are Amirzhanuly Abay and Shikhiyev Alikhan. Our project is Memory Palace — Knowledge Atlas, a personal knowledge workspace built with C#, .NET 10, and Blazor Server.
The project starts from a simple observation: collecting definitions is easier than explaining how those definitions connect. We wanted a small application where a student can capture an idea, describe a relationship, and follow a chain into another subject.
We will show the user workflow, explain the architecture and integrity rules, walk through the path-finding algorithm, and finish with a live demonstration and the verification results. The scope is a local personal workspace rather than a multi-user cloud service.

## Slide 2 — The problem and the goal · 75 sec

The intended audience is students organizing material across subjects. Ordinary notes can store useful definitions, but related ideas are often separated by files, folders, or courses. A student may know each term without being able to explain the relationship between them.
Our aim is to make those relationships visible and searchable. The three core objectives are capture, connect, and discover. Capture means validated concepts with descriptions and categories. Connect means directed, typed relationships with a short note explaining the link. Discover means search, filtering, and a shortest chain between two concepts.
Persistence and backup support all three objectives. The practical value is an inspectable study atlas; we have not conducted a study claiming improved memory or higher grades. For the demonstration, the example combines learning techniques, graph theory, and the technologies used to build the application.

## Slide 3 — Existing approaches · 1 min

We compared approaches rather than trying to reproduce every feature of a large commercial tool. Files and linear notes are simple and portable, and they work well for long-form content. Wiki-style links improve navigation, but a relationship such as supports or contradicts still needs a convention. General graph systems offer flexible modeling and more powerful queries, with more setup and a steeper learning curve.
Memory Palace narrows the problem to concise concepts, five relationship types, and unweighted path discovery. It combines a spatial view with a conventional searchable library, so users do not have to rely on the graph for every action.
This is the project's relevance and its main design trade-off: fewer features, but a focused workflow that can be implemented, tested, and explained within the course scope. It is not a claim that a small coursework application replaces all note-taking or graph-database products.

## Slide 4 — Technology choices · 90 sec

The application targets .NET 10 and uses Blazor Server for UI event handling. That lets us write both UI workflows and business logic in C#, with direct server-side access to the service layer. It avoids a separate REST API for this local scope, but the browser needs a connection to the running server.
Blazor WebAssembly would move UI execution into the browser. The trade-offs include downloading the browser runtime and introducing a separate boundary for data access. Neither hosting model is universally better; the choice follows the deployment and learning goals.
SQLite is a file-based database with no separate server installation. It is convenient for a portable personal workspace, while an external relational database is a better fit for multiple application servers or heavier concurrent writes. EF Core handles mapping and transactions. We chose SVG and CSS for the graph rather than adding a separate graph-rendering framework.

## Slide 5 — The workspace · 75 sec

This is an interface schematic, not a screenshot of a measured browser session. The main layout puts the current workspace in the center and selected-concept details on the right. A narrow navigation rail switches between the spatial map and the library. Search and category controls narrow the same underlying concept set.
The normal workflow is to create a concept, connect it, and explore the resulting relationships. The detail panel keeps the definition and connection notes beside the graph, rather than requiring navigation away. The library is important as an alternative for users who prefer text-based browsing or have a larger collection.
The development method followed four increments: establish the model and integrity rules, complete workflows, verify the core and service behavior, and prepare delivery materials. The page coordinates actions, but reusable editor, modal, graph, and detail components each have narrower responsibilities.

## Slide 6 — Architecture · 2 min

The browser communicates with a Blazor Server circuit. Index coordinates user workflows and feedback. AtlasState holds the current snapshot, filters, counts, and selected concept. Components depend on IConceptService rather than on the database context; ConceptService owns validation, transactions, and backup workflows.
State is scoped to one circuit, so independent tabs keep separate selections and search terms. The database itself is shared. A refresh explicitly reloads changes from another tab; there is no custom broadcast service.
A central design choice is IDbContextFactory. A Blazor circuit can live much longer than one HTTP request, and handlers may overlap. EF Core contexts are not thread-safe, so every service operation creates and disposes a short-lived context. The graph algorithm is independent of UI and persistence, making it straightforward to test.
Continuous map gestures now render locally in the browser. Only a completed node move updates the component state. This avoids a server round trip for every pointer movement while preserving the concept's position across component renders.

## Slide 7 — Data integrity · 90 sec

The domain model has two entities. Concept contains an ID, title, description, category, and creation/update timestamps. Connection contains its own ID, a source concept, a target concept, a relationship type, and an optional note.
The ordered source and target pair has a unique database index. This prevents a duplicate A-to-B relationship, while allowing B-to-A as a distinct relationship. The service rejects self-links, missing endpoints, undefined relation values, and invalid text lengths. Titles are trimmed, normalized, and checked without case sensitivity in the service transaction. Title uniqueness is not a separate database constraint.
Deleting a concept first removes both incoming and outgoing relationships, then the concept, in one transaction. This matters because the target-side foreign key restricts deletion.
Restore validates the complete backup before writing and requires an empty atlas. One transaction commits the validated set. Flat records avoid cycles from EF navigation properties. The goal is predictable failure without leaving dangling edges or a half-restored workspace.

## Slide 8 — Shortest-path discovery · 90 sec

This example uses the demonstration dataset. Spaced Repetition connects to Active Recall, which connects to Memory Palace. SQLite also connects to Memory Palace. The discovered chain from Spaced Repetition to SQLite is therefore three steps.
Discovery treats relationships as traversable in either direction. That is why it can move from Memory Palace to SQLite even though the stored semantic direction is the reverse. The stored direction and relationship type are not changed.
BFS starts with the source in a queue and explores neighbors layer by layer. A predecessor table records how each vertex was reached and marks it visited. When the destination is reached, following predecessors reconstructs the path. Cycles cannot enqueue the same vertex indefinitely.
For V vertices and E edges, both time and auxiliary space are O(V + E). All edges have equal traversal cost, so BFS finds a shortest chain. Weighted relations would need an algorithm such as Dijkstra's. A missing or disconnected endpoint returns no path; identical endpoints return a zero-step path.

## Slide 9 — Live demonstration · 4 min

Use a separate demonstration workspace. Restore docs/demo-atlas.json into an empty atlas and show the eight concepts and nine relationships. Avoid deleting personal data just to reset the demonstration.
First, select Breadth-First Search and inspect its connections. Explain that relationship notes describe why two concepts are linked. Second, create Learning Journal in the Learning category, then edit its description. Connect it to Active Recall with the Supports type and an explanatory note.
Third, find the path from Spaced Repetition to SQLite. Read the chain and point out that discovery can traverse a relationship backwards. Pan the map, drag a node, zoom, and reset. Switch to the library, use a search or category, and clear the filter.
Finally, export a backup. Open the deletion confirmation for Learning Journal, cancel once, and then confirm. Show that the other concepts remain without a dangling connection. Reload to demonstrate persistence. If time is short, prioritize create, connect, discover, and export. Keep the architecture slide available if the live server is unavailable.

## Slide 10 — Verification · 75 sec

The project has two executable assertion runners rather than a third-party test-framework runner. MemoryPalace.CoreChecks tests the independent graph algorithm and scoped-state behavior. MemoryPalace.Tests uses the actual ConceptService against a uniquely named temporary SQLite database, which it removes in a finally block.
On 15 November 2026, the complete solution built on macOS arm64 with .NET SDK 10.0.401 using the restored package assets. The build had zero errors and zero warnings. All 18 core checks and all 29 SQLite integration checks passed. The resolved assets included EF Core SQLite 10.0.12 and SQLitePCLRaw bundle 3.0.5.
The 47 assertions are not a measured line-coverage percentage. JavaScript syntax checks passed, and browser scenarios cover workflows and the new map interactions, but this environment denied Chromium launch. The browser and device matrix therefore remains pending. A fresh package restore and vulnerability audit are also separate from the successful cached-asset build. The QA document records these distinctions.

## Slide 11 — Trade-offs and next steps · 1 min

The current scope is a local personal workspace. It has no authentication, separate user-owned datasets, automatic cross-tab broadcasting, or optimistic concurrency token. Concurrent edits use a last-successful-write policy; lock or write errors produce recoverable feedback rather than automatic merging.
The whole personal atlas is loaded into memory. The graph is bounded to 60 visible nodes for readability and DOM size, with discovered path nodes prioritized. The library and complete text path remain available, but server-side pagination, full-text search, and load benchmarking are future work.
The next steps follow those limits: add identity and ownership before internet deployment, add migrations and concurrency handling as the schema evolves, and add pagination and larger graph layouts as data grows. Short-lived contexts, a service interface, and an independent graph algorithm provide clear extension points. These boundaries are deliberate scope decisions, not features that have already been completed.

## Slide 12 — Discussion · 30 sec

To conclude, Memory Palace combines three capabilities: capture concise concepts, explain typed relationships, and discover a shortest chain between ideas. The project connects reusable Blazor components with scoped state, service-level validation, transactional SQLite storage, and a separately testable graph algorithm.
The running demonstration and recorded checks support the implemented scope. Browser verification and the larger deployment concerns remain clearly identified in the QA report and roadmap.
Thank you. We are ready to discuss the architecture, BFS, data-integrity rules, testing strategy, and the trade-offs behind the implementation. Keep the source, architecture document, and demonstration workspace available for questions. Both team members should be able to explain every layer, including the parts they did not present.

## Defense Q&A

| Question | Key answer |
|---|---|
| Why is a scoped `DbContext` problematic in Blazor Server? | A circuit is long-lived and handlers can overlap; a context is not thread-safe. A factory provides one context per operation. |
| Why use a scoped state container? | Selection and filters belong to one circuit. Persistent data is shared, while presentation state stays local. |
| Why BFS instead of DFS? | BFS explores by distance and finds a shortest unweighted chain; DFS does not guarantee that result. |
| What happens when the graph contains a cycle? | A predecessor entry marks a vertex as visited; it is enqueued once. |
| Why traverse relationships in both directions? | Discovery asks whether ideas are connected. Stored direction still expresses the semantic relationship. |
| What if source and destination are the same? | Return a single-vertex, zero-step path. |
| What if there is no path? | Return an empty result and show a no-connection message. |
| What prevents duplicate relationships? | A unique database index on the ordered source/target pair, plus service validation. |
| Is title uniqueness a database constraint? | No. It is checked after normalization using case-insensitive comparison in the transactional service workflow. |
| Why remove edges explicitly before deleting a concept? | The incoming target FK restricts deletion; removing all incident edges preserves integrity. |
| What prevents a partial restore? | Complete validation before writes and a transaction around the entire insertion. |
| Why require an empty atlas for restore? | It prevents silent overwriting and avoids inventing a merge policy for IDs and titles. |
| Why export flat records? | EF navigation properties contain cycles; flat records produce a stable portable format. |
| What happens with two simultaneous edits? | The last successful write wins. There is no concurrency token or automatic merge; write conflicts surface as recoverable errors. |
| Does the app work offline? | The browser needs a connection to the running server. The database is local, but that does not make the browser an offline client. |
| What is tested by the SQLite runner? | The real service and relational provider, using a disposable temporary database, without replacing SQLite with an in-memory mock. |
| Does `dotnet test` run the checks? | No. Both projects are executable runners invoked with `dotnet run`; assertion failures produce a nonzero exit. |
| Are all browser and OS combinations verified? | Only completed runs count. Consult the explicit status matrix in `QA.md`. |
| What limits scalability today? | Whole-atlas snapshots, non-paginated library rendering, SQLite write concurrency, and the local-workspace scope. |
| What would internet deployment require? | Authentication, authorization, HTTPS, operational backups, concurrency controls, and deployment-specific configuration. |
