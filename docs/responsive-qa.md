# Responsive QA Checklist

Status: MVP 1 manual test checklist  
Scope: Private workbook, take-home list, theme controls, and browser print entry points

## Target Viewports

- Android phone: 360 x 800 CSS pixels, touch input, portrait orientation
- Android large phone: 412 x 915 CSS pixels, touch input, portrait orientation
- Desktop narrow: 768 x 900 CSS pixels, keyboard and mouse
- Desktop wide: 1440 x 1000 CSS pixels, keyboard and mouse

## Private Workbook

- Page loads without horizontal scrolling.
- Header navigation remains usable and does not overlap workbook controls.
- Workbook toolbar stacks cleanly on phone widths.
- Progress count and progress bar remain visible.
- Section navigation cards wrap without truncating section names.
- Section jump links move focus target into view below the sticky toolbar.
- Readiness choices are large enough for touch input on Android.
- Readiness choices wrap to two columns on phone widths.
- Safe note fields fit the viewport and can be resized on desktop.
- Conditional guardian question is hidden before the dependents question is answered.
- Conditional guardian question appears after `Yes` or `Not sure` for dependents.
- Conditional guardian question stays hidden after `No` for dependents.
- `Need professional help` generates a follow-up task with a professional-help flag.

## Private Data Handling

- Device saving starts off.
- Save status announces that unsaved answers are lost when the tab closes.
- Enabling device save updates the visible save status.
- Disabling device save removes local storage for the workbook.
- Clear session resets answers, notes, generated tasks, and device-save state.
- Unsaved sessions show the inactivity auto-clear status.
- Device-saved sessions show that inactivity auto-clear is paused.

## Take-Home List

- Task cards fit the phone viewport without horizontal scrolling.
- Official resource links wrap instead of overflowing.
- Priority labels remain readable in light and dark modes.
- Empty task-list state is understandable before any answers are selected.

## Print Entry Points

- `Print / save full workbook` opens browser print with workbook and take-home content.
- `Print / save take-home list` opens browser print with only take-home content.
- Printed links include URLs.
- Print output is legible in black and white.

## Keyboard And Accessibility Smoke Test

- Tab order reaches primary navigation, workbook controls, section links, answers, notes,
  print buttons, and clear-session button.
- Visible focus indicators appear on section links, answer choices, note fields, and buttons.
- `aria-live` save and inactivity status changes are announced by screen readers.
- Motion is minimal; progress bar changes are not required to convey meaning.

## Current Automated Coverage

- `tests/test_web.py` verifies the private workbook has no form submission target.
- `tests/test_web.py` verifies workbook JavaScript only fetches the public catalog.
- `tests/test_web.py` verifies responsive CSS hooks for toolbar stacking, choice wrapping,
  print output, and focus-visible styles.
