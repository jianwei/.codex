# Figma Implementation Troubleshooting

This document provides detailed solutions to common problems encountered when implementing Figma designs.

## Issue: Figma Output is Truncated

### Symptoms
- `get_design_context` returns incomplete data
- Missing child elements or properties
- Response seems to cut off in the middle

### Cause
The design is too complex or has too many nested layers to return in a single response. The Figma MCP server has response size limits.

### Solution

**Step 1: Get Metadata First**
```javascript
get_metadata(fileKey=":fileKey", nodeId="1-2")
```

This returns a high-level node map showing the structure without all the detailed properties.

**Step 2: Identify Child Nodes**
From the metadata response, identify the specific child nodes you need:
- Look for main sections (header, sidebar, content, etc.)
- Note the node ID for each section
- Identify which sections are most important for implementation

**Step 3: Fetch Individual Nodes**
Fetch each major section separately:
```javascript
get_design_context(fileKey=":fileKey", nodeId=":childNodeId")
```

**Example Workflow:**
```
1. get_metadata(fileKey="abc123", nodeId="1-2")
   → Returns structure: { header: "1-3", sidebar: "1-4", content: "1-5" }

2. get_design_context(fileKey="abc123", nodeId="1-3")  // Header details
3. get_design_context(fileKey="abc123", nodeId="1-4")  // Sidebar details
4. get_design_context(fileKey="abc123", nodeId="1-5")  // Content details
```

**Prevention:**
- Always start with `get_metadata` for complex designs
- Fetch sections incrementally
- Don't assume you can get everything in one call

---

## Issue: Design Doesn't Match After Implementation

### Symptoms
- Visual differences between implemented code and original Figma design
- Spacing looks incorrect
- Colors don't match
- Typography seems different
- Alignment issues

### Cause
Visual discrepancies can be caused by:
- Incorrect design token mapping
- Missing or incorrect spacing values
- Color conversion issues (RGB vs HEX, opacity handling)
- Typography scale mismatches
- Browser rendering differences

### Solution

**Step 1: Side-by-Side Comparison**
- Place Figma screenshot next to your implementation
- Systematically compare: spacing, colors, typography, alignment

**Step 2: Check Design Context Data**
Review the original `get_design_context` response:
- Verify spacing values (padding, margin, gap) match what you implemented
- Check color values (including opacity/alpha channel)
- Verify typography values (font family, size, weight, line height, letter spacing)
- Check alignment values (text align, flex align, etc.)

**Step 3: Verify Design Token Mapping**
- Ensure Figma colors are correctly mapped to project tokens
- Verify spacing tokens match Figma values
- Check typography scale mapping

**Step 4: Check Browser Rendering**
- Test in different browsers
- Verify CSS properties are being applied correctly
- Check for browser-specific rendering differences

**Step 5: Verify Units and Calculations**
- Ensure pixel values match exactly
- Check for rounding errors in calculations
- Verify rem/em conversions if using relative units

**Common Fixes:**
- Adjust spacing values to match Figma exactly
- Fix color values (check opacity/alpha channel)
- Correct typography values (especially line height)
- Fix alignment properties
- Adjust border radius values
- Fix shadow/effect values

**Prevention:**
- Always reference the screenshot during implementation
- Validate incrementally as you build
- Double-check design token mapping
- Use browser DevTools to inspect computed values

---

## Issue: Assets Not Loading

### Symptoms
- Images/icons not displaying
- Broken image links
- 404 errors on asset URLs
- Placeholder images shown instead of actual assets

### Cause
- Figma MCP server's assets endpoint is not accessible
- Asset URLs are being modified or converted incorrectly
- Network issues preventing asset access
- Asset URLs have expired or are invalid

### Solution

**Step 1: Verify Asset URL**
- Check asset URLs in `get_design_context` response
- Verify the URL is a `localhost` URL from the Figma MCP server
- Ensure the URL is complete and not truncated

**Step 2: Use URL Directly**
- **DO NOT modify or transform the URL**
- Use the provided `localhost` source directly
- Do not convert to a different format
- Do not use placeholder services

**Step 3: Verify MCP Server Accessibility**
- Ensure the Figma MCP server is running and accessible
- Check server logs for errors
- Verify network connection

**Step 4: Check Asset Format**
- Verify the asset format (PNG, JPG, SVG, WebP)
- Ensure the browser supports the format
- Check for CORS issues if loading from a different origin

**Step 5: Alternative Approaches**
If assets still won't load:
- Re-fetch design context to get fresh URLs
- Check if you need to download assets and serve them locally
- Verify asset permissions in the Figma file

**Prevention:**
- Always use `localhost` URLs from the Figma MCP server directly
- Never modify or transform asset URLs
- Test asset loading early in implementation
- Keep MCP server running and accessible

---

## Issue: Design Token Values Differ From Figma

### Symptoms
- Project's design system tokens have different values than Figma design
- Colors don't exactly match
- Spacing doesn't match
- Typography scales differ

### Cause
- Project's design system was created independently from Figma
- Design tokens have evolved separately
- Different design systems or style guides
- Legacy design system values

### Solution

**Step 1: Assess the Differences**
- Compare Figma values with project token values
- Identify which tokens differ significantly
- Determine the impact on visual appearance

**Step 2: Decision Framework

**For Colors:**
- If difference is minor (< 5%): Use project tokens, document the deviation
- If difference is significant (> 5%): Consider creating new token variants or use Figma values directly
- Always maintain consistency within the project

**For Spacing:**
- Prioritize project tokens for consistency
- Make minimal adjustments to match visual appearance if needed
- Document any adjustments

**For Typography:**
- Use project typography scale
- Make minimal adjustments to line height or letter spacing if needed
- Maintain readability and accessibility

**Step 3: Implementation Approaches

**Option A: Use Project Tokens (Recommended)**
- Use project design tokens for consistency
- Make minimal adjustments to match visual appearance
- Document deviations in code comments

**Option B: Create Token Variants**
- Create new token variants that match Figma values
- Add to design system if appropriate
- Use sparingly to avoid token proliferation

**Option C: Use Figma Values Directly**
- Use Figma values directly in the component (not recommended)
- Use only when pixel-perfect matching is absolutely necessary
- Document why project tokens weren't used

**Step 4: Document Your Decision**
- Document which approach you chose
- Explain why in code comments
- Note any trade-offs made

**Best Practices:**
- **Prioritize project tokens** to maintain codebase consistency
- **Minimize adjustments** to match visuals when conflicts arise
- **Document clearly** any deviations from standard tokens
- **Stay consistent** - don't mix approaches within the same component

**Prevention:**
- Align design systems with Figma design tokens where possible
- Create a Figma → Project token mapping document
- Regular sync between design and development teams
- Use design tokens consistently across all implementations

---

## Issue: Component Structure Doesn't Match Figma Hierarchy

### Symptoms
- Component structure in code doesn't match Figma layer structure
- Missing nested elements
- Incorrect parent-child relationships
- Layout issues due to structure mismatch

### Cause
- Misunderstanding of Figma layer hierarchy
- Incorrect interpretation of auto-layout
- Missing nested components or groups
- Incorrect component composition

### Solution

**Step 1: Review Figma Structure**
- Use `get_metadata` to see the complete node hierarchy
- Understand parent-child relationships
- Identify groups, frames, and components

**Step 2: Map to Code Structure**
- Map Figma groups → React fragments or containers
- Map Figma frames → React components or sections
- Map Figma components → React components
- Maintain hierarchy in code structure

**Step 3: Verify Auto Layout**
- Check auto-layout settings in design context
- Implement flexbox/grid to match auto-layout behavior
- Verify spacing and alignment match

**Step 4: Test Structure**
- Verify components render correctly
- Check nested elements appear in correct order
- Ensure layout matches Figma design

**Prevention:**
- Always review metadata to understand structure
- Map Figma hierarchy systematically to code structure
- Verify structure matches before adding styles
- Test incrementally as you build

---

## Issue: Interactive States Don't Match Design

### Symptoms
- Hover states look different from Figma
- Active/pressed states don't match
- Focus states are missing or incorrect
- Disabled states aren't styled correctly

### Cause
- Missing interactive state designs in Figma
- Incorrect implementation of state styles
- Missing state variants in design context
- Accessibility requirements not considered

### Solution

**Step 1: Check Design Context**
- Review state variants in `get_design_context` response
- Look for hover, active, disabled, focus states
- Check if states are defined as component variants

**Step 2: Implement Missing States**
- If states exist in Figma: Implement exactly as designed
- If states are missing: Create them based on design system patterns
- Ensure accessibility (focus states, keyboard navigation)

**Step 3: Test All States**
- Test hover states
- Test active/pressed states
- Test focus states (keyboard navigation)
- Test disabled states
- Verify transitions match design

**Step 4: Verify Accessibility**
- Ensure focus indicators are visible
- Verify keyboard navigation works
- Check color contrast for all states
- Ensure states are perceivable

**Prevention:**
- Always check for state variants in design context
- Implement all interactive states
- Test states during implementation
- Ensure accessibility from the start