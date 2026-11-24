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

## 2026-11-21 — GNT-010 · Header, home, project and footer corrections

- Use the same light glass header over all pages. Scrolling increases glass opacity by three percentage points while slightly reducing the configured tint. Existing dark header tints are mixed into a light base. The desktop and mobile menus align with their respective triggers, stay inside the viewport, and reset on dismissal or layout change. The language switch moved to the footer.
- Use a 10px control radius and remove decorative borders from home cards and actions without removing keyboard focus indicators. Project actions fit their label and use a direction-aware arrow. Project status keeps only the value, with the generic label and legacy decorative dots removed.
- Render the footer wordmark in white using the logo alpha channel. Increase the social SVGs to 28px and give newsletter submission a dedicated contrast-safe button.
- Verified 70 local Chromium page/language/viewport combinations and pointer, touch and keyboard navigation. Also verified menus in a short viewport and during desktop/mobile resizing. Tested against sample legacy theme color overrides and fixture media. Minimum measured header contrast was 5.79:1, and newsletter control contrast was 14.16:1. Purchase and newsletter submissions and their saved rows were verified in both languages.
- Django system checks, collectstatic, JS syntax and GDCS checks passed. Production branding assets and separately configured custom CSS were unavailable. No schema migration.

## 2026-11-21 — GNT-011 · Transparent header, mobile menu and component alignment

- Keep the header transparent at the top. Scrolling reveals one full-width tinted glass overlay. The content wrapper stays transparent. Replace old wrapper/action selectors that could retain the opaque center or a decorative dot from site custom CSS.
- Use a native details/summary disclosure for the mobile menu. JavaScript enhances dismissal, focus restoration and nested menus. Keep desktop dropdown navigation and existing form routes.
- Use 12px button radii. Size project actions to their text and icon with 10px horizontal padding. Keep the entire project card clickable.
- Align the white wordmark to the inline start of the footer grid. Compensate for transparent padding in same-origin logo assets without changing their files.
- Verified 70 local Chromium page combinations, 12 touch scenarios in FA/EN with JavaScript enabled or disabled, desktop keyboard navigation, and both form submissions. Under fixture CSS simulating the old white wrapper and dot, the scrolled strip measured the same pixel value across six horizontal samples. The transparent padded logo reached the grid boundary at the sampled desktop sizes. Minimum tested nav contrast over black was 4.92:1.
- Django check, collectstatic, JS syntax, GDCS and Git whitespace checks passed. These tests use local fixture settings and media. No schema migration.

## 2026-11-21 — GNT-012 · Brand alignment and home project widths

- Put the logo on the left and purchase controls on the right in both languages. Keep navigation in the current language direction, preserve the glass strip and anchor the mobile menu on the right.
- Align the visible footer wordmark above the tagline, on the right in Persian. Calculate the horizontal alpha padding in the template and cache the result. Set the homepage card widths in both carousel modes, including the existing swipeable responsive fallback. Cards measured 232px at 390px and 290px at 1440px.
- Add editable bilingual heading and button labels and independent footer purchase colors through the existing admin. Migration `0017` adds six fields with the previous public labels as defaults. Migration dry-run still reports the five unrelated baseline field differences recorded under GNT-001.
- Chromium passed 90 page/language/viewport combinations and 14 carousel-off combinations. Touch menu operation, desktop keyboard navigation and focus, footer wordmark alignment with and without JavaScript, and purchase and newsletter submissions were verified in both languages. Admin form saves and browser-rendered settings were checked with fixture content and colors. Production assets and settings remain unverified.
- Django system checks, production-mode collectstatic, JavaScript syntax, GDCS and Git whitespace checks passed. Migration from 0016 applied on the local fixture database.

## 2026-11-22 — GNT-013 · Homepage presentation and compact footer

- Render a viewport-height, centered hero followed immediately by About. Use one theme color at the seam. Read video, poster, hero text and links from the existing Hero section. Keep the poster in reduced-motion and failure states.
- Show an editable all-projects label with a directional arrow. Use square default corners and a separate radius control for homepage previews. Keep the carousel and static fallback.
- Hide the Journal link from desktop and mobile headers by default through SiteSettings. Keep editable menu order and labels, submenus, and existing Journal entry points outside the header.
- Compact the four footer groups and keep both forms, social links, and the language switch. In FA fixture tests the footer measured 667px instead of 1108px at 390px and 408px instead of 507px at 1440px.
- Verified 110 Chromium page, language and viewport combinations, including short landscape. Checked touch and keyboard navigation, video playback and reduced motion, eight browser combinations with actual admin changes, and purchase and newsletter submissions in both languages. Checked matching seam pixels in the default palette. Captured before and after images with shared fixtures.
- Migration `0018` adds five settings fields and was applied and reversed on disposable SQLite fixtures. Django checks, collectstatic, JS syntax, GDCS and Git whitespace checks passed. The five unrelated model-state differences recorded under GNT-001 remain present. Production media, theme and database were outside verification.

## 2026-11-22 — GNT-014 · Transparent controls, compact footer and blog retirement

- Use a clear, outlined header purchase CTA and a plain all-projects text link. Retire old filled-background theme overrides for these controls. Make the homepage hero labels smaller while preserving 44px targets. Remove carousel arrow buttons while retaining mouse drag, touch, trackpad and keyboard navigation.
- Remove the footer description and reduce the space above the wordmark. Keep the four groups in native disclosures. Their default compact state grows only when a visitor opens a group. On the same FA fixtures the footer measured 222px instead of 667px at 390px wide and 292px instead of 408px at 1440px.
- Remove Journal links, routes, views, model, templates, sitemap entries and CMS controls. Legacy local blog links are filtered in navigation and the menu editor. Django returns 404 for old blog pages and covers. Migration 0019 moves the old table outside the application model registry and preserves existing rows. Reverse migration restored the same article content in SQLite.
- Verified 72 Chromium page, language and viewport combinations, including short desktop and landscape phone layouts. Default footer was less than half the viewport height in these fixtures. Verified native mobile disclosure with and without JavaScript, resized footer state, carousel drag and keyboard, consultation and newsletter persistence in both languages, sitemap and old routes, admin views and fresh migration. Production was outside this verification.

## 2026-11-23 — GNT-015 · Project portfolio and standalone About

- Match the supplied reference compositions with a photo-led project index and a split detail page with real project facts, optional construction progress, gallery and related projects. Keep current project URLs, status anchors, catalogue links, purchase availability and the shared header and footer.
- Add a bilingual About page with story, philosophy, principles, quote and portfolio CTA. Connect the homepage button, legacy internal menu links and the footer. Include the route in the sitemap.
- Expose page copy, section visibility and media in Site Sections, project story and progress in Projects, principles in Philosophy Features, labels in Site Texts and the scoped palette in SiteTheme. Use supplied concept WebPs for page illustration fallbacks. Project images remain from CMS records. Migration 0020 adds optional project fields, bilingual labels and initial sections while preserving existing records.
- Verified 100 page, language and viewport combinations in Chromium, including a project without photos or purchase, a zero value for progress and short landscape. Verified the gallery with touch, keyboard and focus restoration, project/status navigation, both forms and the persisted records in both languages. Saved actual admin form edits for titles, labels, colors, progress, principles and an uploaded image, and verified them in Chromium. A fresh SQLite migration and 0020 rollback and reapply passed. Django check, collectstatic, JavaScript syntax and Git whitespace passed. Screenshots use local test content.

## 2026-11-23 — GNT-016 · Project search, catalogue visibility and responsive refinements

- Add a shared header search icon and a compact server-rendered search form on Projects. Match active project name, code and location in both languages, with normalized Persian and Arabic characters and digits. Keep status groups, an editable bilingual hint, and a reset action.
- Add per-project catalogue action visibility. The PDF stays attached when the action is hidden. Existing catalogues default to visible after migration 0021.
- Refine editorial headings, spacing, gallery sizing and mobile breakpoints. Place progress percentage, a native progress bar and current stage together. Remove the public history-back and back-to-top controls and square the footer purchase button.
- Chromium passed 120 page, language and viewport combinations from 320px through 1920px, with separate search checks with and without JavaScript and eight long-text checks. Verified catalogue toggles and search labels through real Django admin saves, zero/unknown/100% progress, purchase and newsletter persistence, Django checks, production-mode collectstatic and migration 0021 apply/revert/reapply in SQLite.

## 2026-11-23 — GNT-017 · Single project search results grid

- Render one set of matching project cards while a query is active. A genuine zero-match search shows one message. The reset and standard status navigation restore the default portfolio view.
- Verified 64 Chromium result combinations covering completed-only, ongoing-only, mixed and zero results in FA/EN at four widths, with and without JavaScript. Verified search form submission, reset and result navigation in all 16 browser contexts. Django checks and production-mode collectstatic passed.

## 2026-11-23 — GNT-018 · Request dialog design and field feedback

- Align the shared request dialog with the dark homepage, using square controls, a neutral submit action and translucent backdrop. Compact the responsive field and option layout and keep the form scrollable on short screens.
- Bind error feedback to the corresponding controls and preserve input on server validation. Keep editable bilingual copy and active theme keys, with configurable field border, placeholder and close-icon colors.
- Verified 64 Chromium route, language and viewport combinations, including 320px widths and landscape. Verified keyboard focus trap and restoration, backdrop and Escape dismissal, a resized 228px viewport, client feedback, server errors and persisted request and newsletter submissions. Verified actual admin writes and browser-rendered colors and long labels at eight viewport and language combinations. Django checks, collectstatic, JavaScript syntax and Git whitespace passed.

## 2026-11-23 — GNT-019 · Request dialog frame and template styles

- Include scoped dialog styles in the shared template. Keep the dialog above the page with a compact charcoal panel, a thin visible frame and an opaque neutral base beneath the editable panel color.
- Reproduced the unstyled GNT-018 dialog with the actual GNT-017 stylesheet. Chromium passed 60 checks across Home and Project Detail in FA/EN at five viewport sizes in normal production mode, with older shared CSS, and with local CSS blocked. Captured eight before and after images at mobile and desktop sizes.
- Verified keyboard focus, touch controls, validation and two stored requests. Verified Django admin changes to the panel border and submit color, including the opaque fallback when given a transparent panel color. Django checks and production-mode collectstatic passed.

## 2026-11-23 — GNT-020 · Light glass request dialog

- Use a translucent off-white panel, scoped backdrop blur and an outlined, transparent submit action. Provide a solid fallback for reduced transparency and browsers without backdrop blur.
- Expose independent panel, field, action, state and layout settings in the existing SiteTheme admin section. Retain existing overrides and bilingual copy controls. Reuse the JSON settings field without schema changes.
- Chromium passed 60 checks on Home and Project Detail in FA/EN at five viewport sizes with normal, stale or blocked local CSS. Verified keyboard and touch interaction, validation, two persisted requests and eight before/after captures. A real admin save and reset covered colors, numeric limits, zero blur and bilingual copy. Verified custom styles and reduced transparency in six additional browser configurations. Django checks and production collectstatic passed. The migration dry-run output matched the GNT-019 baseline.

## 2026-11-23 — GNT-021 · Localized request phones and neutral form palette

- Share the accepted phone pattern between Django and the browser. Accept Latin, Persian and Arabic-Indic digits with optional separators and supported Iranian prefixes. Store normalized local numbers and keep invalid input intact.
- Use off-white glass, a neutral page veil and a transparent action. Replace control boxes with underlines and preserve keyboard focus. Keep retired form colors in SiteTheme for rollback and offer independent active settings.
- Reproduced the Persian-digit rejection and the orange button and dark boxes using GNT-020 and legacy fixture settings. Chromium passed 60 page, language, viewport and CSS combinations. Verified three browser submissions, 32 direct validation cases and four CSRF-protected POSTs without browser validation. Verified saved phone numbers, admin save and reset, eight before/after captures, Django checks, production static collection and JavaScript syntax. Migration dry-run output matched GNT-020.

## 2026-11-24 — GNT-022 · Project portfolio and gallery

- Use the supplied Gar.zip as the baseline. Simplify the portfolio opening to its title and label, move search and status links into a compact toolbar, and remove the About callout. Keep status anchors and compact the project cards.
- Share an editable charcoal and ivory palette across the portfolio and project details. Place the story and gallery side by side on desktop and reduce the height of related project cards on mobile. Restore the two existing About fallback images missing from the supplied archive.
- Replace the gallery viewer with a native dialog supporting touch, mouse dragging, keyboard, captions and focus restoration. Expand images inline without JavaScript or native dialog support.
- Chromium verified FA/EN at 320, 390, 768, 1024 and 1440px, including search, related cards, request modal and empty gallery scenarios. Separate gallery checks covered touch, dragging, arrows, keyboard and no-dialog fallback. Verified ten real admin color saves and computed styles on both project pages and About. Django checks, static collection and JavaScript syntax passed.

## 2026-11-24 — GNT-023 · Minimal project photo viewer

- Size the charcoal viewer to the uncropped photo and use a single overlaid close control. Preserve captions and the position indicator in a compact bar under the photo.
- Keep touch swipes, desktop dragging, keyboard navigation and inline enlargement. Add single-tap navigation at the photo edges and describe the controls for assistive technology.
- Chromium passed 12 bilingual modal configurations with portrait and landscape images, including a short landscape viewport. Checked the one-button layout, long captions, gestures, focus restoration, and expansion with JavaScript disabled or native dialog support unavailable. Django checks, production static collection and JavaScript syntax passed.

## 2026-11-24 — GNT-024 · Gallery arrows and related projects

- Add translucent navigation arrows on the left and right edges of the full-size photo. Visible discs use 44px touch targets and RTL-aware labels and navigation. Keep swipes, mouse dragging and the single-photo layout.
- Use a charcoal default background for related projects. SiteTheme can set its background and foreground independently through the existing color controls.
- Chromium passed 12 bilingual viewport configurations, gesture and keyboard navigation, the single-photo case and both inline fallbacks. Verified actual admin saves and rendered custom colors scoped to related projects. Django checks, production static collection and JavaScript syntax passed.
