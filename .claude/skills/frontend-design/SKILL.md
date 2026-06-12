---
name: spendly-ui-designer
description: >
  Generates modern, production-ready UI components and pages for Spendly, a personal expense tracker (Flask app with Jinja templates, plain HTML/CSS, light-mode fintech SaaS style). Use this skill whenever the user asks to design, create, build, redesign, restyle, or improve any page or component for Spendly, such as "design the dashboard", "create UI for the add-expense form", "build a component for transaction list", or "redesign the settings page". Also trigger for general Spendly frontend work including layouts, cards, navbars, modals, charts/summary widgets, empty states, and icon usage. Always check existing templates/static files for consistency before generating new markup.
---

# Spendly Frontend UI Designer

Generates clean, modern, fintech-style UI for Spendly (Flask + Jinja templates, plain HTML/CSS, no framework). Output must be production-ready and consistent with the existing project.

## Workflow

1. **Check existing design first.** Before writing anything, look at the project's existing templates and CSS:
   - `templates/` for HTML/Jinja structure and existing components
   - `static/css/` for current colors, fonts, spacing, naming conventions
   - If the user attached screenshots/photos of the existing UI, study them
   - If no existing styles are found and nothing is provided, ask the user for a reference (screenshot or file) before inventing a new visual language. Only fall back to the default style guide below if the user says there's nothing to match or explicitly wants a fresh look.

2. **Clarify scope** if not given: which page/component, any data fields, constraints (e.g. must fit existing navbar), and whether this is a new file or an edit to an existing one.

3. **Generate output** in this order:
   - **UI Structure (brief)** — layout outline, key sections, and notable UX decisions (2-6 bullet points max, no walls of text)
   - **Code** — HTML/Jinja template + CSS (separate `<style>` or CSS file matching project convention), modular and minimal
   - Note any new icon dependencies if introduced

## Default Style Guide (use only if no existing styles found)

Light-mode fintech SaaS aesthetic:

- **Layout**: Card-based, 8px spacing grid (multiples of 8px for padding/margin/gaps)
- **Corners**: `border-radius: 12px` for cards, `8px` for buttons/inputs
- **Shadows**: Subtle — `box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)`
- **Colors**:
  - Background: `#F8F9FB`
  - Card surface: `#FFFFFF`
  - Primary text: `#1A1D29`
  - Secondary text: `#6B7280`
  - Border: `#E5E7EB`
  - Accent (primary action / income): `#22C55E`
  - Expense/negative: `#EF4444`
  - Brand/interactive: `#4F46E5`
- **Typography**: System font stack (`-apple-system, "Segoe UI", Roboto, sans-serif`). Headings semi-bold, body regular, numeric values (amounts) tabular/monospace-leaning weight for alignment
- **Spacing**: Generous whitespace between cards (16-24px gaps), comfortable padding inside cards (16-24px)

## Icons

Use Lucide icons (lightweight SVG, inline or via CDN script) for actions, categories, and navigation. Pick icons that semantically match the content (e.g. wallet for balance, arrow-up-right for income, arrow-down-right for expense, tag for category). Don't overuse icons — only where they aid scanability.

## Code Quality Rules

- Modular: one component/page per output, reusable class names (e.g. `.expense-card`, `.summary-widget`), no inline styles unless trivial
- Minimal boilerplate: don't regenerate the whole base layout unless asked — produce the block/component that fits into the existing `{% block content %}` or equivalent
- Avoid `!important`, deeply nested selectors, and magic numbers not on the 8px grid
- Responsive: mobile-first or at least graceful down to ~375px width using flexbox/grid

## Avoid

- Generic/dated UI (heavy gradients, default browser form styling, Bootstrap-default look)
- Unstructured code dumps without the UI Structure summary
- Inventing a new color palette or font stack if the project already has one — match it
- Overly clever animations or effects that don't serve usability