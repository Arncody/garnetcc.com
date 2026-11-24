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

## Portfolio and About content

The project index opens with the editable portfolio label and title on charcoal. Its compact toolbar provides search and status links, and the ivory project grids retain the existing `#ongoing` and `#completed` anchors. The index ends at the project listing. The About page at `/about/` continues to use its own editorial sections and palette. All three pages share the site header and footer.

The header search icon opens the project search field. Search active projects by name, code or location in Persian or English. Matching projects appear in one grid. An empty search result has one message, and clearing the term restores the status sections. Search works without JavaScript.

The detail page uses charcoal for the project cover, facts and progress area. The story and gallery share one ivory section, side by side on desktop and stacked on smaller screens. Opening a gallery photo displays a frame sized to the uncropped image, with an overlaid close control and a compact caption and position indicator. Multiple photos add translucent controls on either side of the photo. The viewer also supports left/right keys, touch swipes, mouse dragging and taps at the photo edges. Escape closes the viewer and returns focus to the original photo. If the browser lacks dialog support or JavaScript is unavailable, gallery links enlarge the images inline. Related projects use a charcoal background and a compact two-column grid on mobile. Use the two «پروژه‌های بیشتر» settings under SiteTheme → «رنگ صفحات پروژه‌ها» to set the section background and its text independently.

Use SiteTheme → «رنگ صفحات پروژه‌ها» for the shared project palette and Site Sections for the bilingual portfolio title and label. Project records retain the story, photos, progress, stage and purchase controls. A known zero progress displays as zero, and an unknown value displays only the available stage. The About page retains its own color group and original static fallback images.

Migration `0021_project_search_and_catalog_visibility` adds bilingual search labels and a catalogue button visibility switch. In Projects, the button is shown when both «نمایش دکمه کاتالوگ پروژه» and the PDF are present. Turning off the switch retains the stored file. Use Site Texts to edit the search label and input hint.

## Request form

The shared request dialog uses translucent off-white glass from the site palette, a subtle frame and a neutral backdrop. The transparent submit action and text fields use a single underline. Radio options and the close button have no enclosing border by default. Keyboard focus remains visible. The panel uses solid off-white when backdrop blur is unsupported or reduced transparency is requested. Name and phone sit side by side above 576px. Inputs use a 16px floor, interactive controls use at least 44px targets and the panel scrolls independently in short viewports.

The shared template includes the dialog styles with its markup. SiteTheme → «فرم ثبت درخواست» controls the active colors, transparency, blur, sizes and spacing. Earlier saved form colors are retained for rollback. The current palette is editable independently. Use Site Texts for bilingual headings, labels, hints, options and the submit label.

The request form accepts Latin, Persian and Arabic-Indic digits, local and Iranian country-code formats, spaces and dashes. Django defines the accepted pattern for both the browser and server. Requests are saved with Latin digits in local format. Invalid numbers keep their original text and display field feedback.
