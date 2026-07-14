<!-- @author Codex (K2.6) -->

# Rule Extraction Guide

Use this guide to turn provided App screenshots into design experience and reusable rules for future pages.

## Extraction Mindset

- Screenshots are samples, not templates. Extract reusable design decisions, not page-specific content.
- Convert visual facts into semantic rules. A color value becomes a role; a card size becomes a layout principle; a button state becomes an interaction rule.
- Separate system rules from local exceptions. Keep repeated patterns; mark rare decorative choices as exceptions unless they serve a clear reusable role.
- Always include negative guidance. A rule without "不要怎么用" is too weak for handoff.

## What to Observe

- Product temperament: trustworthy, efficient, calm, urgent, premium, playful, operational, content-heavy, or decision-heavy.
- User pressure: browsing, comparing, filling, confirming, paying, correcting errors, waiting for status, reviewing after completion.
- Information density: how much text appears per screen, which content is emphasized, and whether scanning or reading is primary.
- Layout rhythm: page margin, card width, card padding, section gap, inner row gap, sticky areas, safe area, and scroll behavior.
- Component hierarchy: top bar, status block, notice bar, information card, form row, tag/chip, primary action, secondary action, warning area, error row, floating entry.
- State language: default, selected, active, disabled, loading/waiting, success, warning, error, destructive, payment/commitment.
- Brand cues: which color, typography, icon, illustration, or gradient carries recognition.
- Inconsistency: repeated values that are close but not identical, such as multiple greens, multiple warning oranges, similar radii, or inconsistent text weights.

## How to Convert Observations Into Rules

- Color: group raw values by semantic role such as brand, success, warning, danger, price, link, text primary, text secondary, background, surface, border.
- Typography: define type levels by role, not by element names. Example roles: page title, section title, body value, body label, helper text, caption, numeric emphasis.
- Spacing: define a scale and attach it to layout jobs. Example roles: page margin, card padding, row gap, section gap, compact inline gap.
- Radius: define by component role. Example roles: card, inner panel, chip/tag, small button, pill button, floating button.
- Border and shadow: specify when flat separation is enough and when elevation is allowed.
- Components: describe anatomy, sizing, content hierarchy, states, and usage limits.
- Copy: derive tone from task pressure. Confirming and payment moments should be precise; warnings should explain consequence and action; success text should be short and confidence-building.

## Required Rule Format

Use this pattern for each rule:

```markdown
### 规则名称

- 规则：具体、可执行、可量化；必要时给出 token 名称。
- 适用场景：说明在哪些页面、模块、状态或用户任务中使用。
- 不要怎么用：说明禁止混用、过度使用、误用或与当前产品气质冲突的做法。
```

## Inconsistency Checklist

When reviewing screenshots, explicitly check:

- Similar colors with different hex values but same purpose.
- Similar radii used for the same component role.
- Text levels that share size but differ in weight without clear reason.
- Button heights or paddings that vary across equivalent actions.
- Warning and error colors used interchangeably.
- Icon sizes or stroke weights that vary across the same toolbar or list.
- Cards with inconsistent inner padding or section gaps.
- Copy that uses inconsistent terms for the same concept.

For each issue, write:

- `发现`
- `影响`
- `建议统一为`

## Token Naming Guidance

Prefer semantic tokens:

- `--color-brand-primary`
- `--color-brand-primary-pressed`
- `--color-functional-success`
- `--color-functional-warning`
- `--color-functional-danger`
- `--color-price`
- `--color-text-primary`
- `--color-text-secondary`
- `--color-surface-card`
- `--space-page-x`
- `--space-card-padding`
- `--radius-card`
- `--radius-control`
- `--height-button-primary`

Avoid page-specific tokens such as `--color-order-status-title` unless the user is building a component library for that exact domain.
