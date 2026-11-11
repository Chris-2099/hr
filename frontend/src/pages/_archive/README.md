# Archived custom dashboard pages

These 5 pages (Talent Acquisition, Retention, Performance, Engagement,
Compensation) were fully working custom React + Recharts dashboards, live-
wired to the real backend endpoints (`/api/dashboard/*`), built before the
architecture decision to use embedded Power BI reports for these themes
instead (landing page stays custom-built; everything else becomes a Power
BI embed once a semantic model with RLS exists).

Moved here rather than deleted - the backend endpoints these called are
untouched and still fully functional (verify with `curl localhost:8000/api/dashboard/retention`
etc.), so reviving any of these is a matter of moving the file back to
`src/pages/` and re-adding its route in `App.tsx`, not rebuilding it.
