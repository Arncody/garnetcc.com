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
- Header: logo on the physical left and purchase controls on the physical right in both languages. The navigation follows the current language direction. The strip is transparent at the top and gains a full-width translucent glass layer after scrolling. Blur is capped at 14px. The desktop submenu aligns with its trigger. At 1088px and below, the native disclosure opens at the right edge of the header container. JavaScript enhances dismissal and submenus.
- Buttons: filled primary, outlined secondary, and text variants with a 12px control radius. Home cards and action buttons have no decorative outer borders. Project view actions size to their labels and use a directional arrow inside the full-card link. Interactive targets are at least 44×44px where the button itself is the hit area. Use a visible 2px focus outline with light or dark color for the surrounding surface.
- Motion: state transitions use 150ms. Shared transitions are removed for reduced-motion preferences.
- Hero: neutral scrim keeps text readable over bright media, with a matching fallback for media-free states.
- Home projects: card widths use one homepage-scoped token in the carousel and in its fallback. On desktop cards cap at 290px. At 900px and below the fallback remains swipeable. The project's title, status and full-card link remain visible.
- Footer: brand and purchase CTA above four groups for quick links, company information, contact, and newsletter/social links. Groups wrap to two columns on tablets and one column on narrow phones. Buy opens the existing request form. The white wordmark and configured tagline share an inline edge (right in Persian, left in English). The template compensates for transparent padding in supported logo files from configured storage. The language switch lives in the footer.

## SiteTheme compatibility

The historical database defaults inherit the shared palette at render time. Valid custom base colors are published as CSS properties. Existing header and project action overrides still apply. The footer purchase button has its own background, text and hover controls. Legacy values for retired decoration remain stored for rollback and are marked inactive in the admin.

The admin keeps the header purchase label in SiteTexts and the logo and tagline in SiteSettings. The SiteTexts group for homepage projects and footer purchase adds bilingual labels for the homepage project heading, project view action and footer purchase button. Migration `website.0017_home_and_footer_display_texts` adds these fields with the previous public labels as defaults. Apply it with `python manage.py migrate --noinput` after backing up the deployment database, then refresh static files with `python manage.py collectstatic --noinput`. For rollback, retain the added columns if their text values need to be preserved. Reversing to `0016` removes the six fields and their values.

## Responsive and media

Review 320, 390, 768, 1024 and 1440px in both directions. Keep essential Hero subjects inside a central safe area. Suggested sources are 2560×1600 for Hero, 1600×1100 for project covers, and 1600×1200 or 1920×1280 for gallery images.
