# Figma Implementation Examples

This document provides detailed step-by-step examples for implementing Figma designs. Use these as references when implementing similar components or layouts.

## Example 1: Implementing a Button Component

**User Input:** "Implement this Figma button component: https://figma.com/design/kL9xQn2VwM8pYrTb4ZcHjF/DesignSystem?node-id=42-15"

### Step-by-Step Workflow

**Step 1: Extract Node Information**
- Parse URL: `fileKey=kL9xQn2VwM8pYrTb4ZcHjF`, `nodeId=42-15`
- Verify node ID format (uses `-` separator)

**Step 2: Fetch Design Context**
- Run `get_design_context(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42-15")`
- Review the returned data:
  - Button dimensions (width, height, min/max constraints)
  - Padding values (top, right, bottom, left)
  - Border radius
  - Background colors and fills
  - Typography (font family, size, weight, line height)
  - Text color
  - Border properties (if any)
  - Shadow/effect properties (if any)
  - Interactive states (hover, active, disabled)

**Step 3: Capture Visual Reference**
- Run `get_screenshot(fileKey="kL9xQn2VwM8pYrTb4ZcHjF", nodeId="42-15")`
- Save screenshot for reference
- Note visual details: exact spacing, color shades, shadow depth

**Step 4: Download Assets**
- Check if button contains any icons
- If present, download icon assets from Figma MCP server
- Use localhost URLs directly

**Step 5: Check Existing Components**
- Search for existing button components in project
- Review their APIs (props, variants, usage)
- Determine if existing component can be extended or new component needed

**Step 6: Map Design Tokens**
- Map Figma colors to project color tokens:
  - Example: Figma `#007AFF` → Project `colors.primary` or `colors.primary-500`
  - Example: Hover state `#0056CC` → Project `colors.primary-hover` or `colors.primary-600`
- Map Figma spacing to project spacing tokens:
  - Example: Figma `16px` padding → Project `spacing.medium` or `spacing[4]`
- Map Figma typography to project typography scale:
  - Example: Figma `16px/24px Inter Medium` → Project `typography.body.medium`

**Step 7: Implement Component**
- Create or extend button component
- Apply design tokens (colors, spacing, typography)
- Implement interactive states (hover, active, disabled, focus)
- Add appropriate TypeScript types for props
- Add JSDoc comments

**Step 8: Verify Against Screenshot**
- Compare implementation side-by-side with screenshot
- Verify:
  - Padding matches exactly
  - Border radius matches
  - Colors match (including opacity)
  - Typography matches (font, size, weight, line height)
  - Shadows/effects match
  - Interactive states match design
  - Accessibility (focus states, keyboard navigation)

**Result:** Button component matching Figma design, integrated into project design system with proper TypeScript types and documentation.

---

## Example 2: Building a Dashboard Layout

**User Input:** "Build this dashboard: https://figma.com/design/pR8mNv5KqXzGwY2JtCfL4D/Dashboard?node-id=10-5"

### Step-by-Step Workflow

**Step 1: Extract Node Information**
- Parse URL: `fileKey=pR8mNv5KqXzGwY2JtCfL4D`, `nodeId=10-5`

**Step 2: Fetch High-Level Structure**
- Run `get_metadata(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-5")` to understand page structure
- Review node tree to identify main sections:
  - Header section (node ID: `10-6`)
  - Sidebar section (node ID: `10-7`)
  - Content area (node ID: `10-8`)
  - Card section (node ID: `10-9`)

**Step 3: Fetch Design Context for Each Section**
- Run `get_design_context(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-6")` for header
- Run `get_design_context(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-7")` for sidebar
- Run `get_design_context(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-8")` for content area
- Run `get_design_context(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-9")` for card section

**Step 4: Capture Full Page Screenshot**
- Run `get_screenshot(fileKey="pR8mNv5KqXzGwY2JtCfL4D", nodeId="10-5")` for complete page
- Save for overall layout reference

**Step 5: Download All Assets**
- Download logo from header section
- Download icons from sidebar
- Download chart images or illustrations from content area
- Download card images
- Use localhost URLs directly

**Step 6: Build Layout Structure**
- Use project's layout primitives (Grid, Flexbox, Container components)
- Implement responsive layout based on Figma constraints
- Set appropriate breakpoints matching Figma design

**Step 7: Implement Each Section

**Header:**
- Check for existing header component
- Implement navigation, logo, user menu
- Map design tokens
- Ensure responsive behavior

**Sidebar:**
- Check for existing sidebar component
- Implement navigation items
- Map design tokens
- Ensure collapsible behavior if design requires

**Content Area:**
- Implement main content layout
- Use existing card components where possible
- Map design tokens
- Ensure proper spacing and alignment

**Card Section:**
- Check for existing card components
- Extend or create cards as needed
- Map design tokens
- Ensure consistent styling

**Step 8: Integrate Components**
- Assemble all sections into dashboard layout
- Ensure proper spacing between sections
- Validate responsive behavior
- Test interactive elements

**Step 9: Verify Responsive Behavior**
- Test at different breakpoints (mobile, tablet, desktop)
- Verify layout matches Figma constraints
- Ensure components adapt correctly
- Check for overflow issues

**Step 10: Final Validation**
- Compare complete implementation with screenshot
- Verify all sections match design
- Test all interactive states
- Verify accessibility
- Check cross-browser compatibility

**Result:** Complete dashboard matching Figma design with responsive layout, proper component reuse, and full integration with project design system.

---

## Example 3: Implementing a Form Component

**User Input:** "Implement this form from Figma: https://figma.com/design/abc123/Forms?node-id=20-10"

### Step-by-Step Workflow

**Step 1: Extract Node Information**
- Parse URL: `fileKey=abc123`, `nodeId=20-10`

**Step 2: Fetch Design Context**
- Run `get_design_context(fileKey="abc123", nodeId="20-10")`
- Review form structure:
  - Form container properties
  - Input field designs
  - Label styles
  - Button styles
  - Error message styles
  - Validation states

**Step 3: Get Child Node Details**
- Run `get_metadata(fileKey="abc123", nodeId="20-10")` to see form fields
- Fetch individual input fields if needed:
  - Text input (node ID: `20-11`)
  - Email input (node ID: `20-12`)
  - Password input (node ID: `20-13`)
  - Submit button (node ID: `20-14`)

**Step 4: Capture Visual Reference**
- Run `get_screenshot(fileKey="abc123", nodeId="20-10")`
- Note spacing between fields, label positioning, error state appearance

**Step 5: Check Existing Form Components**
- Search for existing input components
- Check form validation utilities
- Review form state management patterns

**Step 6: Map Design Tokens**
- Map input styles (border, padding, typography)
- Map label styles
- Map error message styles
- Map button styles (submit button)

**Step 7: Implement Form**
- Use existing input components or extend them
- Implement form validation
- Add error states matching Figma design
- Ensure proper accessibility (labels, ARIA attributes)
- Implement proper focus states

**Step 8: Verify**
- Compare with screenshot
- Test all states (default, focus, error, disabled)
- Verify accessibility
- Test form submission flow

**Result:** Form component matching Figma design with proper validation, accessibility, and integration with project patterns.