import yaml
import xml.etree.ElementTree as ET
import logging
from typing import Dict, Any, List
from core.domain import Character

class XMLReader:
    def __init__(self, rules_path: str):
        self.logger = logging.getLogger(__name__)
        self.rules_path = rules_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        try:
            with open(self.rules_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.error(f"Failed to load rules from {self.rules_path}: {e}")
            raise

    def parse(self, xml_path: str) -> Character:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
        except Exception as e:
            self.logger.error(f"Failed to parse XML file {xml_path}: {e}")
            raise

        character = Character()

        # 1. Process Single Values
        single_rules = self.rules.get('single', {})
        for key, xpath in single_rules.items():
            value = self._get_text(root, xpath)
            if value is not None:
                character.add_data_point(key, value)
            else:
                self.logger.warning(f"Field '{key}' not found at path '{xpath}'")

        # 2. Process Lists
        list_rules = self.rules.get('lists', [])
        for rule in list_rules:
            list_name = rule.get('name')
            container_path = rule.get('container')
            item_pattern = rule.get('item_pattern')
            required_field = rule.get('required_field')
            fields = rule.get('fields', {})
            
            if not all([list_name, container_path, item_pattern, fields]):
                self.logger.warning(f"Skipping malformed list rule: {rule}")
                continue

            extracted_items = self._extract_list_items(root, container_path, item_pattern, fields, required_field)
            if extracted_items:
                character.add_list(list_name, extracted_items)
            else:
                self.logger.warning(f"No items found for list '{list_name}' at '{container_path}'")

        return character

    def _extract_list_items(self, root: ET.Element, container_path: str, item_pattern: str, fields: Dict[str, str], required_field: str = None) -> List[Dict[str, Any]]:
        container = root.find(container_path)
        if container is None:
            # Graceful failure: Log warning but don't crash
            self.logger.warning(f"Container path '{container_path}' not found in XML.")
            return []

        items = []
        # Iterate over children that match the pattern (e.g., "id-")
        for child in container:
            if item_pattern in child.tag:
                item_data = {}
                # "Deep Loop": Extract multiple fields for this item
                for field_name, field_config in fields.items():
                    val = None
                    
                    # Case 1: Simple Path (String)
                    if isinstance(field_config, str):
                        val = self._get_text(child, field_config)
                    
                    # Case 2: Advanced Configuration (Dictionary)
                    elif isinstance(field_config, dict):
                        path = field_config.get('path')
                        extraction_type = field_config.get('type')
                        
                        if extraction_type == 'flatten':
                            # Flatten Logic: Iterate over children of the path and join sub-fields
                            sub_container = child.find(path)
                            if sub_container is not None:
                                sub_fields = field_config.get('sub_fields', [])
                                separator = field_config.get('separator', ' ') 
                                item_separator = field_config.get('item_separator', ', ')
                                
                                flat_values = []
                                for sub_item in sub_container:
                                    # Extract components for this sub-item
                                    components = []
                                    for sub_field in sub_fields:
                                        comp_val = self._get_text(sub_item, sub_field)
                                        if comp_val:
                                            components.append(comp_val)
                                    
                                    if components:
                                        flat_values.append(separator.join(components))
                                
                                if flat_values:
                                    val = item_separator.join(flat_values)
                            else:
                                # Fallback: If the container path doesn't exist, try a simple fallback path
                                fallback = field_config.get('fallback_path')
                                if fallback:
                                    val = self._get_text(child, fallback)
                        elif extraction_type == 'subtree':
                            # Extract the entire subtree as a dictionary
                            sub_node = child.find(path)
                            if sub_node is not None:
                                val = self._xml_to_dict(sub_node)
                        else:
                            # Fallback or other future types
                            val = self._get_text(child, path)

                    if val is not None and (isinstance(val, dict) or val.strip() != ""):
                        item_data[field_name] = val
                    else:
                         # Optional: Log specific missing sub-fields
                         pass 
                
                # Validation: Check required field if specified
                if required_field:
                    if required_field not in item_data or not item_data[required_field]:
                        # Skip ghost item
                        continue

                # Only add item if we successfully extracted components
                if item_data:
                    items.append(item_data)
        
        return items

    def _get_text(self, node: ET.Element, xpath: str) -> Optional[str]:
        try:
            found = node.find(xpath)
            if found is not None:
                # Use itertext() to capture text from nested tags (like <p>, <b> in formattedtext)
                text = "".join(found.itertext())
                return text.strip() if text else None
        except Exception:
            # Catch bad path errors to ensure graceful failure
            pass
        return None

    def _xml_to_dict(self, element: ET.Element) -> Any:
        # If element has no children, return text
        if len(element) == 0:
            return element.text or ""
        
        result = {}
        for child in element:
            child_val = self._xml_to_dict(child)
            # If tag already exists, convert to list (or keep list)
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_val)
                else:
                    result[child.tag] = [result[child.tag], child_val]
            else:
                result[child.tag] = child_val
        return result
