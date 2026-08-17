# AGENTS.md

## Project overview

PAM ("Personal Assistant Manager") is a personal, single-user "Life OS" dashboard built with Django. Owner/user: Jonas Ampferl. It's meant to consolidate calendar, tasks, contacts, health data, and notes in one place.

## Stack & structure

- Django 6.0, SQLite (`db.sqlite3`, gitignored), `python-dotenv` for env vars (`.env`, gitignored).
- All frontend assets are vendored locally under `static/` — Bootstrap 5 + Bootstrap Icons, Font Awesome, Chart.js, EasyMDE. No npm, no CDN, no build step.
- Django apps: `core` (shared dashboard + calendar-source registry), `account` (auth/settings), `planner` (calendar, events, contacts, tasks), `health` (Garmin sync), `knowledgebase` (notes).
- Garmin integration reads `GARMIN_EMAIL` / `GARMIN_PASSWORD` from `.env`; token cache lives in `.garmin_tokens/` (gitignored). See `health/client/garmin.py` and `health/sync.py`.

## Conventions (established across this project — follow unless told otherwise)

- **Minimal new CSS/JS.** Reuse existing Bootstrap utilities and already-loaded static assets before adding anything new. Prefer inline attribute handlers (`onchange="this.form.submit()"`, `onclick="return confirm(...)"`, `data-bs-toggle="collapse"`) over new `<script>` blocks or files.
- **UI text is German** throughout (labels, buttons, headings) — keep new UI strings German too. Conversation with the user happens in a mix of German and English; mirror whichever language their message is in.
- **Templates**: `app/templates/app/*.html`, extending `dashboard.html` → `base.html`. Recursive partials (subtasks, folder trees, etc.) live in `app/templates/app/partials/` — note `knowledgebase` inconsistently put its partial at the top-level `templates/partials/` instead; don't copy that, namespace under the app.
- **Model conventions**: German `verbose_name`/`verbose_name_plural` in `Meta`, sensible default `ordering`, a `__str__`.
- **Cross-app calendar integration**: any date-scoped feature should register a `CalendarSource` in the app's own `calendar_sources.py` (see `core/calendar_sources.py` for the `CalendarItem`/`CalendarSource` contract — note `CalendarItem` has both a required field list AND a `__post_init__`, both must be kept in sync when adding a field) and hook it up via the app's `AppConfig.ready()`. This is the single registry the Planner calendar, dashboard widgets, and ICS feed all read from — don't build a parallel path.
- **Reuse existing generic models before inventing new ones** — e.g. shopping lists should be a `planner.TaskList`, not a new model.
- **Migrations**: I don't run `makemigrations`/`migrate` myself — always tell the user to run them after a model change.

## User workflow preference (stated explicitly this session)

- The user asked, for the whole session: **do not edit/write files directly — give code as text/diffs and let them apply it themselves.** At the start of a new session, confirm with them whether this still applies before using Edit/Write on application code. (A caught bug this habit already exposed: a partial paste once left a dataclass with `__post_init__` referencing a field that hadn't actually been added — double-check the *whole* diff landed, not just skim it.)

## Current implemented state (as of 2026-08-17)

- **Planner**: month/week/day calendar. Multi-day events render across every day they span (`CalendarItem.end_date`), continuation styling via Bootstrap's `rounded-*-0` utilities + chevron icons. Overlapping events in week/day view pack into side-by-side columns (`_layout_day_events` in `planner/views.py`), with a fixed 16px left gutter always reserved so you can still click to create a new event. Events + Categories, Contacts, ICS export secured via a per-user token (`account.CalendarFeedToken`, copyable + regeneratable from Settings). Tasks: `TaskList` → `TaskGroup` → `Task` with unlimited subtask nesting, due dates on all three levels feeding the calendar via `TaskSource`, and a static `PINNED_TASKLIST_IDS` set in `planner/utils.py` for always-surfacing a list's open tasks on the dashboard regardless of due date (deliberately static for now — a real "pinned" field is future work).
- **Health**: Garmin sync (`health/sync.py`, `health/client/garmin.py`) — manual "Sync" button only, no scheduled job. `DailyStats` + `Activity` models, dashboard with a 7-day steps chart. Both models registered in Django admin.
- **Knowledge Base**: full folder-tree notes app (drag-and-drop move, inline rename, autosave) — considered feature-complete.
- **Account**: login/logout, Settings page — only the ICS feed section is real; profile/notification/theme fields are still a static mockup.
- **Core dashboard** (`core/index.html`): "Heutige Aufgaben" (unified TaskList/TaskGroup/Task due-today + pinned-list view, checkbox toggles redirect back via `HTTP_REFERER` so you stay on the dashboard), "Nächste Termine", "Letzte Aktivitäten", "Offene Aufgaben" and "Events diese Woche" stat cards are all real. "Trainings absolviert" and "Wasser" stat cards, and the "Habit Tracker" card, are still hardcoded fakes.

## Known gaps / not yet done

- No root `/` URL redirect — still 404s, must land on `/core/` or `/account/login` directly.
- `core/management_view` is an explicit fake PoC (non-persisted feature toggles).
- `health/templates/health/trainingsplan.html` is a dead duplicate of content already inlined in `health/index.html` (superseded by the planned real training-plan model, see below).
- No automated tests anywhere in the project.
- Navbar global search box and "+Neu" quick-add dropdown (`templates/base/navbar.html`) are still commented-out HTML stubs.
- No scheduled/periodic Garmin sync (no cron/Celery — manual button only).

## Planned direction (discussed, not yet built)

Big next area the user wants to explore: an interconnected Health/Fitness/Nutrition system. Proposed structure from our planning discussion:

- **New `nutrition` app**: `Ingredient`, `Recipe`, `RecipeIngredient` (through-table), `CookingSession` (batch cooking/meal-prep, tracks portions made), `PlannedMeal` (meal plan + food log in one — references a `CookingSession` or `Recipe`, or is a manual entry for ad-hoc food). Shopping lists should be generated as a `planner.TaskList` (one `Task` per ingredient), not a new model.
- **New `habits` app** (or fold into `health`): `Habit` + `HabitCheckIn`, streaks computed on the fly, not stored. Deliberately NOT a calendar source — recurring daily state, not a date-scoped event; belongs on the dashboard + its own page instead.
- **Extend `health`**: `PlannedWorkout` (training plan, optionally linked to a synced `Activity` for planned-vs-actual comparison), extra `Activity`/`DailyStats` fields pulled from Garmin (HR zones, elevation, training effect, stress, body battery, HRV, VO2max, SpO2 — verify exact field availability against the `garminconnect` library before committing to names), and a generic `BiomarkerReading` (metric_key/value/unit/date/source) time-series model for anything not auto-synced (lab panels, grip strength, etc.) — chosen over rigid columns because the longevity-metric list will keep growing and shouldn't require a migration every time.
- "Longevity Analysis" = an analysis/trend view over the above data, not new input models. Avoid inventing a made-up composite score; prefer per-metric rolling-average trend lines.
- Open questions still unresolved (ask the user before modeling further): external food-database integration for ingredient nutrition vs. manual entry only; fixed meal slots (breakfast/lunch/dinner/snack) vs. freeform timed slots like calendar events; whether "planned" and "eaten" meals should be one model or two; whether habits need quantities (e.g. "drink 2L water") rather than just done/not-done.

## Planned: Documents app (discussed, not yet built)

Replaces the "Dokumente" sidebar stub (currently `javascript:alert('Not implemented yet.')` in `templates/base/links.html`). Purpose: manage digitized documents (scans/PDFs) — payslips, insurance papers, certificates, etc. Requirements gathered from the user:

- **Folders**: `DocumentFolder`, self-referential tree for categories (Arbeit, Versicherungen, Zertifikate, ...) — same parent/child pattern as `knowledgebase.KnowledgeItem`.
- **Archiving**: `Document.is_archived` (and by extension a folder's contents), same boolean-flag pattern already used for `planner.TaskList.is_archived`.
- **Search**: by title, category, and description via normal DB filtering — plus the user explicitly wants full-text search *inside* PDF content. Since SQLite has no real full-text search, the pragmatic approach is to extract text at upload time (e.g. via `pypdf`/`pdfplumber`) into a stored `content_text` field and run `icontains` over that, rather than searching the binary file itself.
- **Deadlines**: a `Document` needs an optional due datetime ("submit file X until Y"). Should feed the calendar via a `DocumentSource`, same `core.calendar_sources` registry pattern as Events/Tasks/Meals — not a separate reminder mechanism.
- **Recurring-document grouping**: e.g. every month's Lohnzettel (payslip) — opening any one should show all of them "in order". Simplest fit: a `series_key` (or a lightweight `DocumentSeries` FK) on `Document`, listing same-series documents in date order. This is a narrower, more common case than freeform relations and shouldn't need the general mechanism below.
- **Freeform relations between documents**: beyond series grouping, the user also wants to be able to link arbitrary documents to each other — likely a self-referential `related_documents = ManyToManyField('self')` on `Document`.
- **Cross-app linking**: other apps (Contacts, Tasks, Events, Knowledge Base) should be able to link to a specific `Document`. Open design decision, worth resolving once the `Document` model exists rather than upfront: Django's `contenttypes`/`GenericForeignKey` for one reusable "link to a document from anywhere" mechanism, vs. plain FK fields added ad-hoc per app as the actual need arises (simpler, less magic, but not centralized).

## Planned: Knowledge Base enhancements (discussed, low priority)

The user explicitly deprioritized this: "not enough usecases for this currently, put at the end of my priorities." Capture the ideas, but don't build unprompted.

- **Wikilink-style linking between notes** (Obsidian-style `[[...]]`), which needs each file-type `KnowledgeItem` to have a stable identifier to link to.
- **Backlinks**: see which notes reference the current one. Likely needs a dedicated `NoteLink` model (from_note FK, to_note FK) populated by scanning `content` for the link syntax on save, rather than scanning all notes on every page load.
- **Automatic backlink refactoring on rename** (like Obsidian): this is in tension with the point above — if links are ID-based (`[[42]]`) they never break on rename and there's nothing to "refactor," only a title-to-display resolution needed at render time; if links are name-based (`[[Note Title]]`, like Obsidian actually does it) then renaming a note requires rewriting the link text inside every OTHER note's `content` that references it. **Decide which model (ID-based vs. name-based links) before building this** — they imply different mechanisms, not just an implementation detail.
- **Export**: a button to export one file, a folder, or everything — single file as plain markdown/text, anything bigger as a `.zip` (Python's built-in `zipfile`, no new dependency needed), preserving folder structure.
- **Assets (e.g. images)**: must be uploaded as real media files, NOT stored as DB blobs. Note this requires `MEDIA_ROOT`/`MEDIA_URL` to be configured in `pam/settings.py`, which isn't set up yet anywhere in the project — this is also a prerequisite for the planned Documents app's file uploads, so it's worth setting up once for both. EasyMDE itself already renders standard markdown image syntax fine once there's a working upload endpoint returning a media URL to insert.
- **Journaling — undecided placement**: the user is unsure whether daily journal entries belong inside Knowledge Base or deserve their own app, specifically because a separate app might interlink more naturally with Habits and other goals (see the `habits` app under "Planned direction" above). Don't assume either way — ask before modeling.

## Planned: additional features (greenlit 2026-08-17)

The user picked these from a brainstormed batch — greenlit as future direction, not scheduled/scoped yet.

- **Quick Capture / Inbox**: a single fast "dump anything here" box (dashboard-level), triaged later into a Task, Event, or Knowledge Base note. Solves "let me jot this down without deciding where it goes right now."
- **Finance & budget tracking**: called "very important." Worth researching before modeling: whether **Finanzguru** (German personal finance/banking-aggregation app) exposes a usable API for auto-importing transactions instead of manual entry — not confirmed yet, needs investigation first.
- **Travel planner**: endorsed, but the user was explicit that it needs to be a *deep integration* of existing `planner.TaskList` (packing lists) and `planner.Event`/calendar (itinerary) rather than a shallow bolt-on feature with its own parallel data model.
- **PWA/offline support**: installable on the phone home screen, works offline at least for viewing.
- **Multi-factor authentication (MFA)**: the user is a security researcher professionally, so this was an easy yes. Current login (`account.login_view`) is plain username/password with no MFA at all — this is a real gap to close, not just a nice-to-have.
- **Home Assistant integration**: pull smart-home data (sensors, device/presence state) into PAM. Natural shape: a new client + sync module mirroring the existing Garmin pattern (`health/client/garmin.py` / `health/sync.py` — poll on demand, `update_or_create` for idempotent syncing), rather than inventing a new integration style.
- **Household todo list**: a shared task list scoped to household chores/errands, distinct from personal Tasklists. This is effectively a concrete instance of the "shared to-do lists" use case already described under Multi-user/family sharing below — likely blocked on that sharing/ownership layer rather than buildable standalone.

### Multi-user / family sharing — flagged as important for the future

Concrete use cases the user gave: their girlfriend should be able to see **specific** calendar events (not the whole calendar), a shared shopping list, a shared budget-splitting list, and specific shared to-do lists.

Implications worth internalizing before scoping this:
- This is **selective per-item sharing**, not "just add another Django user" — need a permission/sharing layer (which specific `Event`/`TaskList`/budget entries are visible or editable by which other user), not account-wide blanket access.
- Most models (`Event`, `TaskList`, `Contact`, etc.) don't currently have an owner/`user` FK at all, since the whole app assumes a single implicit user. Retrofitting ownership onto existing models is a likely prerequisite *before* a sharing layer can be built on top.
- Budget-splitting implies the not-yet-built Finance feature needs multi-party awareness (who owes whom) baked in from the start, not added after the fact.
- This is a bigger structural/architectural change than everything else on this list — treat it as its own project phase, not a quick add-on.

### Considered and declined

- **Reading/watching list**: pitched, but the user decided a dedicated `planner.TaskList` (e.g. "Bücher lesen") already covers this well enough — not planned as its own feature.

## Other feature ideas discussed (not committed to)

Contact interaction log with "reach out" reminders, data export/backup, a daily journal (distinct from Knowledge Base's wiki style), vehicle/asset maintenance tracker, recurring events/tasks, a real notification/reminder system (ties into the currently-fake Account notification toggles), drag-and-drop event rescheduling in the calendar, home/asset inventory & warranty tracker, year-in-review/insights dashboard.
