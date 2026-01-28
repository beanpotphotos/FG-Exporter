# Fantasy Grounds Character Exporter

**A tool to convert Fantasy Grounds Unity (FGU) XML exports into high-fidelity, logic-enriched D&D 5e PDF character sheets.**

![Logo](https://via.placeholder.com/150) *(You can upload your logo.png to the repo and link it here if you like)*

## Description
This tool solves the "PDF Export" problem for Fantasy Grounds Unity. It parses the raw XML character export, applies D&D 5e specific logic (bonus calculations, spell save DCs, weapon formatting), and generates a clean, printable vector PDF.

It goes beyond simple data dumping by understanding the *semantics* of the D&D 5e ruleset (e.g., separating "Actions" from "Spells", formatting dice strings like `1d6 + 3`, and calculating total attack bonuses).

## Features
-   **Intelligent Parsing**: Extracts data from standard FGU XML exports.
-   **Hexagonal Architecture**: Logic is separated from input/output, ensuring accurate math.
-   **Advanced Damage Calculation**:
    -   Automatically calculates total attack bonuses (Stat + Prof + Magic).
    -   Formats damage strings nicely (e.g., `1d8 + 4 piercing`).
    -   Handles complex magic items and "DamageData" subtrees.
-   **Spellbook Generation**: creates a dedicated "Spells & Magic" page with dynamic pagination.
-   **modern GUI**: A dark-themed, responsive user interface.
-   **Dual Output**: Generates both **PDF** (printable) and **Markdown** (text-based) formats.

## Usage

### 1. The Easy Way (Executable)
1.  Download the latest `FantasyGroundsExporter.exe` from the [Releases](../../releases) page.
2.  Run the executable.
3.  Click **Browse XML...** and select your character's `.xml` file (exported from FGU via `/exportchar`).
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

## Interpreting the Output
The PDF is designed to be "Action First". 
-   **Page 1**: Core Stats, Skills, and Weapons.
-   **Page 2**: Feature Dump (Class features, Racial traits).
-   **Page 3+**: Spells & Magic Services (if applicable).

## Disclaimer
**Beta Software (v0.9)**
This tool handles inconsistent data structures by making "best effort" guesses based on D&D 5e rules. While tested with standard classes (Fighter, Wizard, multi-classing), heavily customized community rulesets or homebrew items with non-standard XML structures might render oddly.

## License
MIT License. Free to use, fork, and mod.
