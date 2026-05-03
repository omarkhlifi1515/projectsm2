---
name: Premium Intellectual
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#393939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#d0c5af'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#99907c'
  outline-variant: '#4d4635'
  surface-tint: '#e9c349'
  primary: '#f2ca50'
  on-primary: '#3c2f00'
  primary-container: '#d4af37'
  on-primary-container: '#554300'
  inverse-primary: '#735c00'
  secondary: '#c7c7ba'
  on-secondary: '#2f3128'
  secondary-container: '#46483d'
  on-secondary-container: '#b5b6a9'
  tertiary: '#c6cee8'
  on-tertiary: '#283044'
  tertiary-container: '#abb2cc'
  on-tertiary-container: '#3d455a'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffe088'
  primary-fixed-dim: '#e9c349'
  on-primary-fixed: '#241a00'
  on-primary-fixed-variant: '#574500'
  secondary-fixed: '#e3e3d5'
  secondary-fixed-dim: '#c7c7ba'
  on-secondary-fixed: '#1b1c14'
  on-secondary-fixed-variant: '#46483d'
  tertiary-fixed: '#dae2fd'
  tertiary-fixed-dim: '#bec6e0'
  on-tertiary-fixed: '#131b2e'
  on-tertiary-fixed-variant: '#3f465c'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Newsreader
    fontSize: 48px
    fontWeight: '600'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  h1:
    fontFamily: Newsreader
    fontSize: 32px
    fontWeight: '500'
    lineHeight: '1.2'
  h2:
    fontFamily: Newsreader
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.1em
  ui-element:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 8px
  margin-page: 40px
  gutter-grid: 24px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
  hairline: 0.5px
---

## Brand & Style

This design system establishes a visual language of academic authority and precision for the ENISO Assistant. It moves away from the ephemeral nature of modern SaaS trends, instead grounding the user experience in the permanence of a digital library or a high-end research institution.

The style is a hybrid of **Minimalism** and **Tactile** design. It utilizes heavy whitespace to allow complex information to breathe, while employing subtle physical metaphors—like grain textures and paper-thin strokes—to evoke the feeling of high-quality parchment and scholarly journals. The brand personality is unapologetically sophisticated, catering to researchers and academics who value meticulous detail and trustworthy assistance.

## Colors

The palette is anchored by a deep, monochromatic base to minimize eye strain during long-form research. 

- **Primary (Academic Gold):** Used sparingly for interactive elements, highlights, and primary call-to-actions. It represents excellence and prestige.
- **Secondary (Ivory):** The primary color for typography and high-contrast iconography. Its warmth reduces the harshness typically found in pure white digital text.
- **Midnight Blue & Charcoal:** These layered neutrals provide the structural foundation. Midnight Blue is used for primary navigation and deep backgrounds, while Charcoal defines tactile surfaces and containers.
- **Accents:** Functional colors (success/error) are desaturated and "muddy" to maintain the sophisticated atmosphere, avoiding neon or vibrant tones that would disrupt the professional aesthetic.

## Typography

The typographic system relies on the interplay between tradition and utility. 

**Newsreader** serves as the voice of authority. It is used for headlines, block quotes, and editorial moments. Its varied stroke widths and classical serifs lend a "published" feel to long-form insights.

**Inter** handles the heavy lifting of the UI. It provides maximum legibility for chat logs, data tables, and input fields. Technical content (like citations or metadata) should use the `label-caps` style to create a distinct hierarchy between the core content and the supporting data.

## Layout & Spacing

This design system utilizes a **Fixed Grid** model for desktop and a fluid model for mobile. Layouts should feel architectural and intentional, reminiscent of a well-typeset academic paper.

- **The 0.5px Rule:** Separation is achieved primarily through extremely fine lines (`hairline`) rather than heavy shadows or large gaps. These lines should use the Ivory color at 15-20% opacity.
- **Rhythm:** Spacing follows an 8px modular scale. High-density areas (like toolbars) use 8px gaps, while content-heavy areas (like the chat canvas) use 32px or 40px margins to prevent visual clutter.
- **Alignment:** Strict left-alignment for all text content to preserve the reading line, with generous margins on the right for "marginalia" or citations.

## Elevation & Depth

Depth in this system is conveyed through **Tonal Layers** and texture rather than light-source simulation.

1.  **The Canvas (Level 0):** The deepest layer, using Midnight Blue. A subtle film grain texture is applied globally to prevent "flatness" and give the screen a tactile, paper-like quality.
2.  **Surface Containers (Level 1):** Slightly lighter Charcoal tones with a `hairline` border. These hold primary content blocks.
3.  **Active Elements (Level 2):** Elements being interacted with or currently "active" utilize soft, deep shadows (Blur: 24px, Opacity: 40%, Color: Black) to appear as if they are hovering slightly off the desk.

Avoid backdrop blurs or frosted glass. Depth is found in "stacking" dark paper on dark paper, separated by fine light-reflecting edges.

## Shapes

The shape language is "Architectural"—meaning corners are present but softened just enough to feel professional rather than sharp.

- **Standard Radius:** 4px (Soft) for buttons, inputs, and small modules.
- **Container Radius:** 8px for cards and the main chat window.
- **Interactive Elements:** Avoid pills or full circles unless used for status indicators. Rectilinear forms reinforce the brand's precision and "Tech" aspect.

## Components

- **Primary Buttons:** Solid Academic Gold background with Midnight Blue text. No gradients. On hover, the gold slightly brightens, and a 0.5px border appears 2px outside the button to create a "precise target" effect.
- **Scholarly Inputs:** Input fields are defined by a bottom border only (0.5px Ivory) when inactive, turning into a full 4px-radius box when focused.
- **Citations & Footnotes:** Small Inter caps text with a subtle Academic Gold highlight on hover. These should appear in the "marginalia" (the right gutter of the layout).
- **Cards:** No background color; defined by a 0.5px Ivory border at low opacity. This keeps the layout airy and focused on the text.
- **Chat Blocks:** Eschew the "bubble" look. Use "blocks" of text separated by vertical dividers or subtle indentations, mimicking the structure of a dialogue in a play or a scripted manuscript.
- **Micro-interactions:** Transitions should be fast (150ms-200ms) with a linear-out-slow-in easing curve. Elements shouldn't "bounce"; they should click into place with mechanical precision.