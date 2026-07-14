---
name: tuniu-design
description: Generate a concrete, reusable Design System from App design ideas plus screenshots or Figma links. Use when asked to summarize design rules, create design guidelines, extract visual language, audit UI consistency, or produce design tokens for any mobile App page or feature based on visual examples.
---

<!-- @author Codex (K2.6) -->

# Tuniu Design

## Overview

Use this skill to generate a Design System that can guide future pages, not to document one provided page. Treat screenshots/Figma nodes as evidence for extracting reusable rules, patterns, constraints, and design red lines.

Read `references/rule-extraction-guide.md` before writing the final spec. It captures the reusable method learned from the provided design samples without binding the skill to those samples.

## Required Workflow

1. Collect visual evidence.
   - Use every provided screenshot or Figma node as source material.
   - Extract measurable details: colors, font sizes, line heights, spacing, grid, card width, button height, radius, border, shadow, icon size, state colors, and layout density.
   - If screenshots are missing, ask for them or clearly mark the output as a provisional concept spec.

2. Judge the product direction.
   - Identify product temperament, target users, and core use scenarios.
   - Base the judgment on visual and interaction evidence, not generic product adjectives.
   - Explain how the UI should feel during high-frequency, high-risk, empty, success, warning, error, and payment/commitment moments when relevant.

3. Extract reusable visual language.
   - Convert observed details into page-agnostic rules.
   - Separate stable rules from one-off decoration.
   - Identify inconsistencies and recommend one canonical rule for each inconsistency.

4. Produce the full Design System.
   - Include all sections:
     - Design principles
     - Color system
     - Typography system
     - Spacing and grid
     - Radius, border, and shadow
     - Core component rules
     - State rules
     - Icon and illustration rules
     - Copy tone rules
     - Forbidden rules/design red lines
   - Every individual rule must include:
     - `规则`
     - `适用场景`
     - `不要怎么用`

5. Finish with implementation tokens.
   - Provide CSS variables.
   - Provide Tailwind `theme.extend` when the user asks for frontend handoff or the project uses Tailwind.
   - Token names must be semantic, for example `--color-brand-primary`, `--color-text-secondary`, `--radius-card`, `--space-page-x`.

6. Verify before responding.
   - Confirm the output is reusable for other pages.
   - Confirm it does not merely describe the sample page.
   - Confirm inconsistencies and design red lines are explicit.
   - Confirm design tokens cover the visible system: colors, typography, spacing, radius, borders, shadows, component sizes, and states.

## Output Shape

Use Chinese unless the user asks otherwise. Use this order:

1. `产品判断`
2. `设计经验提炼`
3. `当前视觉语言归纳`
4. `不一致与风险`
5. `Design System 规范`
6. `Design Tokens`
7. `落地建议`

Prefer specific, reusable guidance. For example:

- Good: `主内容卡片使用 12px 左右页面安全边距，形成移动端可扫描的信息流；适用于订单、表单、权益、费用等高密度信息承载。不要在同一页面混用 8px/16px/20px 随意边距。`
- Bad: `页面整体简洁美观，卡片清晰。`

## Evidence Rules

- Treat the current screenshots/Figma links as the source of truth for the current task only.
- Do not hard-code prior sample page names, node ids, or business modules into the final answer unless the user explicitly asks.
- Use approximate values only when exact values are unavailable; label them as approximate.
- Do not invent a brand direction when the visual evidence already defines one.
- Do not silently normalize inconsistencies. Name the inconsistency, then recommend a canonical token or component rule.
- Do not output only tokens. Human-readable design rules are required.

## Token Requirements

CSS variables must include:

- Brand, functional, text, border, background, surface, overlay colors.
- Font family stack and size/line-height pairs.
- Spacing scale, page margin, card padding, list gap, section gap.
- Radius values for cards, panels, controls, pills, floating buttons, and tags.
- Border widths and elevation/shadow values.
- Component sizing values for top bars, bottom bars, primary buttons, secondary buttons, chips/tags, cards, notice bars, form rows, and error/help text.

Tailwind config should map the same values into `theme.extend.colors`, `fontSize`, `spacing`, `borderRadius`, `boxShadow`, and useful component sizing tokens.
