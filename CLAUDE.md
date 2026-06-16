# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

---

## 5. Explaining Concepts (Project-Specific)

When the user asks for an explanation of a technology or concept, illustrate it with **Spring Boot** elements as the example.

- Ground abstract ideas in concrete Spring Boot constructs — e.g. `@RestController`, `@Service`, `@Repository`, dependency injection / `@Autowired`, `@Configuration`, `application.yml`, the embedded Tomcat servlet container, Spring Data JPA, `@Transactional`, auto-configuration, starters.
- Map the general concept to its Spring Boot counterpart so the user can anchor learning to a familiar framework.
- If the concept has no natural Spring Boot analogy, say so explicitly rather than forcing a misleading example.

---

## 6. Coding Conventions (Project-Specific)

**Use descriptive variable names. Follow PEP 8.**

- No single-letter names except the narrow, conventional cases: loop counters (`i`, `j`), coordinates (`x`, `y`), or a throwaway value (`_`).
- This applies to comprehension and lambda variables too — prefer `for block in content` over `for b in content`, `for part in parts` over `for p in parts`.
- Do not abbreviate to save characters/tokens. Readability over terseness.
- Naming case (PEP 8): functions/variables `lower_snake_case`, classes `CapWords`. A `CapWords` name normally signals a class — don't use it for plain functions.

---

## 7. Canonical Structure — Best Practice over Simplification (Project-Specific)

**The user is learning Python. Always write code in the canonical, widely-recommended way — even when it is more verbose than a shortcut.** Arbitrary simplifications rob the user of the chance to learn the standard pattern.

- **Default to the conventional/officially-recommended approach.** When several approaches exist, pick the standard one and briefly say why. Do not invent terser-but-nonstandard variants.
- **Do NOT simplify or collapse structure for brevity.** Examples to keep as-is, never fold away:
  - `src/` layout — code lives under `src/rnd_onboarding/`, installed as a package (editable via `uv sync`).
  - Packages keep their `__init__.py`. A subpackage folder (e.g. `prompts/`) stays a package even if it currently holds one file — do not flatten it into a single `.py` module to "save a file".
- **No structural churn.** Do not repeatedly reorganize the project layout. Once a canonical structure is in place, keep it stable; restructure only when the user explicitly asks.
- If a simpler form is genuinely better, *propose* it and explain the trade-off — but do not apply it unilaterally.

