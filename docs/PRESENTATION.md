# Memory Palace — Defense Script

**Course:** C# / .NET Cross-Platform Development
**Team:** Amirzhanuly Abay and Shikhiyev Alikhan
**Format:** 11 slides and a live demonstration, approximately 18–20 minutes.

Open `presentation.html` in a browser. Arrow keys move between slides; **Print / PDF** prints the complete deck. The title slide already contains both names. If either spelling changes, edit its `team-members` element and the team line above. A reusable deck template would use `[Student 1 Full Name]` and `[Student 2 Full Name (Optional)]` in those locations.

Both students should rehearse the whole project, including the database rules and graph algorithm. Assign speaking sections after rehearsal rather than leaving either person unable to explain the other sections.

## Slide 1 — Project and team · 1 minute

“Good afternoon. We are Amirzhanuly Abay and Shikhiyev Alikhan. Our final project is Memory Palace — Knowledge Atlas, a personal knowledge workspace built with C#, .NET 10, and Blazor Server.

The application lets a student capture concepts, describe how they relate, and discover chains between different subjects. The central idea is that knowledge is useful not only as separate notes, but also as relationships that we can inspect and explain.”

Introduce the topic and show the map/library screenshot or the running workspace. State the local personal-workspace scope clearly.

## Slide 2 — Aim and objectives · 1 minute

“Our aim is to make connections between ideas visible and searchable. The intended audience is students organizing material across courses.

The objectives are to implement concept creation, reading, editing, and deletion; typed directed relationships; search and category filtering; persistent local storage; shortest-path discovery; and a portable backup format. We also need a structure that can be tested and explained independently of the interface.”

Use a concrete example: connect breadth-first search to graph theory, then connect both to the application's knowledge map. Explain that educational usefulness is the motivation; the project does not claim a measured improvement in memory or grades.

## Slide 3 — Technology comparison · 2 minutes

“We chose Blazor Server because both UI event handlers and the application service can be written in C#. The server can access EF Core directly, so a separate REST API is unnecessary for this scope.

Blazor WebAssembly would move UI execution into the browser and reduce that part of the server workload. It would also require downloading the browser runtime and designing a separate boundary for database access. Blazor Server instead requires a persistent connection between the browser and server.

SQLite keeps deployment small: one database file and no separate database server. An external relational database would be a better fit for multiple application servers or heavier concurrent writes, but adds deployment and operational work.”

Mention that .NET 10 is the target framework, EF Core handles relational mapping, and HTML/CSS/SVG provide the interface without a separate graph-rendering framework. Discuss actual trade-offs rather than claiming that one technology is universally best.

## Slide 4 — Existing approaches and relevance · 1 minute

“Ordinary notes and wiki pages work well for longer documents. They can contain links, but a typed relationship such as ‘supports’ or ‘contradicts’ needs explicit organization. General graph systems offer more powerful query capabilities, with a larger setup and learning cost.

Our project focuses on a smaller problem: concise concepts, a limited set of meaningful relationship types, and a path between ideas. The graph supports exploration, while the library gives a straightforward alternative for searching and editing.”

Keep the comparison at the approach level. Do not claim to replace every feature of a full note-taking or graph-database product.

## Slide 5 — Methodology, plan, and interface mockup · 1 minute

“We worked through the project in increments: inspect the requirements and starting structure, establish data integrity, complete the user workflows, split the interface into reusable components, and add tests and submission materials.

The layout follows the main workflow. Navigation switches between the map and library. The top section shows actions and statistics. The central area supports exploration; the right panel explains the selected idea. Search and categories narrow the workspace, and the path controls help connect two areas of knowledge.”

Point to the mockup. Explain why details remain beside the graph rather than requiring a separate navigation step.

## Slide 6 — Architecture and state · 2 minutes

“The browser communicates with a Blazor Server circuit. `Index` coordinates user actions and feedback. `AtlasState` holds a snapshot of the concepts, the current selection, and filters. Components depend on `IConceptService`, while `ConceptService` owns validation, persistence, and backup workflows.

State is scoped to a circuit, so another browser tab has its own selection and search. Database data is shared. A refresh explicitly loads changes made elsewhere.

A key design choice is `IDbContextFactory`. A Blazor circuit can outlive an HTTP request, and event handlers can overlap. A shared context would be unsafe because EF Core contexts are not thread-safe. Each operation therefore creates and disposes its own context.”

Show the pipeline and identify one component using each mechanism: `KnowledgeGraph` parameters, editor save callbacks, and `ConceptDetails` cascading state. Explain that this is a layered application within one project, not a claim of distributed services.

## Slide 7 — Data integrity and error handling · 1.5 minutes

“A concept contains its text, category, identifier, and timestamps. A relationship contains a source, target, type, and optional note. A unique database index protects the ordered endpoint pair. A to B and B to A are different relationships; a concept cannot connect to itself.

Deletion removes both incoming and outgoing relationships before deleting the concept, within the same transaction. This is necessary because the target foreign key restricts deletion.

Backup restore validates the entire record set first. It rejects duplicate titles, invalid IDs, broken endpoints, undefined relation types, and incompatible versions. It then writes the data in one transaction, only into an empty atlas.”

Explain that field-length and normalized title rules are enforced in the service. Unexpected errors are logged; the user receives a concise recovery message. Do not claim that SQLite automatically enforces EF length metadata.

## Slide 8 — Live demonstration · 4 minutes

Prepare a separate empty demonstration workspace before the defense. Keep personal data backed up; do not delete it just to reset a demonstration.

1. **Restore the example.** Import `docs/demo-atlas.json`. Point out eight concepts and nine relationships.
2. **Inspect an idea.** Select **Breadth-First Search** and show its relationship to **Graph Theory** and **Memory Palace**, including direction and note.
3. **Create and edit.** Add **Learning Journal**, category **Learning**, with a brief description. Change the description using **Edit**.
4. **Create a relationship.** Connect **Learning Journal** to **Active Recall** using **Supports** and a short explanatory note.
5. **Discover a chain.** Find a path from **Spaced Repetition** to **SQLite**. Read the result and explain why discovery may traverse a stored relationship backwards.
6. **Switch views.** Search for a title or category, open the library, and show the empty-result recovery by clearing filters.
7. **Export and delete.** Download a JSON backup. Cancel a deletion once, then confirm deletion of **Learning Journal**. Show that the other concepts remain and no dangling relationship is displayed.
8. **Check persistence.** Reload the page and select a remaining concept in the library.

If time is short, retain steps 1, 3, 4, 5, and 7. If the server connection fails, use the architecture slide and explain the recovery action rather than presenting the failure as successful execution.

## Slide 9 — BFS and complexity · 1.5 minutes

“The path finder builds an adjacency list and uses a queue. Starting from the source, it visits neighbors layer by layer. A predecessor table records how each vertex was reached and also marks it as visited. When the destination is reached, we reconstruct the path through those predecessors.

Because each vertex and edge is processed a bounded number of times, time complexity is O(V + E). The adjacency list, queue, and predecessor table also use O(V + E) space. A visited set prevents cycles from creating an infinite loop.

All relationships have equal traversal cost. That is why BFS finds a shortest chain. Weighted relationships would need an algorithm such as Dijkstra's.”

Discuss practical limits: at most 60 graph nodes are rendered, with path nodes prioritized; the full text result and library remain available. Database reads use no tracking, and filters/statistics are derived from the current snapshot.

## Slide 10 — Quality assurance · 1.5 minutes

“We have two executable assertion runners. The first checks the graph algorithm and state behavior. The second uses the actual service against a temporary SQLite database, covering validation, CRUD, relationships, deletion integrity, backups, and concurrent reads.

The recorded run passed 18 core assertions and 29 SQLite assertions, for a total of 47. These counts are not a code-coverage percentage. Browser scenarios and a manual device matrix are documented separately.”

Use the current `QA.md` as the source of truth. The recorded SQLite run used cached baseline packages; the dependency references have since been updated to remove the vulnerable native SQLite dependency. Until the final restore, audit, warning-free build, and rerun are completed, state that qualification is pending. Browser/device checks must also be reported according to their actual execution status.

After a successful final verification, update this slide's QA wording and `QA.md` together. Do not describe configured CI jobs as observed passing runs.

## Slide 11 — Limitations and next steps · 1 minute

“The current application is a local personal workspace. It does not yet include authentication, per-user ownership, automatic synchronization across tabs, or optimistic concurrency tokens. Concurrent edits follow a last-successful-write policy.

The next steps would be authentication and ownership, migration-based schema evolution, concurrency handling, server-side search and pagination, and support for larger graphs. The current service boundary and separate graph algorithm give those changes clear places in the design.”

Invite questions and keep the application and architecture document available.

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
