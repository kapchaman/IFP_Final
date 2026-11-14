# Submission checklist

## What to submit

Submit one ZIP of the **contents of the repository root** (the directory containing `MemoryPalace.sln`), or submit the GitHub URL for the updated `main` branch if the course platform accepts repositories. Keep the project structure intact so the solution and relative file paths work.

The submission should contain:

- `MemoryPalace.sln`, `global.json`, `.gitignore`, and `README.md`.
- `MemoryPalace.Web/` with the application source, static assets, and project file.
- `MemoryPalace.CoreChecks/`, `MemoryPalace.Tests/`, and `tests/e2e/` with their test sources and configuration.
- `docs/` with the architecture, requirements matrix, QA report, demo backup, presentation, and defense script.
- `.github/workflows/checks.yml` so the cross-platform build and checks can be inspected.

Do **not** include generated `bin/`, `obj/`, `node_modules/`, Playwright report directories, or the local SQLite database in `MemoryPalace.Web/App_Data/`. The database is created automatically when the app starts; `docs/demo-atlas.json` is the portable sample data file.

Do not submit `Final Requirements CSh.docx` as if it were a project artifact unless the instructor or submission portal explicitly requests the assignment sheet. It is the rubric used to evaluate this work.

## Before upload

- [ ] Confirm the instructor accepts .NET 10. The rubric does not set a .NET version, but the earlier project context specified .NET 6; this project currently targets .NET 10 and EF Core 10.
- [ ] On a machine with NuGet access, run the restore, warning-as-error build, vulnerable-package audit, and both assertion runners listed in `QA.md`.
- [ ] Run the Playwright scenarios and complete the manual browser/device checklist in `QA.md`; record only environments actually checked.
- [ ] Open `docs/presentation.html`, verify the team members' full names and the demo, then export the slides to PDF if the portal asks for a separate presentation file.
- [ ] Rehearse the required 15–20 minute defense with both team members. The assignment sheet says the defense is obligatory and either student may be asked about any part of the project.

## Presentation coverage

The HTML deck and defense script cover the team, topic, aim and objectives, project plan, comparison of technology choices, architecture, practical relevance, methodology, and interface mockup. The defense script also includes the live-demo flow and likely technical questions. Submit the HTML deck and script with the source; provide a PDF export only if a separate slide file is required.
