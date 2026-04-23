# Web Design Quality Reference

Use this reference for broad visual frontend work: landing pages, dashboards, prototypes, HTML slide decks, data visualizations, UI polish passes, and new product surfaces.

## Design Context Order

Prefer context in this order:

1. Repo code, existing components, theme files, tokens, CSS variables, Tailwind config, Storybook, or design-system packages.
2. User-provided Figma links, screenshots, brand guidelines, copy docs, and product specs.
3. Existing production pages from the same product.
4. Comparable products in the same domain.
5. A temporary design system based on the task's audience and domain.

When adding to an existing UI, first describe the current visual vocabulary: color usage, density, radius, elevation, icon style, motion style, content tone, and responsive behavior. New UI should look like it belongs in the same product unless the user asks for a redesign.

## V0 Draft Strategy

Use an early v0 when a task has broad visual uncertainty, multiple possible directions, or high rework risk. A v0 should include:

- A real viewable layout.
- The proposed token system.
- Major sections and component silhouettes.
- Honest placeholders such as `[image]`, `[chart]`, `[icon]`, or `[customer quote]`.
- Explicit assumptions that affect visual direction.

Do not overuse this for narrow codebase edits. If the task is a focused component change, implement directly after reading the surrounding UI.

## Design System Note

For substantial work, write a short note before implementation:

```markdown
Design direction:
- Product context:
- Audience and tone:
- Color system:
- Typography:
- Spacing:
- Radius and elevation:
- Motion:
- Assets and placeholders:
- Responsive rules:
```

If the product already has tokens, state which existing tokens or component conventions will be reused.

## OKLCH Guidance

OKLCH is useful for creating consistent perceived brightness across colors. When supported by the stack, derive palettes with variables:

```css
:root {
  --brand-hue: 252;
  --brand: oklch(0.55 0.2 var(--brand-hue));
  --brand-strong: oklch(0.45 0.22 var(--brand-hue));
  --brand-soft: oklch(0.88 0.07 var(--brand-hue));
  --neutral-50: oklch(0.98 0.003 var(--brand-hue));
  --neutral-900: oklch(0.18 0.01 var(--brand-hue));
}
```

Use OKLCH as a tool, not a mandate. If the repo uses Tailwind tokens, CSS custom properties, HSL, Sass variables, or a component library theme, fit the existing system.

## Anti-Cliche Checklist

Avoid these unless the product context specifically calls for them:

- Purple/pink/blue gradient backgrounds used as the whole visual idea.
- Large rounded white cards on pale gray with no domain signal.
- Blue primary buttons as the default answer to every interface.
- Left-border accent cards repeated across unrelated content.
- Emoji used as icons in production UI.
- Fake customer logos, testimonials, awards, statistics, or dashboards.
- Abstract SVG blobs, gradient orbs, and generic background meshes that do not explain the product.
- Reusing the same font and palette across unrelated products.

The replacement is not always "more decoration." Often the right fix is stronger typography, better spacing, denser information design, better imagery, or a clearer component hierarchy.

## Interaction And Motion

- Use motion to explain state change, reinforce hierarchy, or create one memorable moment.
- Prefer CSS transitions and animations for simple UI. Use the project's existing motion library if it has one.
- Keep durations purposeful: fast for controls, slower for hero reveals or storytelling.
- Respect reduced-motion preferences for large or continuous effects.
- Include keyboard focus states for interactive controls.

## Placeholder Rules

Use placeholders honestly when content or assets are missing:

- `[image]` for missing imagery.
- `[icon]` for missing iconography when the icon set is unknown.
- `[chart data]` for unavailable metrics.
- `[customer quote]` only when the user wants a testimonial slot, not a fabricated quote.

Structure placeholders so they can be replaced without redesigning the page.

## Delivery Checklist

- Target viewports render without overlap or overflow.
- Text is readable and does not rely on viewport-width scaling.
- Repeated UI elements have stable dimensions.
- Controls have appropriate hover, focus, active, disabled, loading, and error states.
- Color choices come from the declared or existing system.
- Images and media show the relevant subject and are not generic atmosphere when inspection matters.
- Console is clean of relevant frontend errors.
- The result has a clear domain signal in the first viewport for product, venue, portfolio, brand, and object-focused pages.
