# Fantasy Grounds Character Exporter

**A tool to convert Fantasy Grounds Unity (FGU) XML exports into high-fidelity, logic-enriched D&D 5e PDF character sheets.**

## About
Converts Fantasy Grounds XML files into PDFs or Markdown. It was developed with Google Antigravity as an AI-programming partner. This is a standalone Python executable; no AI is used to convert. It is mostly accurate and functional for D&D 5e data. I'm not a programmer, I just love Fantasy Grounds and D&D.

## Features
-   **Intelligent Parsing**: Extracts data from standard FGU character XML exports.
-   **Hexagonal Architecture**: Logic is separated from input/output, ensuring accurate math.
-   **Advanced Damage Calculation**:
    -   Automatically calculates total attack bonuses (Stat + Prof + Magic).
    -   Formats damage strings nicely (e.g., `1d8 + 4 piercing`).
    -   Handles complex magic items and "DamageData" subtrees.
-   **modern GUI**: A dark-themed, responsive user interface.
-   **Dual Output**: Generates both **PDF** (printable) and **Markdown** (text-based) formats.

## Usage

### 1. The Easy Way (Executable)
1.  Download the latest `FantasyGroundsExporter.exe` from the [Releases](../../releases) page.
2.  Run the executable.
3.  Click **Browse XML...** and select your character's `.xml` file (exported from FGU via `/exportchar`) or using the Export Record in the top left of the character sheet.
4.  Select **dnd5e** as the Logic Engine.
5.  Click **Generate PDF**.

### 2. The Developer Way (Python)
If you want to run from source:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI
python gui.py

# OR Run the CLI
python main.py -i "my_character.xml" -f pdf
```

## Disclaimer
**Beta Software (v0.9)**
This tool handles inconsistent data structures by making "best effort" guesses based on D&D 5e rules. While tested with standard classes (Fighter, Wizard, multi-classing), heavily customized community rulesets or homebrew items with non-standard XML structures might render oddly.

## License
MIT License. Free to use, fork, and mod.
