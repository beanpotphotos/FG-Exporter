# Release Notes v0.9-beta

**Fantasy Grounds Exporter** is a standalone utility for converting Fantasy Grounds Unity character exports (`.xml`) into readable, printable formats.

## Key Features

*   **PDF Generation**: Produces a clean, vector-based PDF optimized for print.
    *   **Action-Oriented Layout**: Prioritizes attacks, actions, and features on the first page.
    *   **Spellbook Generation**: Automatically paginates spells with "Level" headers.
    *   **Smart Layout**: dynamically adjusts column widths for long feature names.
*   **Data Enrichment (D&D 5e)**:
    *   **Math Validation**: Independent calculation of Attack Bonuses and Save DCs based on core stats (Attributes + Proficiency + Item Bonuses).
    *   **String Formatting**: Standardizes output formatting (e.g., converts "d6" to "1d6", ensures signed modifiers like "+5").
    *   **Damage Parsing**: Extracts and formats damage strings from complex nested XML structures, including fallback heuristics for missing data.
*   **Markdown Export**: logic-enriched data in a raw Markdown format for use in other tools or wiki software.
*   **Standalone GUI**: Python-based GUI (`.exe`) with a threaded backend, requiring no external dependencies for the end user.

## Technical Details

*   **Architecture**: Implements a Hexagonal Architecture (Port & Adapters) to separate input parsing (XML) from domain logic (5e Rules) and output rendering (ReportLab).
*   **Enrichment Logic**: Includes a dedicated logic engine for D&D 5e that handles:
    *   Attribute Modifier calculation `(Score - 10) // 2`.
    *   Proficiency Bonus calculation `ceil(Level / 4) + 1`.
    *   Spell Save DC calculation `8 + Prof + CastingMod`.
    *   Weapon Properties parsing.

## Known Limitations (Beta)

*   **Input Dependency**: The quality of the output is strictly dependent on the semantic quality of the Input XML. "Homebrew" items that do not follow standard FGU data structures may not render correctly.
*   **Heuristics**: Fallback logic is used when explicit modifiers are missing (e.g., assuming Strength for Melee weapons if unspecified).
