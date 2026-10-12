# Garnet UI Specification

## Visual direction

The supplied Stitch reference is the visual source of truth. The Django frontend keeps its architectural editorial layout while adding a restrained glassmorphism system.

### Palette
- Deep navy: `#092634`
- Primary architectural blue: `#003651`
- Blue architectural accent: `#004E72`
- Vibrant orange: `#FF6E42`
- Light canvas: `#F9F9F9`
- Primary text: `#1A1C1C`
- Muted text: `#60727D`
- Glass border: `rgba(255,255,255,.15)`

## Glass rules
- Panels use 8–12% white fill on dark surfaces.
- Backdrop blur: 14–22px.
- Borders stay visible so text remains readable.
- Body text contrast is intentionally high; the glass is never fully opaque or fully transparent.

## Responsive breakpoints
- Desktop: >1050px
- Tablet: 821–1050px
- Mobile: ≤820px
- Small mobile: ≤520px

## Image sizes
| Usage | Recommended source | Ratio |
|---|---:|---:|
| Hero background | 2560×1600 | 16:10 |
| Project main | 1600×1100 | ~3:2 |
| Project gallery | 1600×1200 | 4:3 |
| Section image | 1400×1100 | ~5:4 |
| Service icon | 256×256 | 1:1 |
| Logo raster fallback | 800×800+ | 1:1 |

Keep important architectural subjects inside the central 70% safe area because the hero is cropped differently across devices.
