# Project Specification: Fantasy Grounds Unity Character Converter

## 1. Architecture Overview (Hexagonal / Ports & Adapters)

We will enforce a strict separation of concerns using Hexagonal Architecture, driven by a **YAML Configuration File**.

```mermaid
graph TD
    Config[rules.yaml] --> InputAdapter
    User((User)) --> InputAdapter[Input Adapter<br/>(YAML-Driven XML Reader)]
    InputAdapter --> Core[Core Domain<br/>(Flexible Data Container)]
    Core --> OutputAdapter[Output Adapter<br/>(Markdown Writer)]
    
    subgraph "Ports & Adapters"
        InputAdapter
        OutputAdapter
    end
    
    subgraph "Core Domain"
        Core
    end
```

### Folder Structure
```
/
├── core/
│   ├── __init__.py
│   └── domain.py       # Defines the Character class (Flexible Dictionary-based)
├── adapters/
│   ├── input/
│   │   ├── __init__.py
│   │   └── xml_reader.py   # Uses PyYAML to read rules and extract data
│   └── output/
│       ├── __init__.py
│       └── markdown_writer.py
├── rules.yaml          # The HUMAN-EDITABLE Configuration File
├── main.py             # Entry point
└── requirements.txt    # references PyYAML
```

---

## 2. Configuration Design (`rules.yaml`)

We choose **YAML** for its readability and ability to handle nested structures. The logic will support extracting multiple fields per list item.

### Proposed Structure
The file is divided into `single` (one-off extractions) and `lists` (iterative deep extraction).

```yaml
version: "1.0"

# 1. Single Value Extractions
# Usage: extracts a value from a specific path.
single:
  Name: "character/name"
  Race: "character/race"
  HP: "character/hp/total"
  AC: "character/defenses/ac/total"

# 2. Iterative List Extractions
# Usage: Finds a container, iterates over children matching a pattern, 
# and extracts multiple fields from each child.
lists:
  - name: "Classes"
    container: "character/classes"
    item_pattern: "id-"
    fields:
      Class Name: "name"
      Level: "level"
      Subclass: "specialization"

  - name: "Skills"
    container: "character/skilllist"
    item_pattern: "id-"
    fields:
      Skill Name: "name"
      Total Bonus: "total"
      Proficiency: "prof"
```

### Inventory Example (Crucial Requirement)
This demonstrates the "Depth" requirement: capturing Name, Count, Weight, and Location for a single item.

```yaml
  - name: "Inventory"
    container: "character/inventorylist"
    item_pattern: "id-"
    fields:
      Item Name: "name"
      Count: "count"
      Weight: "weight"
      Location: "location"
```

---

## 3. Data Mapping (Domain Model)

The `Character` class remains flexible to accept whatever the YAML dictates.

```python
@dataclass
class Character:
    # Single values (from 'single' section)
    # e.g., {"Name": "Rook", "AC": "16"}
    data: Dict[str, Any] = field(default_factory=dict)
    
    # List values (from 'lists' section)
    # e.g., "Inventory": [
    #   {"Item Name": "Backpack", "Count": 1, "Weight": 5, "Location": "carried"},
    #   {"Item Name": "Rope", "Count": 1, "Weight": 10, "Location": "Backpack"}
    # ]
    lists: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
```

---

## 4. Input Adapter Logic (Generic Engine)

The `xml_reader.py` will use `PyYAML` and `xml.etree.ElementTree`.

### Logic Flow

1.  **Load Rules**: `rules = yaml.safe_load(open('rules.yaml'))`
2.  **Process Singles**:
    *   Loop through `rules['single']`.
    *   For each `key, xpath`: `Character.data[key] = get_text(root, xpath)`
3.  **Process Lists**:
    *   Loop through `rules['lists']`.
    *   Locate container: `container = root.find(rule['container'])`
    *   Find children: `items = [child for child in container if rule['item_pattern'] in child.tag]`
    *   **The Deep Loop**:
        *   For each `item_node`:
            *   Create `item_dict = {}`
            *   Loop through `rule['fields']`:
                *   For each `field_name, relative_path`:
                *   `item_dict[field_name] = get_text(item_node, relative_path)`
            *   Append `item_dict` to results list.
    *   Store in `Character.lists[rule['name']]`.
