# Advanced Frontend Design Patterns

Use these patterns when a frontend task benefits from a richer artifact than a static page. They are implementation prompts and lightweight templates, not mandatory architecture.

## Responsive Slide Stage

Use for HTML presentations, walkthroughs, fixed-size demos, and visual narratives.

Key rules:

- Treat slide numbers shown to users as 1-indexed.
- Give each slide or screen a stable `data-screen-label`, such as `01 Title`, `02 Problem`, or `03 Demo`.
- Keep controls outside the scaled stage so they remain usable on small screens.
- Persist the current slide in `localStorage` for iterative review.

Minimal structure:

```html
<main class="deck-shell">
  <section class="stage" aria-live="polite">
    <article class="slide is-active" data-screen-label="01 Title"></article>
    <article class="slide" data-screen-label="02 Context"></article>
  </section>
  <nav class="deck-controls" aria-label="Slide controls">
    <button type="button" data-action="prev">Previous</button>
    <span class="slide-count">1 / 2</span>
    <button type="button" data-action="next">Next</button>
  </nav>
</main>
```

## Device And Browser Frames

Use frames when the user asks for a prototype, mobile flow, app mockup, or browser-based product concept.

Guidelines:

- Use frames to clarify context, not as decoration.
- Keep the simulated device dimensions stable with `aspect-ratio`.
- Do not hide important UI under decorative chrome.
- Use real app states inside the frame: empty, loading, error, success, and selected states when relevant.

React shape:

```jsx
function DeviceFrame({ title, children }) {
  return (
    <section className="device-frame" aria-label={title}>
      <div className="device-status" aria-hidden="true" />
      <div className="device-screen">{children}</div>
      <div className="device-home" aria-hidden="true" />
    </section>
  );
}
```

## Tweaks Panel

Use a tweaks panel when exploring multiple design variants, color systems, copy tone, density, or motion.

Controls should map to real design decisions:

- Theme or palette.
- Density.
- Type scale.
- Motion intensity.
- Content emphasis.
- Layout variant.

Keep tweak state serializable so it can be persisted:

```jsx
const defaultTweaks = {
  theme: "light",
  density: "comfortable",
  motion: "standard",
  layout: "editorial"
};
```

Avoid turning every CSS value into a control. A good tweaks panel exposes meaningful choices, not implementation noise.

## Animation Timeline

Use timeline helpers for demos, animated explainers, hero sequences, and interaction prototypes.

```jsx
function useTimeline(durationMs = 5000, playing = true) {
  const [progress, setProgress] = React.useState(0);

  React.useEffect(() => {
    if (!playing) return;
    let frame = 0;
    let start = 0;

    const step = (timestamp) => {
      if (!start) start = timestamp;
      setProgress(((timestamp - start) % durationMs) / durationMs);
      frame = requestAnimationFrame(step);
    };

    frame = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frame);
  }, [durationMs, playing]);

  return progress;
}

const easing = {
  easeOut: (t) => 1 - Math.pow(1 - t, 3),
  easeInOut: (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2)
};

function interpolate(t, from, to, curve = easing.easeInOut) {
  const p = curve(Math.max(0, Math.min(1, t)));
  return from + (to - from) * p;
}
```

Respect `prefers-reduced-motion` for large, looping, or parallax effects.

## Design Canvas

Use a design canvas when comparing multiple visual directions side by side.

Each option should vary along a clear axis:

- Layout.
- Visual density.
- Palette.
- Interaction model.
- Typography.
- Information hierarchy.

```jsx
function DesignCanvas({ options }) {
  return (
    <section className="design-canvas" aria-label="Design options">
      {options.map((option) => (
        <article className="design-option" key={option.id}>
          <header>
            <span>{option.label}</span>
            <strong>{option.direction}</strong>
          </header>
          {option.preview}
        </article>
      ))}
    </section>
  );
}
```

Do not present near-identical variants. Users need meaningful contrast to make decisions.

## Theme Toggle

Use a theme toggle only when dark and light modes are both part of the product requirement or design exploration.

Guidelines:

- Derive both themes from the same token model.
- Store the user's choice.
- Respect `prefers-color-scheme` as the initial value.
- Keep contrast accessible in both modes.

```jsx
function useThemeMode() {
  const getInitial = () =>
    localStorage.getItem("theme") ||
    (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

  const [theme, setTheme] = React.useState(getInitial);

  React.useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("theme", theme);
  }, [theme]);

  return [theme, setTheme];
}
```

## Data Visualization

Use visualization when it helps users compare, diagnose, or decide.

Rules:

- Pick the simplest chart that answers the question.
- Use real units, labels, legends, and empty/error states.
- Keep color meaning stable across charts.
- Avoid chart decoration that makes values harder to read.
- Use tables alongside charts when exact comparison matters.

## Color And Font Starting Points

Use these only when there is no brand or design system. Drop them immediately when the product provides a visual direction.

| Direction | Palette Seed | Typography Direction | Good Fit |
| --- | --- | --- | --- |
| Technical tool | Cool blue or cyan in OKLCH | Geometric sans + readable mono | Dev tools, observability, AI infrastructure |
| Editorial | Warm neutral or muted ink | Serif display + quiet sans | Essays, media, research, portfolios |
| Premium utility | Near-black neutral + restrained accent | Precise sans with strong numerals | Finance, consulting, security |
| Consumer energy | Coral, green, or yellow accent | Friendly sans with rounder forms | Commerce, creator tools, social products |
| Dense professional | Teal, graphite, or restrained blue | Compact sans + tabular numerals | Dashboards, B2B workflows, analytics |

Avoid using the same palette and font pair repeatedly across unrelated products. The first viewport should quickly signal the actual domain.
