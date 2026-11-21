# AI work log

## 2026-11-21 — Blueprint v1
- Read GARNET.zip static source tree, routing, models, settings, key views, requirements, README.
- Created versioned project development documents without modifying application source.
- Runtime tests, dependency installation, browser checks, penetration tests and performance benchmarking **not performed**.

## 2026-11-21 — Prerequisite evidence

- GNT-000: inventoried both supplied GDCS ZIPs and checked archive integrity. No live environment file, database, or key/export file appeared in their inventories. The historical archive and upstream Git history were unavailable. Track historical exposure verification in GNT-005, and rotate credentials if exposure is confirmed. Keep deploy secrets in host environment variables or an untracked local environment file. Share source-only packages and inspect their inventory before sending.
- GNT-001: on local Django 5.2.6/SQLite, the complete ZIP passed system checks, migrations through 0016, and production-mode collectstatic. The dry-run migration check reports five existing model-state differences. Chromium returned HTTP 200 for 48 baseline and 60 populated visual-audit combinations across FA/EN with zero measured document overflow.
- GNT-003: inspected computed styles, templates, and Chromium captures at 320, 390, 768, 1020, 1024, and 1440 px. P1 findings include white navigation on light backgrounds, near-10px CTA type, undersized touch controls, hard-coded directions, and 2.17:1 newsletter icon contrast. About and project grid redesign remain outside Phase 2. Local fixtures represent media and CMS content.

## 2026-11-21 — GNT-008 · Phase 2

- Adopted the approved monochrome palette and a shared typography, spacing, container, control and motion scale. Existing SiteTheme custom colors stay supported. Legacy decoration settings are retained for rollback and are inactive in the shared UI.
- Implemented a borderless glass header, bilingual keyboard navigation, visible focus, accessible shared controls, and basic responsive footer and newsletter contrast corrections.
- Verified Home, Projects, Project Detail, Blog and Article with Chromium and local fixture content in FA/EN at 320, 390, 768, 1024 and 1440px. All 50 combinations returned HTTP 200 with no measured horizontal document overflow. Keyboard skip link, menu/submenu, Escape/focus restoration, menu routes, CTA sizing, nested button text color and absence of button shadow were checked.
- The sampled default header contrast was at least 8.88:1 on forced black/white backgrounds, including before/after scroll on mobile and desktop. The default newsletter icon contrast is 18.42:1. Before/after captures were made with local fixtures.
- Both languages passed client-side consultation validation and test submission. Newsletter registration and duplicate handling passed, with one row per test email. Django system checks, collectstatic, Python AST, JavaScript syntax, SiteTheme override checks and git diff --check passed.
- No migration was added. The migration dry-run still reports the five baseline field differences recorded under GNT-001. Production media and live custom colors were unavailable for verification. Dedicated footer work is GNT-009.

## 2026-11-21 — GNT-009 · Shared header and footer refinement

- Made the shared header a full-width borderless glass strip. It uses dark glass over the home and project Heroes before scroll, light glass on other pages, and the configured logo variants. Desktop shows inline navigation and language switching. The existing mobile menu remains available at narrower widths.
- Rebuilt the dark footer around the reference layout with brand, purchase, quick links, company information, contact, newsletter and configured social links. Kept the existing purchase flow through the shared request form and omitted the WhatsApp/consultation CTA. Brand and contact values come from SiteSettings.
- Verified 50 Chromium combinations across home, project list, project detail, blog list and article at 320, 390, 768, 1024 and 1440px in FA and EN. Checked no horizontal overflow, shared grid alignment, menu/focus and footer links. Minimum measured header contrast was 7.94:1 on the local bright/dark test. Verified purchase and newsletter submissions and persisted rows in both languages. Captured desktop and mobile views with fixture content.
- Django system checks, collectstatic, GDCS and Git whitespace checks passed. Production settings, logo files and CSS overrides were unavailable locally. No migration is required for this change.
