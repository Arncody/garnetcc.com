# GARNET UI Specification

## Modern Architectural Minimalism

Use quiet monochrome surfaces and architectural photography. The default palette lives in `website/theme_tokens.py` and is exposed as CSS properties by the shared template. `static/css/design-system.css` defines the semantic roles and shared component tokens.

| Palette | Hex | Main use |
|---|---|---|
| Charcoal | `#141414` | Text, primary actions and dark surfaces |
| Footer Charcoal | `#171717` | Footer canvas |
| Graphite | `#383838` | Secondary text and primary-action hover |
| Gray | `#858585` | Control borders |
| Stone | `#E8E7E4` | Dividers, secondary hover and neutral metadata |
| Off White | `#F8F8F6` | Page canvas |
| White | `#FFFFFF` | Surfaces and inverse text |

Regional colors remain available for operational feedback such as validation. Project status is communicated by text.

## Shared components

- Type: IRANSansWebFaNum in FA, system sans in EN. Body 16px, controls 14px, metadata 13px. Display and section headings scale fluidly.
- Layout: max width 1200px, shared gutters from 16 to 40px, section spacing from 32 to 64px. Content follows the current language direction.
- Header: logo on the physical left and purchase controls on the physical right in both languages. The navigation follows the current language direction. The purchase button is transparent with a thin outline, using the header ink for the current background. Scrolling reveals a full-width translucent layer with blur capped at 14px. At 1088px and below, the native disclosure opens from the right.
- Buttons: filled primary, outlined secondary, and text variants with a 12px control radius. Home cards and action buttons have no decorative outer borders. Project view actions size to their labels and use a directional arrow inside the full-card link. Interactive targets are at least 44×44px where the button itself is the hit area. Use a visible 2px focus outline with light or dark color for the surrounding surface.
- Motion: state transitions use 150ms. Shared transitions are removed for reduced-motion preferences.
- Homepage opening: the hero fills at least the dynamic viewport height and can grow for long text. The media covers the viewport and the centered text and project actions sit near its lower edge. A vertical gradient ends at `#101111` by default, the same color used by the immediately following About section. The poster remains available for reduced motion or video failure. Edit the opening in Hero and edit the About heading, subtitle and description in Site Sections.
- Home projects: editorial previews use square corners by default and have a local radius control. Card widths share a homepage token in the carousel and its fallback, and cap at 290px on desktop. The text-only all-projects control pairs its editable label with a direction-aware arrow. Rails are navigable with touch, drag, trackpad and keyboard.
- Footer: the brand wordmark and purchase CTA sit above four disclosure groups for quick links, company information, contact, and newsletter/social links. In compact mode the groups start closed on narrow or short viewports and open on desktop. The newsletter uses the full row when opened on small phones. Footer purchase, newsletter signup and the language switch remain available in both layouts.

## SiteTheme compatibility

The historical database defaults inherit the shared palette at render time. Valid custom base colors are published as CSS properties. Existing header and project action overrides still apply. The footer purchase button has its own background, text and hover controls. Legacy values for retired decoration remain stored for rollback and are marked inactive in the admin.

The admin keeps the header purchase label in SiteTexts and the logo in SiteSettings. Use SiteTexts for the About and all-projects link labels and SiteTheme for the shared hero/About color and compact footer setting. Menu labels and ordering are edited in Menu Items.

Apply `website.0019_archive_blog` with `python manage.py migrate --noinput` after backing up the database. Refresh static files with `python manage.py collectstatic --noinput`. The migration archives the article table as `website_retired_blogpost` with its contents intact. Old blog URLs and Django-served blog media return 404. To roll back, migrate to `0018` with the GNT-014 code, then restore the GNT-013 files.

## Responsive and media

Review 320, 390, 768, 1024 and 1440px in both directions. Keep essential Hero subjects inside a central safe area. Suggested sources are 2560×1600 for Hero, 1600×1100 for project covers, and 1600×1200 or 1920×1280 for gallery images.
