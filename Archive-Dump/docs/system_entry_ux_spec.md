# System Entry – UX Spec (Draft)

Last updated: 2025-11-02
Owner: Control Room (CustomTkinter)
Scope: Single-page System Entry form with guided, explicit inputs and schema-aware hints.

## Goals
- Fast, foolproof data entry: every field is filled (explicit value or "N/A").
- Clear guidance: inline helper text + contextual side panel.
- Low-friction media workflow: pick a photo anywhere; app copies into `photos/` with a safe name and stores a relative path.
- Accessibility: large-text toggle and keyboard-first flow.
- Validation: real-time feedback; Save disabled until required items are valid.

## Target Platform
- Desktop app (Python + CustomTkinter).
- iOS PWA unaffected (display-only); this spec focuses on desktop System Entry.

## Information Architecture

Sections (single page):
1) System Basics
   - System Name (required; free text)
   - Region (dropdown; from data JSON)
   - Coordinates X (required; integer/float)
   - Coordinates Y (required; integer/float)

2) World Profile
   - Sentinel Activity (dropdown: None, Low, Medium, High, Extreme)
   - Fauna (dropdown: None, Low, Medium, High)
   - Flora (dropdown: None, Low, Medium, High)
   - Planets (interactive list: chips with add/remove)

3) Base & Media
   - Base Location (free text; e.g., “Portal near Wos”)
   - Photo (button: Choose file…) → copies file to `photos/` → stores `photos/<safe-name>.ext` or "N/A"

4) Notes (multiline text)

5) Actions
   - Save (primary). Disabled until: Name present and Coordinates valid.
   - Cancel (secondary). Discards changes (with confirmation if dirty).

Side Panel: Contextual Help
- Sticky right panel showing per-field guidance and examples.
- Auto-populated from schema where possible (field descriptions, enums, ranges).

## Field Definitions & Validation

- System Name
  - Input: string. Placeholder: “e.g., Adam”
  - Rules: required; trim; disallow only whitespace; allow hyphens/spaces.
  - Default on blank Save: prevent Save (error shown under field).

- Region
  - Input: dropdown (source = regions list from `data.json`).
  - Rules: optional; default "N/A" if not chosen.

- Coordinates X, Y
  - Input: numeric entry (accepts `-` prefix; decimals allowed). Placeholders: “e.g., 123” / “e.g., -45.2”.
  - Rules: required; parseable as float; show inline error on invalid; Save disabled while invalid.

- Sentinel Activity / Fauna / Flora
  - Input: dropdowns. Values: [None, Low, Medium, High, Extreme] (Sentinel) and [None, Low, Medium, High] (Fauna/Flora).
  - Rules: optional; default "N/A" if not chosen.

- Planets
  - Input: add by typing name and pressing Enter; remove via ✕ on chip; keyboard focus returns to input.
  - Rules: allow duplicates? No (warn and ignore if duplicate name). Empty list allowed → store [].

- Base Location
  - Input: string. Placeholder: “e.g., Portal by Wos (SE ridge)”
  - Rules: optional; default "N/A" if blank.

- Photo
  - Action: opens file picker (any path). On select, copy file into `photos/` with collision-safe name (e.g., `wos-portal-2.png`).
  - Stored value: relative path (`photos/<file>`) or "N/A" if none.
  - Preview: show filename; open-in-explorer button.

- Notes
  - Input: multiline; optional; default "N/A" if blank.

## Error States
- Inline under field in subtle red with clear message. Example: “Enter a valid number (e.g., 42 or -13.5).”
- Save disabled while System Name empty or Coordinates invalid.
- Global non-blocking banner if schema mismatches on Save.

## Keyboard Flow
- Tab order: Name → Region → X → Y → Sentinel → Fauna → Flora → Planets input → Base → Photo button → Notes → Save.
- Enter on Planets input adds planet; Enter on form (when Save focused) triggers Save.
- Esc on dialogs (photo picker errors) closes.

## Progressive Disclosure
- Advanced notes area is collapsed by default if window height < 800px; expands on click or when focused.

## Contextual Help (Right Panel)
- Shows: field title, short description, example, constraints.
- Source: `data/data.schema.json` where available; fallback to static text below.
- Toggles: “Large text” switch increases UI scale ~1.15x (system-wide within this panel + form labels).

### Static Help Fallback (if schema unavailable)
- System Name: Free text. Keep it recognizable and unique.
- Region: Choose from existing regions or leave N/A.
- Coordinates: Use the galaxy grid coordinates. Decimals permitted.
- Sentinel / Fauna / Flora: Use qualitative levels as observed.
- Planets: Add names you use in the field (nicknames fine).
- Photo: Choose a screenshot; it’ll be copied under `photos/`.

## Wireframes (ASCII)

Layout – Desktop (≥1280px)

+---------------------------------------------------------------+
| System Entry                                 [ Large Text ☐ ] |
+----------------------+------------------------------+---------+
| System Basics        | World Profile                 |  Help   |
|----------------------|-------------------------------|  Panel  |
| Name: [ Adam      ]  | Sentinel: [ Medium  v ]       | ------- |
| Region: [ Core  v ]  | Fauna:    [ Low     v ]       | • Name  |
| X: [ 123 ]  Y:[-45 ] | Flora:    [ High    v ]       |   Use a |
|                      | Planets:  [Wos] [Tal] [+]     |   clear |
|                      |  (type + Enter to add)        |   name… |
|----------------------|-------------------------------|         |
| Base & Media         | Notes                         |         |
| Base: [ Portal…   ]  | [ Multiline box…           ]  |         |
| Photo: [Choose…] [Open]                              |         |
|----------------------|-------------------------------|         |
| [ Cancel ]                           [ Save (disabled) ]       |
+---------------------------------------------------------------+

Layout – Narrow (≤1000px)

[ System Basics ]
[ World Profile ]
[ Base & Media ]
[ Notes ]
[ Help Panel (collapsible) ]

## Visual Style (brief)
- Colors: Deep charcoal background, slate panels, cyan accents (#55E1FF) for primary; subtle greens for success; muted reds for errors.
- Typography: Inter or Segoe UI; 14–16px base; Large Text = +15%.
- Density: Comfortable (8px grid); button heights 36–40px.
- Icons: Minimal; chips use ✕; photo uses folder icon.

## Telemetry / Logging
- Log import/copy errors for photos (source path, target path, exception summary). Mask PII in logs.

## Save Contract
- On Save, produce a complete system record with explicit values: strings or "N/A"; numeric coords as float; planets as array; photo as relative path or "N/A".
- Validate against schema (if present). If failing, show banner and keep form open.

## Open Questions
- Region source of truth: from schema, data.json, or a config list?
- Allow planet reordering? (future)
- Multiple photos per system? (future)
