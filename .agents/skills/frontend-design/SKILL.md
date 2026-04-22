---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use when Codex needs support for building web components, pages, artifacts, posters, applications, dashboards, prototypes, HTML/CSS layouts, or styling or improving any visual web UI. Do not use for unrelated backend, CLI, or data-processing tasks. Inputs should include relevant files, product context, design constraints, and available tools. Output should be polished code or a concise plan, result, and verification summary that avoids generic AI aesthetics while respecting existing product design systems.
---

# Frontend Design

Use this skill to create or improve web interfaces where visual quality, interaction design, and implementation polish matter. The goal is not just "works in the browser"; the goal is a coherent product experience that feels intentionally designed for its audience, domain, and constraints.

## Operating Principles

- Start from context. Prefer the existing product code, design tokens, component library, screenshots, Figma context, brand guidelines, or reference surfaces over inventing a style from scratch.
- Match the product's visual vocabulary before extending it: color ratios, density, radius, elevation, icon style, motion, copy tone, and component rhythm.
- Avoid generic AI aesthetics: default blue buttons, purple/pink gradient wash, over-rounded cards, fake logo walls, fabricated testimonials, emoji-as-icons, vague "modern SaaS" layouts, and decorative effects that do not serve the product.
- Make a strong design choice, but keep it appropriate. A financial dashboard, developer tool, museum landing page, mobile prototype, and slide deck should not share the same aesthetic.
- Build real working UI. Include responsive behavior, interaction states, empty/error/loading states when relevant, and accessible focus treatment.

## Workflow

1. Understand the job. Identify the audience, product context, output type, required interactions, target breakpoints, framework constraints, and any design system already in use.
2. Gather design context. Read nearby UI code first when a repo exists. Use screenshots or references to extract tokens and behavior, not to copy blindly.
3. Declare the design direction before substantial implementation. For non-trivial visual work, state the planned color system, typography, spacing, radius, elevation, motion, and asset approach in a short note so the user can correct the direction early.
4. For high-risk or broad visual work, create a viewable v0 early. The v0 should show layout, tokens, key modules, and honest placeholders such as `[image]` or `[icon]`; it does not need every state or detail.
5. Implement the full UI using the repo's patterns. Prefer existing components and CSS/token conventions. Add abstractions only when they reduce real duplication or align with the codebase.
6. Verify in the browser or with the repo's frontend checks when available. For substantial UI work, inspect at desktop and mobile widths and fix visible overlap, overflow, blank canvases, broken assets, and console errors.

## Design System Declaration

For new pages, redesigns, prototypes, and visually significant changes, define these choices before writing the main implementation:

```markdown
Design direction:
- Audience and tone:
- Color system:
- Typography:
- Spacing and layout rhythm:
- Radius and elevation:
- Motion:
- Imagery, iconography, and placeholders:
- Responsive behavior:
```

Keep this lightweight for small edits. If the repo already has a design system, summarize how the change follows it rather than creating a new one.

## Color And Tokens

- Prefer CSS variables, Tailwind tokens, theme tokens, or the project's existing token system over one-off hex values.
- OKLCH is useful for deriving perceptually consistent palettes. Use it when the target stack supports it or when the project already uses modern CSS color functions.
- Avoid rogue hues. Once a palette is chosen, derive hover, border, muted, and emphasis colors from it instead of adding unrelated accents.
- Do not force a trendy palette. A restrained, domain-appropriate system is better than a loud but generic one.

## Typography

- Prefer the product's existing font system. If no font direction exists, choose fonts for domain fit and hierarchy rather than defaulting to Inter, Roboto, Arial, or system fonts.
- Pair a distinctive display face with a readable body face only when the product can support the extra asset and visual personality.
- Keep type scales stable across responsive breakpoints. Do not use viewport-width font scaling for normal UI text.

## Placeholders And Data

- Do not fabricate customer logos, testimonials, metrics, awards, or user data unless the user explicitly asks for fictional content.
- Use honest placeholders for missing media or unknown assets, then structure the UI so real assets can be dropped in later.
- Prefer real product state examples from the repo or user-provided material when demonstrating UI states.

## Visual QA Checklist

Before delivery, check the relevant items:

- The UI renders correctly at the requested viewports, including mobile when applicable.
- Text does not overlap, clip, or overflow its container.
- Interactive elements have hover, focus, active, disabled, loading, and error states where the workflow needs them.
- Colors come from the declared or existing design system.
- Visual assets load and are not stretched, blurred, or cropped in a way that hides the subject.
- Layout dimensions are stable for fixed-format elements such as boards, toolbars, tiles, counters, slide stages, and device frames.
- The browser console has no relevant errors or warnings.
- The final result avoids generic AI design cliches and fits the product's actual domain.

## Reference

For broad visual frontend work, high-risk redesigns, landing pages, dashboards, prototypes, slide-like HTML artifacts, or UI polish passes where the aesthetic direction matters, also consult `references/web-design-quality.md`. It adds Claude Design-inspired guidance adapted for Codex: design-context gathering, lightweight design-system declaration, v0 draft strategy, OKLCH/token guidance, anti-cliche checks, placeholder rules, and a visual delivery checklist.
