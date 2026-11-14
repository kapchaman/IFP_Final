# Memory Palace — Knowledge Atlas

Course final project for **C# / .NET Cross-Platform Development**.

**Team:** Amirzhanuly Abay and Shikhiyev Alikhan.

Memory Palace is a personal knowledge workspace for students who want to understand how ideas connect. It combines a spatial graph, a searchable concept library, typed relationships, and shortest-path discovery. Data stays in a local SQLite database, with JSON export and restore for portability.

## Prerequisites

- .NET 10 SDK. `global.json` accepts installed .NET 10 feature bands.
- Windows, macOS, or Linux, and a modern browser.
- Internet access to NuGet for the first restore and dependency auditing.
- Node.js and Playwright browsers only when running the browser tests.

## Setup and run

Run these commands from the repository root, alongside `MemoryPalace.sln`:

```sh
dotnet restore MemoryPalace.sln
dotnet build MemoryPalace.sln --no-restore --warnaserror
dotnet run --project MemoryPalace.Web
```

The development profile lists its local addresses in the terminal. Its default HTTP address is **http://localhost:5038**. For HTTPS, trust the development certificate with `dotnet dev-certs https --trust`.

To choose a predictable HTTP address without the development profile:

```sh
dotnet run --project MemoryPalace.Web --no-launch-profile --urls http://localhost:5100
```

SQLite is created automatically at `MemoryPalace.Web/App_Data/memory-palace.db`. No separate database server or manual schema setup is required. Existing databases from the same schema can be reused. Schema changes will require EF Core migrations; `EnsureCreatedAsync` is only responsible for initial creation.

## Feature walkthrough

1. **Create and edit concepts.** Choose **New concept**, enter a title, description, and category, and save. Select a concept on the map or in the library, then choose **Edit** to update it. Titles must contain 2–100 characters, categories 2–40, and descriptions at most 2,000.
2. **Connect ideas.** With at least two concepts present, choose **Connect**. Select a target, a relationship (`Related`, `Explains`, `Supports`, `Contradicts`, or `ExampleOf`), and an optional note of up to 500 characters. Relationships are directed; the reverse direction is a separate relationship.
3. **Search and filter.** Search titles, descriptions, and categories without case sensitivity, including Unicode text. Combine the search with a category filter. The library provides a text-based alternative to the graph.
4. **Discover a path.** Select two concepts under **Discover a connection**. Breadth-first search returns a shortest chain and highlights it. Discovery traverses relationships in either direction while preserving their stored direction and meaning.
5. **Delete safely.** Deleting a concept requires confirmation and removes its incoming and outgoing relationships in one transaction. Individual relationships can also be removed after confirmation.
6. **Back up and restore.** **Export backup** downloads a versioned JSON file. **Restore backup** accepts a valid backup only when the atlas is empty. It does not overwrite an existing workspace. The upload limit is 2 MB, with at most 2,000 concepts and 10,000 relationships.

To explore a prepared example, restore [docs/demo-atlas.json](docs/demo-atlas.json) into an empty atlas. It contains eight concepts and nine relationships. The map displays up to 60 concepts, prioritizing a discovered path; use search, categories, or the full library for larger collections. A path longer than the map limit remains available in the text result.

## Architecture summary

The application uses Blazor Server on .NET 10. Reusable Razor components communicate through parameters and event callbacks. A scoped `AtlasState` holds each browser circuit's selection, filters, and data snapshot. `IConceptService` separates UI workflows from validation and persistence, while `IDbContextFactory` gives every database operation its own short-lived context. EF Core maps the domain model to SQLite. `GraphExplorer` implements BFS independently of the UI and database.

See [the architecture specification](docs/ARCHITECTURE.md) for diagrams, service contracts, consistency rules, and design trade-offs.

## Testing

### Core checks

```sh
dotnet run --project MemoryPalace.CoreChecks
```

This executable runner has no external package dependencies. It checks graph traversal, Unicode search, filtering, and state consistency. Expected final output:

```text
18 core checks passed.
```

### SQLite integration runner

```sh
dotnet run --project MemoryPalace.Tests
```

`MemoryPalace.Tests` is an **executable integration test runner**, not a test-framework project. It exercises the real service against a uniquely named temporary SQLite database and removes that database in a `finally` block. It covers validation, CRUD, directed relationships, transactional deletion, JSON round trips, invalid imports, and concurrent reads. Expected final output:

```text
29 SQLite integration checks passed.
```

Both runners exit unsuccessfully if an assertion fails. Use `dotnet run` for these projects: `dotnet test` does not execute them. See [QA results and the manual test matrix](docs/QA.md) for execution evidence and remaining verification.

### Browser tests

Start a separate test instance at port 5100, then run:

```sh
cd tests/e2e
npm install
npx playwright install
npm test
```

The Playwright configuration includes desktop Chromium, Firefox, WebKit, and a mobile WebKit viewport. Set `ATLAS_URL` to use another address. Tests create uniquely named records and remove them on success; use a test workspace because failed scenarios may leave their records behind.

### Dependency and build checks

```sh
dotnet restore MemoryPalace.sln
dotnet build MemoryPalace.sln --no-restore --warnaserror
dotnet list MemoryPalace.sln package --include-transitive --vulnerable
```

EF Core SQLite is pinned to 10.0.12 and the SQLite native bundle to 3.0.5. The direct bundle reference replaces the older native SQLite dependency associated with `NU1903`. Warnings are not suppressed; the CI build treats them as failures. Package references require a fresh restore before the updated native runtime can be verified.

## Submission materials

- [Architecture and service contracts](docs/ARCHITECTURE.md)
- [All 20 assessment criteria](docs/REQUIREMENTS.md)
- [QA evidence and device checklist](docs/QA.md)
- [Eleven-slide presentation](docs/presentation.html)
- [15–20 minute defense script and Q&A](docs/PRESENTATION.md)

Open `docs/presentation.html` directly in a browser. Use the arrow keys or navigation buttons to move between slides; **Print / PDF** prints the complete deck. Both team names are already entered on the title slide and in the defense script. To change them, edit the title slide's `team-members` element and the team line in `docs/PRESENTATION.md`.

This version is intended for a local personal workspace. It does not provide authentication, separate user-owned datasets, or automatic synchronization across browser tabs. Internet deployment would require access control and HTTPS. For schema evolution, large datasets, or multiple servers, see the development notes in the architecture specification.
