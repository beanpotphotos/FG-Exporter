# Project Handover: Fantasy Grounds Unity XML to Markdown Converter (Python)

**Expert Programming LLM Taking Over:**

You are now taking over an existing Python project designed to convert character data from Fantasy Grounds Unity (FGU) XML export files into a human-readable Markdown text format. The user, who has no programming experience, requires a robust and functional tool.

---

## 1. Ultimate Goals & High-Level Conceptual Primer

**Overall Project Goal:**
The overarching goal of this project is to provide a user-friendly, reliable tool that seamlessly transforms complex, machine-readable character data from Fantasy Grounds Unity's XML export format into an easily digestible, plaintext Markdown document. This enables the user to quickly view, share, or archive character sheets without needing specialized software or technical understanding of XML.

**Core Problem Addressed:**
Fantasy Grounds Unity exports character data in a highly structured XML format. While precise for application use, this format is verbose, nested, and not intended for direct human consumption. The project aims to solve the problem of inaccessible character data by converting it into a standardized, simple Markdown format.

**Key Concepts for the New AI:**

*   **Fantasy Grounds Unity (FGU) XML:** This is the source data format. FGU XML files are typically well-formed, but feature deep nesting, custom attributes (`type="string"`, `type="number"`), and variable-named elements (e.g., `<id-00001>`, `<id-00002>` for list items). Extracting data requires careful path traversal and handling of these dynamic tags.
*   **Markdown:** This is the target output format. Markdown is a lightweight markup language with plain-text formatting syntax. It prioritizes readability and simplicity, making it ideal for the user's non-technical needs. The conversion involves mapping specific XML data points to Markdown headings, bold text, lists, and paragraphs.
*   **Python as the Conversion Engine:** Python is used for its strong XML parsing capabilities, robust string manipulation, and ease of scripting, making it suitable for transforming structured data from one format to another.
*   **Parameterized Extraction:** The extraction process is driven by a configuration file (`parameters_list.txt`), allowing the user to define what data to extract and from where, without modifying the core Python logic. This enhances flexibility and maintainability.
*   **GUI for User Interaction:** A simple Tkinter-based Graphical User Interface (GUI) provides an intuitive way for the user to select input files and trigger the conversion, abstracting away command-line complexities.

## 2. Mid-Level Methodology & Development Aspects

This section details the structure, components, and current status of the project.

**Project Structure:**

The project is organized into several distinct Python files and a configuration file, promoting modularity and separation of concerns:

*   **`main.py`:**
    *   **Purpose:** Serves as the primary entry point and houses the Tkinter-based Graphical User Interface (GUI).
    *   **Functionality:**
        *   Initializes the GUI window.
        *   Provides "Browse" functionality for selecting the input FGU XML file.
        *   Automatically suggests an output Markdown file name in the same directory as the input XML.
        *   Triggers the data conversion process by calling `process_character_xml` from `character_processor.py`.
        *   Displays success or error messages using Tkinter `messagebox`.
        *   Manages the absolute path resolution for `parameters_list.txt`.
    *   **Key Libraries:** `tkinter`, `os`, `sys`.

*   **`character_processor.py`:**
    *   **Purpose:** Contains the core business logic for reading parameter definitions and orchestrating the XML data extraction and Markdown formatting.
    *   **Functionality:**
        *   Reads parameter configurations from `parameters_list.txt`.
        *   Iterates through each defined parameter.
        *   Based on the `Extraction Type` (e.g., "single", "list_iterative"), it dispatches calls to appropriate functions in `xml_parser.py`.
        *   Formats the extracted data into a Markdown string (`markdown_output`).
        *   Handles distinct logic for single values versus list-like structures (e.g., classes, skills).
        *   Collects and returns log messages for display or saving.
    *   **Key Libraries:** `csv`, `logging` (for detailed internal tracing).
    *   **Key Functions:**
        *   `process_character_xml(xml_file, parameters_file, log_file)`: Main orchestration function.
        *   `extract_iterative_list_data(xml_file, list_path, tags_to_extract)`: Specialized function for handling complex lists (e.g., `<classes><id-00001>...</id-00001></classes>`).
        *   `read_parameters_from_csv(parameters_file)`: Handles parsing `parameters_list.txt`.

*   **`xml_parser.py`:**
    *   **Purpose:** Provides low-level, reusable functions for interacting with XML files using `xml.etree.ElementTree`. It abstracts away the complexities of XML parsing from the `character_processor.py`.
    *   **Functionality:**
        *   **`get_xml_attribute(xml_file, attribute_path)`:** Extracts a single text value given a direct XML path (e.g., `character/name`). Includes detailed path traversal debugging.
        *   **`get_xml_list_items_by_tag(xml_file, list_path, item_tag)`:** Locates a list container (e.g., `<classes>`) and then identifies all child elements whose tags start with a specific pattern (e.g., `id-`), returning a list of these sub-elements. This is crucial for iterating over dynamically named list items.
        *   **`get_xml_item_text_by_tag(item_element, target_tag)`:** Given an XML element (from `get_xml_list_items_by_tag`), it finds a specific child tag within it (e.g., `<name>`, `<level>`) and returns its text content.
    *   **Key Libraries:** `xml.etree.ElementTree`, `logging`.

*   **`parameters_list.txt`:**
    *   **Purpose:** A CSV-like configuration file that defines all parameters to be extracted.
    *   **Structure:** Contains a header row: `"Parameter Description,XML Path,Extraction Type,List Path,Item Tag,Name Tag,Value Tag"`.
    *   **"Extraction Type" Interpretation:**
        *   `"single"`: Used for simple, direct attribute extraction (e.g., `character/name`).
        *   `"list_iterative"`: Used for complex lists where items have dynamic `id-` tags. The `XML Path` points to the *container* of the list (e.g., `classes` or `skilllist`). `character_processor.py`'s `extract_iterative_list_data` then uses `id-` as the `Item Tag` and specified `tags_to_extract` (like `name`, `level`, `specialization`, `total`).
    *   **Example (conceptual):**
        ```csv
        Parameter Description,XML Path,Extraction Type,List Path,Item Tag,Name Tag,Value Tag
        Character Name,character/name,single,,,,
        Classes,classes,list_iterative,,,name,level,specialization
        Athletics Skill,skilllist,list_iterative,,,name,total
        ```

**Development Aspects & Current Status:**

*   **Core Data Extraction:** The primary issue of "empty output" has largely been resolved. Single-value attributes (name, race, abilities, AC, HP, saves) are now being correctly extracted. List-based data (classes, levels, and individual skills) is also being correctly extracted using the "list_iterative" mechanism.
*   **XML Parsing Library:** `xml.etree.ElementTree` is the chosen XML parsing library for its balance of simplicity and functionality.
*   **`parameters_list.txt` Robustness:** The file is read using `csv.DictReader` with `encoding='utf-8'` and `newline=''`.
*   **Logging:** Extensive `logging` (via `processing.log`) and `print` statements have been integrated throughout `character_processor.py` and `xml_parser.py` to trace execution, variable values, and pinpoint data extraction failures. This logging was crucial in resolving previous issues and will be invaluable for future debugging.
*   **Previous Debugging Efforts:** Extensive efforts were made to verify file paths, XML paths, correct XML tag casing, and robust CSV parsing. A recurring "ValueError: not enough values to unpack" was previously encountered and believed to be resolved by refining the "list_bytag" (now "list_iterative") processing.
*   **Current Known Issue (Minor, Formatting):** The user observed that the Markdown output, when viewed in a "preview" (likely VS Code's Markdown previewer or similar), appears "jumbled onto the same line." Initial assessment suggests this is likely a rendering artifact of the previewer, rather than an issue with the generated Markdown file itself. The `character_processor.py` explicitly adds `\n` characters for newlines. The first task for the new AI is to confirm this by inspecting the raw Markdown file.

**User's Environment for the New AI:**

The user intends to try this project in a new code editor named "Google Antigravity." While the previous debugging occurred in VS Code on Windows (Python 3.12), the script is standard Python and should be portable. The new AI should be mindful of potential environmental differences, though `os.path` and standard library usage minimize cross-platform issues.