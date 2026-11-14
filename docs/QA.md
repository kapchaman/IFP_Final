# Quality Assurance Report

## Automated execution results

**Environment:** macOS arm64, .NET SDK 10.0.401.
**Validation date:** 14 November 2026.

Both executable runners were run successfully in this workspace:

| Runner | Result | Final console output |
|---|---:|---|
| `MemoryPalace.CoreChecks` | 18 passed | `18 core checks passed.` |
| `MemoryPalace.Tests` | 29 passed | `29 SQLite integration checks passed.` |
| **Total** | **47 passed** | No failed assertions |

The SQLite runner uses the actual `ConceptService`, EF Core, and a temporary SQLite database rather than a mocked database provider. Its cleanup executes in a `finally` block. The core runner links the domain, graph, service interface, and state sources directly and has no external package dependencies. These are executable assertion runners; `dotnet test` does not execute them, and 47 passing assertions do not imply a particular line-coverage percentage.

### Dependency qualification

The passing SQLite run used the locally cached baseline: EF Core SQLite 10.0.0 and SQLitePCLRaw 2.1.11. It exposed warning `NU1903` for the native SQLite dependency. The project references have since been updated to **EF Core SQLite 10.0.12** and **SQLitePCLRaw.bundle_e_sqlite3 3.0.5**. No warning has been suppressed.

A fresh restore, vulnerability audit, warning-free build, and repeat SQLite run are required to qualify the updated dependency graph. This session cannot resolve `api.nuget.org`, so these final package checks are **pending**. The 47 passing results above remain valid evidence for the tested baseline; they are not evidence that the new native package was downloaded or executed.

```sh
dotnet restore MemoryPalace.sln
dotnet build MemoryPalace.sln --no-restore --warnaserror
dotnet run --project MemoryPalace.CoreChecks --no-build
dotnet run --project MemoryPalace.Tests --no-build
dotnet list MemoryPalace.sln package --include-transitive --vulnerable
```

CI performs restore, a warning-as-error build, and both runners on Windows, macOS, and Linux. Its configuration is checked in; remote CI results have not been observed in this session.

## Core checks: 18 passing assertions

| # | Assertion |
|---|---|
| 1 | A shorter path wins over a longer route in a cyclic graph |
| 2 | Relationships can be traversed backwards for discovery |
| 3 | Equal source and destination produce a zero-step path |
| 4 | A disconnected graph terminates with no path |
| 5 | A missing source returns no path |
| 6 | A missing destination returns no path |
| 7 | An empty graph returns no path |
| 8 | A dangling edge is ignored |
| 9 | State derives global concept, category, and edge counts |
| 10 | A reload notifies subscribers once |
| 11 | Cyrillic title search is case-insensitive |
| 12 | Description search works |
| 13 | Category text search works |
| 14 | Search and category filtering intersect |
| 15 | Search terms are trimmed |
| 16 | Reload preserves valid selections and filters |
| 17 | Reload clears a removed selection and category |
| 18 | Reload recomputes the edge count |

## SQLite checks: 29 passing assertions

| # | Assertion |
|---|---|
| 1 | Concept input is trimmed |
| 2 | Unicode duplicate titles are rejected |
| 3 | Short titles are rejected |
| 4 | Overlong titles are rejected |
| 5 | Overlong descriptions are rejected |
| 6 | Blank categories are rejected |
| 7 | Updates preserve creation time and update the content/timestamp |
| 8 | Editing to a duplicate title is rejected |
| 9 | Editing a missing concept is rejected |
| 10 | Atlas queries load outgoing graph edges |
| 11 | Detail queries load both directions and endpoint titles |
| 12 | Relationship notes are trimmed |
| 13 | Self-connections are rejected |
| 14 | Missing relationship endpoints are rejected |
| 15 | Duplicate directed pairs are rejected |
| 16 | Undefined relationship enum values are rejected |
| 17 | Overlong relationship notes are rejected |
| 18 | Service search supports Cyrillic case folding |
| 19 | Restore refuses a nonempty atlas |
| 20 | Deleting a connected concept succeeds |
| 21 | Deletion removes incoming and outgoing edges |
| 22 | Repeating deletion of an absent concept is harmless |
| 23 | Malformed backup JSON is rejected |
| 24 | Unsupported backup versions are rejected |
| 25 | Backup relationships with dangling endpoints are rejected |
| 26 | Failed import leaves the database empty |
| 27 | A backup round trip preserves IDs and relationships |
| 28 | Disconnecting preserves the concepts |
| 29 | Concurrent reads succeed with separate contexts |

## Browser automation

Playwright scenarios cover creating concepts, creating a typed relationship with a note, discovering a path, editing, reloading persistent data, navigating the library, deleting a connected concept, checking remaining integrity, and cleaning up. A second scenario checks Escape dismissal and horizontal overflow. The configuration targets Chromium, Firefox, WebKit, and a mobile WebKit viewport.

**Execution status: not run in this session.** Browser automation is separate from the 47 passing .NET assertions. Follow the README commands with a separate test instance at `http://localhost:5100`.

## Manual test matrix

All entries below are pending unless a result is added after execution.

| Area | Procedure | Expected result | Status |
|---|---|---|---|
| Initial setup | Start with an empty database | Schema is created; the empty workspace offers concept creation | Pending |
| Existing data | Start with an existing database of the same schema | Data loads without modification | Pending |
| Demo restore | Restore `demo-atlas.json` into an empty atlas | Eight concepts and nine relationships | Pending |
| Concept forms | Submit blank, boundary-length, duplicate, and valid fields | Clear validation; valid data persists | Pending |
| Editing | Edit title/category/description and reload | New values persist; creation date remains unchanged | Pending |
| Relationships | Add reverse, duplicate, missing-endpoint, and self relationships | Reverse pair allowed; invalid operations rejected | Pending |
| Deletion | Cancel, then confirm deletion of a linked concept | Cancel changes nothing; confirm removes incident edges | Pending |
| Search | Search Unicode text and combine with categories | Case-insensitive matches and clear empty-result recovery | Pending |
| Path discovery | Try connected, disconnected, cyclic, and same-node cases | Shortest chain, no-path feedback, or zero-step result | Pending |
| Backup | Export, restore into an empty test atlas, compare data | IDs, metadata, notes, and relationship types retained | Pending |
| Invalid upload | Choose malformed JSON, an incompatible backup, and a file over 2 MB | Actionable feedback; no partial data | Pending |
| Persistence | Restart the application after changes | Saved records remain available | Pending |
| Separate tabs | Write in one tab, refresh another | Snapshot updates; each tab keeps its own filters | Pending |
| Keyboard | Use Tab, Shift+Tab, Enter, Space, and Escape | Controls usable; dialog focus remains contained | Pending |
| Assistive technology | Inspect labels, status announcements, and graph alternatives | Meaningful names and usable library view | Pending |
| Disconnection | Interrupt and restore browser/server connectivity | Reconnection or reload provides a clear recovery path | Pending |
| Larger atlas | Load over 60 concepts and discover paths | Bounded map; full search/library and text result | Pending |

## Platform and device checklist

- [ ] Windows: restore, build, both runners, and browser walkthrough.
- [ ] macOS: browser walkthrough; repeat package qualification after the dependency update.
- [ ] Linux: restore, build, both runners, and browser walkthrough.
- [ ] Desktop Chromium, Firefox, and Safari/WebKit.
- [ ] Viewports at 375, 768, and 1440 pixels, portrait and landscape.
- [ ] Physical Android phone and iPhone where available.
- [ ] Browser zoom at 200%; no clipped actions or horizontal page overflow.
- [ ] Reduced-motion setting and keyboard-only navigation.

For each defect, record the environment, reproduction steps, expected behavior, observed behavior, fix, and retest result. Do not mark a platform as passed solely because it appears in the CI or Playwright configuration.
