# Design Language: Log In | Octopoda

> Extracted from `https://octopodas.com/dashboard/shared` on May 8, 2026
> 110 elements analyzed

This document describes the complete design language of the website. It is structured for AI/LLM consumption — use it to faithfully recreate the visual design in any framework.

## Color Palette

### Primary Colors

| Role | Hex | RGB | HSL | Usage Count |
|------|-----|-----|-----|-------------|
| Primary | `#f97015` | rgb(249, 112, 21) | hsl(24, 95%, 53%) | 15 |
| Secondary | `#fba66a` | rgb(251, 166, 106) | hsl(25, 95%, 70%) | 1 |
| Accent | `#e8d6c9` | rgb(232, 214, 201) | hsl(25, 40%, 85%) | 5 |

### Neutral Colors

| Hex | HSL | Usage Count |
|-----|-----|-------------|
| `#ebebeb` | hsl(0, 0%, 92%) | 105 |
| `#141414` | hsl(0, 0%, 8%) | 35 |
| `#000000` | hsl(0, 0%, 0%) | 33 |
| `#2c2421` | hsl(16, 14%, 15%) | 8 |
| `#756157` | hsl(20, 15%, 40%) | 8 |
| `#ffffff` | hsl(0, 0%, 100%) | 7 |
| `#493d36` | hsl(22, 15%, 25%) | 6 |
| `#988881` | hsl(18, 10%, 55%) | 2 |
| `#fff5eb` | hsl(30, 100%, 96%) | 1 |
| `#67554c` | hsl(20, 15%, 35%) | 1 |

### Background Colors

Used on large-area elements: `#14141f`, `#fff5eb`, `#ffffff`

### Text Colors

Text color palette: `#000000`, `#141414`, `#2c2421`, `#67554c`, `#f97015`, `#493d36`, `#756157`, `#d2bcac`, `#ffffff`, `#988881`

### Gradients

```css
background-image: linear-gradient(135deg, rgb(249, 112, 21), rgb(249, 158, 31));
```

### Full Color Inventory

| Hex | Contexts | Count |
|-----|----------|-------|
| `#ebebeb` | border | 105 |
| `#141414` | text, background | 35 |
| `#000000` | text | 33 |
| `#f97015` | text | 15 |
| `#2c2421` | text | 8 |
| `#756157` | text | 8 |
| `#ffffff` | background, text | 7 |
| `#493d36` | text | 6 |
| `#e8d6c9` | border | 5 |
| `#d2bcac` | text | 2 |
| `#988881` | text | 2 |
| `#fff5eb` | background | 1 |
| `#fba66a` | background | 1 |
| `#67554c` | text | 1 |

## Typography

### Font Families

- **Inter** — used for all (77 elements)
- **Space Grotesk** — used for body (33 elements)

### Type Scale

| Size (px) | Size (rem) | Weight | Line Height | Letter Spacing | Used On |
|-----------|------------|--------|-------------|----------------|---------|
| 60px | 3.75rem | 800 | 60px | -1.5px | h1, span |
| 20px | 1.25rem | 700 | 28px | -0.5px | a, h2 |
| 18px | 1.125rem | 400 | 28px | normal | p, span |
| 16px | 1rem | 400 | 24px | normal | html, head, script, meta |
| 14px | 0.875rem | 400 | 20px | normal | div, a, span, p |
| 12px | 0.75rem | 500 | 16px | normal | label, button, p, span |

### Heading Scale

```css
h1 { font-size: 60px; font-weight: 800; line-height: 60px; }
h2 { font-size: 20px; font-weight: 700; line-height: 28px; }
```

### Body Text

```css
body { font-size: 18px; font-weight: 400; line-height: 28px; }
```

### Font Weights in Use

`400` (95x), `600` (6x), `800` (4x), `500` (3x), `700` (2x)

## Spacing

**Base unit:** 2px

| Token | Value | Rem |
|-------|-------|-----|
| spacing-4 | 4px | 0.25rem |
| spacing-40 | 40px | 2.5rem |
| spacing-48 | 48px | 3rem |
| spacing-64 | 64px | 4rem |
| spacing-112 | 112px | 7rem |

## Border Radii

| Label | Value | Count |
|-------|-------|-------|
| lg | 12px | 6 |
| xl | 24px | 1 |

## Box Shadows

**sm** — blur: 0px
```css
box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.05) 0px 1px 2px 0px;
```

**sm** — blur: 0px
```css
box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.15) 0px 20px 60px -20px;
```

**lg** — blur: 24px
```css
box-shadow: rgba(249, 112, 21, 0.5) 0px 8px 24px -8px;
```

## CSS Custom Properties

### Colors

```css
--foreground: 0 0% 8%;
--card: 0 0% 100%;
--card-foreground: 0 0% 8%;
--popover: 0 0% 100%;
--popover-foreground: 0 0% 8%;
--primary: 24 95% 53%;
--primary-foreground: 0 0% 100%;
--secondary: 0 0% 8%;
--secondary-foreground: 0 0% 100%;
--muted: 0 0% 96%;
--muted-foreground: 0 0% 45%;
--accent: 24 95% 53%;
--accent-foreground: 0 0% 100%;
--destructive: 0 84% 60%;
--destructive-foreground: 0 0% 100%;
--border: 0 0% 92%;
--ring: 24 95% 53%;
--dark-bg: 228 12% 8%;
--dark-border: 228 10% 16%;
--dark-muted: 0 0% 55%;
--dash-bg: 228 12% 7%;
--dash-card: 228 12% 12%;
--dash-card-hover: 228 12% 14%;
--dash-border: 228 10% 18%;
--dash-border-subtle: 228 10% 14%;
--dash-text-muted: 220 10% 50%;
--code-bg: 0 0% 6%;
--code-border: 0 0% 14%;
--code-foreground: 0 0% 75%;
--tw-ring-offset-shadow: 0 0 #0000;
--tw-ring-shadow: 0 0 #0000;
--tw-ring-inset: ;
--tw-border-spacing-x: 0;
--tw-ring-color: rgb(59 130 246 / .5);
--tw-ring-offset-color: #fff;
--tw-ring-offset-width: 0px;
--tw-shadow-colored: 0 0 #0000;
--tw-border-spacing-y: 0;
```

### Spacing

```css
--tw-numeric-spacing: ;
--tw-contain-size: ;
```

### Typography

```css
--dark-text: 0 0% 98%;
--dash-text: 0 0% 95%;
--dash-text-dim: 220 10% 35%;
```

### Shadows

```css
--tw-drop-shadow: ;
--tw-shadow: 0 0 #0000;
```

### Radii

```css
--radius: .75rem;
```

### Other

```css
--background: 0 0% 100%;
--input: 0 0% 92%;
--sunset-orange: 24 95% 53%;
--sunset-amber: 35 95% 55%;
--sunset-peach: 25 100% 94%;
--dark-surface: 228 12% 11%;
--dash-surface: 228 12% 10%;
--tw-backdrop-sepia: ;
--tw-sepia: ;
--tw-ordinal: ;
--tw-backdrop-saturate: ;
--tw-contain-style: ;
--tw-backdrop-invert: ;
--tw-brightness: ;
--tw-backdrop-grayscale: ;
--tw-hue-rotate: ;
--tw-scale-y: 1;
--tw-pan-y: ;
--tw-backdrop-contrast: ;
--tw-backdrop-brightness: ;
--tw-pan-x: ;
--tw-translate-y: 0;
--tw-rotate: 0;
--tw-contrast: ;
--tw-skew-x: 0;
--tw-backdrop-blur: ;
--tw-translate-x: 0;
--tw-gradient-via-position: ;
--tw-saturate: ;
--tw-scroll-snap-strictness: proximity;
--tw-grayscale: ;
--tw-scale-x: 1;
--tw-backdrop-hue-rotate: ;
--tw-gradient-to-position: ;
--tw-numeric-fraction: ;
--tw-skew-y: 0;
--tw-slashed-zero: ;
--tw-blur: ;
--tw-invert: ;
--tw-backdrop-opacity: ;
--tw-numeric-figure: ;
--tw-gradient-from-position: ;
--tw-pinch-zoom: ;
--tw-contain-paint: ;
--tw-contain-layout: ;
```

### Semantic

```css
success: [object Object];
warning: [object Object];
error: [object Object];
info: [object Object];
```

## Breakpoints

| Name | Value | Type |
|------|-------|------|
| sm | 600px | max-width |
| sm | 640px | min-width |
| md | 767px | max-width |
| md | 768px | min-width |
| lg | 1024px | min-width |
| xl | 1240px | min-width |
| xl | 1280px | min-width |

## Transitions & Animations

**Easing functions:** `[object Object]`

**Durations:** `0.15s`, `0.2s`

### Common Transitions

```css
transition: all;
transition: color 0.15s cubic-bezier(0.4, 0, 0.2, 1), background-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), border-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), text-decoration-color 0.15s cubic-bezier(0.4, 0, 0.2, 1), fill 0.15s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.15s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.15s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.15s cubic-bezier(0.4, 0, 0.2, 1), transform 0.15s cubic-bezier(0.4, 0, 0.2, 1), filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), backdrop-filter 0.15s cubic-bezier(0.4, 0, 0.2, 1), -webkit-backdrop-filter 0.15s cubic-bezier(0.4, 0, 0.2, 1);
transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
```

### Keyframe Animations

**marquee**
```css
@keyframes marquee {
  0% { transform: translate(0px); }
  100% { transform: translate(-50%); }
}
```

**ping**
```css
@keyframes ping {
  75%, 100% { transform: scale(2); opacity: 0; }
}
```

**pulse**
```css
@keyframes pulse {
  50% { opacity: 0.5; }
}
```

**spin**
```css
@keyframes spin {
  100% { transform: rotate(360deg); }
}
```

**enter**
```css
@keyframes enter {
  0% { opacity: var(--tw-enter-opacity, 1); transform: translate3d(var(--tw-enter-translate-x, 0),var(--tw-enter-translate-y, 0),0) scale3d(var(--tw-enter-scale, 1),var(--tw-enter-scale, 1),var(--tw-enter-scale, 1)) rotate(var(--tw-enter-rotate, 0)); }
}
```

**exit**
```css
@keyframes exit {
  100% { opacity: var(--tw-exit-opacity, 1); transform: translate3d(var(--tw-exit-translate-x, 0),var(--tw-exit-translate-y, 0),0) scale3d(var(--tw-exit-scale, 1),var(--tw-exit-scale, 1),var(--tw-exit-scale, 1)) rotate(var(--tw-exit-rotate, 0)); }
}
```

**v2-blob-pulse**
```css
@keyframes v2-blob-pulse {
  0%, 100% { transform: scale(1) translateY(0px); opacity: 0.85; }
  50% { transform: scale(1.08) translateY(-12px); opacity: 1; }
}
```

**v2-bar-grow**
```css
@keyframes v2-bar-grow {
  0% { transform: scaleY(0); opacity: 0; }
  100% { transform: scaleY(1); opacity: 1; }
}
```

**v2-row-fill**
```css
@keyframes v2-row-fill {
  0% { transform: scaleX(0); }
  100% { transform: scaleX(1); }
}
```

**v2-dot**
```css
@keyframes v2-dot {
  0%, 100% { box-shadow: rgba(34, 197, 94, 0.6) 0px 0px; }
  50% { box-shadow: rgba(34, 197, 94, 0) 0px 0px 0px 8px; }
}
```

## Component Patterns

Detected UI component patterns and their most common styles:

### Buttons (2 instances)

```css
.button {
  color: rgb(249, 112, 21);
  font-size: 12px;
  font-weight: 500;
  padding-top: 0px;
  padding-right: 0px;
  border-radius: 0px;
}
```

### Cards (4 instances)

```css
.card {
  background-color: rgb(255, 255, 255);
  border-radius: 12px;
  box-shadow: rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0) 0px 0px 0px 0px, rgba(0, 0, 0, 0.05) 0px 1px 2px 0px;
  padding-top: 0px;
  padding-right: 0px;
}
```

### Inputs (2 instances)

```css
.input {
  background-color: rgb(255, 255, 255);
  color: rgb(44, 36, 33);
  border-color: rgb(228, 215, 205);
  border-radius: 12px;
  font-size: 14px;
  padding-top: 12px;
  padding-right: 16px;
}
```

### Links (6 instances)

```css
.link {
  color: rgb(117, 97, 87);
  font-size: 14px;
  font-weight: 400;
}
```

## Component Clusters

Reusable component instances grouped by DOM structure and style similarity:

### Input — 1 instance, 1 variant

**Variant 1** (1 instance)

```css
  background: rgb(255, 255, 255);
  color: rgb(44, 36, 33);
  padding: 12px 16px 12px 16px;
  border-radius: 12px;
  border: 1px solid rgb(228, 215, 205);
  font-size: 14px;
  font-weight: 400;
```

### Button — 2 instances, 2 variants

**Variant 1** (1 instance)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(249, 112, 21);
  padding: 0px 0px 0px 0px;
  border-radius: 0px;
  border: 0px solid rgb(235, 235, 235);
  font-size: 12px;
  font-weight: 500;
```

**Variant 2** (1 instance)

```css
  background: rgba(0, 0, 0, 0);
  color: rgb(255, 255, 255);
  padding: 14px 0px 14px 0px;
  border-radius: 12px;
  border: 0px solid rgb(235, 235, 235);
  font-size: 14px;
  font-weight: 600;
```

## Layout System

**1 grid containers** and **10 flex containers** detected.

### Container Widths

| Max Width | Padding |
|-----------|---------|
| 1280px | 48px |
| 576px | 0px |
| 512px | 0px |

### Grid Column Patterns

| Columns | Usage Count |
|---------|-------------|
| 2-column | 1x |

### Grid Templates

```css
grid-template-columns: 560px 560px;
gap: 64px;
```

### Flex Patterns

| Direction/Wrap | Count |
|----------------|-------|
| column/nowrap | 1x |
| row/nowrap | 9x |

**Gap values:** `16px`, `20px`, `64px`, `8px`

## Accessibility (WCAG 2.1)

**Overall Score: 100%** — 0 passing, 0 failing color pairs

## Dark Mode

The site has a distinct dark mode color scheme:

- **Primary:** `#f97015`
- **Secondary:** `#fba66a`
- **Backgrounds:** `#14141f`, `#fff5eb`, `#ffffff`
- **Text:** `#000000`, `#141414`, `#2c2421`, `#67554c`, `#f97015`

### Dark Mode CSS Variables

```css
--foreground: 0 0% 8%;
--card: 0 0% 100%;
--card-foreground: 0 0% 8%;
--popover: 0 0% 100%;
--popover-foreground: 0 0% 8%;
--primary: 24 95% 53%;
--primary-foreground: 0 0% 100%;
--secondary: 0 0% 8%;
--secondary-foreground: 0 0% 100%;
--muted: 0 0% 96%;
--muted-foreground: 0 0% 45%;
--accent: 24 95% 53%;
--accent-foreground: 0 0% 100%;
--destructive: 0 84% 60%;
--destructive-foreground: 0 0% 100%;
--border: 0 0% 92%;
--ring: 24 95% 53%;
--dark-bg: 228 12% 8%;
--dark-border: 228 10% 16%;
--dark-muted: 0 0% 55%;
--dash-bg: 228 12% 7%;
--dash-card: 228 12% 12%;
--dash-card-hover: 228 12% 14%;
--dash-border: 228 10% 18%;
--dash-border-subtle: 228 10% 14%;
--dash-text-muted: 220 10% 50%;
--code-bg: 0 0% 6%;
--code-border: 0 0% 14%;
--code-foreground: 0 0% 75%;
--tw-ring-offset-shadow: 0 0 #0000;
--tw-ring-shadow: 0 0 #0000;
--tw-ring-inset: ;
--tw-border-spacing-x: 0;
--tw-ring-color: rgb(59 130 246 / .5);
--tw-ring-offset-color: #fff;
--tw-ring-offset-width: 0px;
--tw-shadow-colored: 0 0 #0000;
--tw-border-spacing-y: 0;
--tw-numeric-spacing: ;
--tw-contain-size: ;
--dark-text: 0 0% 98%;
--dash-text: 0 0% 95%;
--dash-text-dim: 220 10% 35%;
--tw-drop-shadow: ;
--tw-shadow: 0 0 #0000;
--radius: .75rem;
--background: 0 0% 100%;
--input: 0 0% 92%;
--sunset-orange: 24 95% 53%;
--sunset-amber: 35 95% 55%;
--sunset-peach: 25 100% 94%;
--dark-surface: 228 12% 11%;
--dash-surface: 228 12% 10%;
--tw-backdrop-sepia: ;
--tw-sepia: ;
--tw-ordinal: ;
--tw-backdrop-saturate: ;
--tw-contain-style: ;
--tw-backdrop-invert: ;
--tw-brightness: ;
--tw-backdrop-grayscale: ;
--tw-hue-rotate: ;
--tw-scale-y: 1;
--tw-pan-y: ;
--tw-backdrop-contrast: ;
--tw-backdrop-brightness: ;
--tw-pan-x: ;
--tw-translate-y: 0;
--tw-rotate: 0;
--tw-contrast: ;
--tw-skew-x: 0;
--tw-backdrop-blur: ;
--tw-translate-x: 0;
--tw-gradient-via-position: ;
--tw-saturate: ;
--tw-scroll-snap-strictness: proximity;
--tw-grayscale: ;
--tw-scale-x: 1;
--tw-backdrop-hue-rotate: ;
--tw-gradient-to-position: ;
--tw-numeric-fraction: ;
--tw-skew-y: 0;
--tw-slashed-zero: ;
--tw-blur: ;
--tw-invert: ;
--tw-backdrop-opacity: ;
--tw-numeric-figure: ;
--tw-gradient-from-position: ;
--tw-pinch-zoom: ;
--tw-contain-paint: ;
--tw-contain-layout: ;
success: [object Object];
warning: [object Object];
error: [object Object];
info: [object Object];
```

## Design System Score

**Overall: 92/100 (Grade: A)**

| Category | Score |
|----------|-------|
| Color Discipline | 92/100 |
| Typography Consistency | 90/100 |
| Spacing System | 100/100 |
| Shadow Consistency | 100/100 |
| Border Radius Consistency | 100/100 |
| Accessibility | 100/100 |
| CSS Tokenization | 100/100 |

**Strengths:** Tight, disciplined color palette, Consistent typography system, Well-defined spacing scale, Clean elevation system, Consistent border radii, Strong accessibility compliance, Good CSS variable tokenization

**Issues:**
- 12 !important rules — prefer specificity over overrides
- 96% of CSS is unused — consider purging
- 2137 duplicate CSS declarations

## Gradients

**1 unique gradients** detected.

| Type | Direction | Stops | Classification |
|------|-----------|-------|----------------|
| linear | 135deg | 2 | brand |

```css
background: linear-gradient(135deg, rgb(249, 112, 21), rgb(249, 158, 31));
```

## Z-Index Map

**4 unique z-index values** across 3 layers.

| Layer | Range | Elements |
|-------|-------|----------|
| dropdown | 100,100 | ol.f.i.x.e.d. .t.o.p.-.0. .z.-.[.1.0.0.]. .f.l.e.x. .m.a.x.-.h.-.s.c.r.e.e.n. .w.-.f.u.l.l. .f.l.e.x.-.c.o.l.-.r.e.v.e.r.s.e. .p.-.4. .s.m.:.b.o.t.t.o.m.-.0. .s.m.:.r.i.g.h.t.-.0. .s.m.:.t.o.p.-.a.u.t.o. .s.m.:.f.l.e.x.-.c.o.l. .m.d.:.m.a.x.-.w.-.[.4.2.0.p.x.] |
| sticky | 10,20 | div.r.e.l.a.t.i.v.e. .z.-.1.0. .m.x.-.a.u.t.o. .m.a.x.-.w.-.7.x.l. .p.x.-.6. .l.g.:.p.x.-.1.2. .p.t.-.2.4. .m.d.:.p.t.-.2.8. .p.b.-.1.6. .m.i.n.-.h.-.s.c.r.e.e.n. .f.l.e.x. .i.t.e.m.s.-.c.e.n.t.e.r, span.r.e.l.a.t.i.v.e. .z.-.1.0, div.a.b.s.o.l.u.t.e. .t.o.p.-.8. .l.e.f.t.-.8. .m.d.:.t.o.p.-.1.0. .m.d.:.l.e.f.t.-.1.2. .z.-.2.0 |
| base | 0,0 | span.a.b.s.o.l.u.t.e. .i.n.s.e.t.-.x.-.0. .b.o.t.t.o.m.-.1. .h.-.[.0...5.e.m.]. .-.z.-.0 |

## SVG Icons

**3 unique SVG icons** detected. Dominant style: **outlined**.

| Size Class | Count |
|------------|-------|
| md | 3 |

**Icon colors:** `currentColor`

## Font Files

| Family | Source | Weights | Styles |
|--------|--------|---------|--------|
| Geist | google-fonts | 300, 400, 500, 600, 700, 800, 900 | normal |
| Geist Mono | google-fonts | 400, 500 | normal |
| Instrument Serif | google-fonts | 400 | normal |

**Google Fonts URL:** `https://fonts.googleapis.com/`

## Image Style Patterns

| Pattern | Count | Key Styles |
|---------|-------|------------|
| thumbnail | 1 | objectFit: fill, borderRadius: 0px, shape: square |

**Aspect ratios:** 4.8:1 (1x)

## Motion Language

**Feel:** mixed · **Scroll-linked:** yes

### Duration Tokens

| name | value | ms |
|---|---|---|
| `xs` | `150ms` | 150 |
| `sm` | `200ms` | 200 |

### Easing Families

- **custom** (7 uses) — `cubic-bezier(0.4, 0, 0.2, 1)`

## Component Anatomy

### button — 2 instances

**Slots:** label
**Sizes:** xs · xl

## Brand Voice

**Tone:** neutral · **Pronoun:** third-person · **Headings:** unknown (tight)

### Top CTA Verbs

- **forgot** (1)
- **continue** (1)

### Button Copy Patterns

- "forgot password?" (1×)
- "continue" (1×)

## Page Intent

**Type:** `dashboard` (confidence 0.6)
**Description:** Sign in to the Octopoda dashboard to monitor agents, inspect memory, review loop alerts, recover crashes, and manage production agent operations.

Alternates: auth (0.5)

## Section Roles

Reading order (top→bottom): content

| # | Role | Heading | Confidence |
|---|------|---------|------------|
| 0 | content | — | 0.3 |

## Material Language

**Label:** `flat` (confidence 0)

| Metric | Value |
|--------|-------|
| Avg saturation | 0.219 |
| Shadow profile | soft |
| Avg shadow blur | 0px |
| Max radius | 24px |
| backdrop-filter in use | no |
| Gradients | 1 |

## Imagery Style

**Label:** `mixed` (confidence 0)
**Counts:** total 1, svg 0, icon 0, screenshot-like 0, photo-like 0
**Dominant aspect:** ultra-wide
**Radius profile on images:** square

## Component Library

**Detected:** `tailwindcss` (confidence 0.81)

Evidence:
- tailwind-like class density 77%

## Component Screenshots

3 retina crops written to `screenshots/`. Index: `*-screenshots.json`.

| Cluster | Variant | Size (px) | File |
|---------|---------|-----------|------|
| input--outline--xl | 0 | 430 × 46 | `screenshots/input-outline-xl-0.png` |
| button--default--xs | 0 | 101 × 16 | `screenshots/button-default-xs-0.png` |
| button--default--xl | 0 | 430 × 48 | `screenshots/button-default-xl-0.png` |

Full-page: `screenshots/full-page.png`

## Quick Start

To recreate this design in a new project:

1. **Install fonts:** Add `Inter` from Google Fonts or your font provider
2. **Import CSS variables:** Copy `variables.css` into your project
3. **Tailwind users:** Use the generated `tailwind.config.js` to extend your theme
4. **Design tokens:** Import `design-tokens.json` for tooling integration
