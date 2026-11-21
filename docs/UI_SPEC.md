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
- Layout: max width 1200px, shared gutters from 16 to 40px, section spacing from 32 to 64px. Header and content follow inline direction.
- Header: full-width glass, dark over the Home and Project Hero before scroll and light elsewhere. Blur is capped at 12px. The shared container aligns the logo with the footer and main sections. Use the configured logo variant when available. The desktop shows inline navigation and a language switch. Smaller viewports use the existing collapsible menu.
- Buttons: filled primary, outlined secondary, and text variants. Interactive targets are at least 44×44px where the button itself is the hit area. Use a visible 2px focus outline with light or dark color for the surrounding surface.
- Motion: state transitions use 150ms. Shared transitions are removed for reduced-motion preferences.
- Hero: neutral scrim keeps text readable over bright media, with a matching fallback for media-free states.
- Footer: brand and purchase CTA above four groups for quick links, company information, contact, and newsletter/social links. Groups wrap to two columns on tablets and one column on narrow phones. Buy opens the existing request form. Use configured brand text, contacts and social destinations.

## SiteTheme compatibility

The historical database defaults inherit the new shared palette at render time. Valid custom base colors are published as CSS properties and existing component color overrides are still applied. Legacy values for retired decoration remain stored for rollback. The admin marks their controls as inactive. No schema migration is required. Review site-specific custom colors and custom CSS for contrast before deployment.

## Responsive and media

Review 320, 390, 768, 1024 and 1440px in both directions. Keep essential Hero subjects inside a central safe area. Suggested sources are 2560×1600 for Hero, 1600×1100 for project covers, and 1600×1200 or 1920×1280 for gallery images.
