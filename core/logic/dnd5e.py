import logging
from core.domain import Character
from core.logic.base import EnricherStrategy

logger = logging.getLogger("DnD5eLogic")

class DnD5eEnricher(EnricherStrategy):
    """
    Domain Service for enriching a generic Character object with D&D 5e specific derived statistics.
    Strictly follows the rule: Input -> Enricher -> Output.
    """
    
    def enrich(self, character: Character) -> Character:
        """
        Main entry point. Modifies the character in place (or returns it) with calculated fields.
        """
        logger.info("Enriching character data with D&D 5e logic...")
        
        self._enrich_modifiers(character)
        self._enrich_proficiency_bonus(character)
        self._enrich_hit_dice(character)
        self._enrich_spell_dc(character)
        self._enrich_passive_perception(character)
        self._enrich_passive_perception(character)
        self._enrich_weapons(character)
        self._enrich_spells(character)
        self._clean_data(character)

        return character

    def _enrich_spells(self, character: Character):
        """Calculate Spell Save DC strings for spells."""
        spells = character.lists.get("Spells & Powers", [])
        if not spells: return
        
        prof_val = 0
        try:
             prof_val = int(character.data_points.get("Proficiency Bonus", "+0").replace("+", ""))
        except:
             pass
             
        # Map Group Name -> Data (Stat, DC base?)
        # We need to find the definition of the group in "Power Groups" list
        pg_list = character.lists.get("Power Groups", [])
        pg_map = {pg.get("Name", ""): pg for pg in pg_list}
        
        # Also map Classes -> SpellAbility
        classes = character.lists.get("Classes", [])
        # Simple map: "Spells (Wizard)" -> "Wizard" -> "intelligence"
        
        stats = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for s in spells:
            # 1. Attempt to extract Save info from 'actions' (Nested XML)
            action_save_data = self._extract_save_from_actions(s, character, prof_val)
            
            # 2. Try to calculate Generic/Group DC (needed for fallback or resolving action data)
            group_name = s.get("Group", "")
            stat_name = None
            dc = None
            
            # Strategy A: Check Power Groups list
            if group_name in pg_map:
                pg = pg_map[group_name]
                raw_stat = pg.get("SaveStat", "") or pg.get("Stat", "")
                if raw_stat: stat_name = raw_stat
            
            # Strategy B: Infer from Group Name
            if not stat_name and "(" in group_name:
                 possible_class = group_name.split("(")[1].replace(")", "").strip()
                 for c in classes:
                     if c.get("Class") == possible_class:
                         stat_name = c.get("SpellAbility")
                         break
            
            # Calc DC if stat found
            if stat_name:
                 stat_name = stat_name.lower()
                 if stat_name in stats:
                     mod_str = character.data_points.get(f"{stat_name.capitalize()} Modifier", "+0")
                     try:
                         mod_val = int(mod_str.replace("+", ""))
                         dc = 8 + prof_val + mod_val
                     except: pass
            
            # 3. Apply Save Logic
            if action_save_data:
                # Handle "DC ? CON" case (Group-based DC)
                if "?" in action_save_data:
                    if dc is not None:
                        s["Save"] = action_save_data.replace("?", str(dc))
                    else:
                        s["Save"] = action_save_data.replace("DC ? ", "")
                else:
                    s["Save"] = action_save_data
            
            elif dc is not None:
                 # Fallback: Use logic based on Stat ONLY if existing 'Save' field is present
                 # and we have a DC.
                 raw_save = s.get("Save", "")
                 if raw_save:
                     short_save = raw_save[:3].upper()
                     s["Save"] = f"DC {dc} {short_save}"


    def _extract_save_from_actions(self, spell: dict, character: Character, prof_val: int) -> str:
        """
        Inspect 'actions' dict to find cast actions with save info.
        Returns formatted string "DC X STAT" or None.
        """
        actions = spell.get("actions", {})
        # XMLReader might return a list of dicts if multiple 'id-00001', or a dict of dicts.
        # Usually XMLReader for 'id-' pattern returns a LIST of items if they are siblings.
        # But here 'actions' is a child of 'spell'. XMLReader usually makes children list or dict based on cardinality.
        # Let's handle both list and dict to be safe.
        
        action_list = []
        if isinstance(actions, dict):
             action_list = actions.values()
        elif isinstance(actions, list):
             action_list = actions
             
        for action in action_list:
            if not isinstance(action, dict): continue
            
            # Check type='cast'
            if action.get("type") == "cast":
                save_type = action.get("savetype", "")
                if not save_type: continue
                
                short_save = save_type[:3].upper()
                
                # Determine DC
                dc_base = action.get("savedcbase", "group")
                dc_val = 0
                
                if dc_base == "fixed":
                    try:
                        dc_val = int(action.get("savedcmod", "0"))
                    except: pass
                
                elif dc_base == "ability":
                    # savedcstat e.g. "wisdom"
                    stat = action.get("savedcstat", "")
                    if stat:
                        mod_str = character.data_points.get(f"{stat.capitalize()} Modifier", "+0")
                        try:
                            mod = int(mod_str.replace("+", ""))
                            dc_val = 8 + prof_val + mod
                        except: pass
                
                elif dc_base == "group":
                    # Fallback to group logic (calculated in parent loop as 'dc')
                    # We need 'dc' passing in? Or re-calc?
                    # Ideally we use the 'dc' we already calculated in the loop.
                    # But cleaning up refactoring: return (dc_val, save_type) tuple?
                    # Or just return None and let parent use 'dc' + 'save_type'.
                    return f"DC ? {short_save}" # Special marker to fill in DC from parent

                if dc_val > 0:
                    return f"DC {dc_val} {short_save}"
                    
        return None

    def _enrich_modifiers(self, character: Character):
        """Calculate Ability Modifiers from Scores if missing."""
        atts = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        for att in atts:
            score_str = character.data_points.get(att)
            mod_str = character.data_points.get(f"{att} Modifier")

            if score_str:
                # Always ensure modifier has signed format if possible
                try:
                    # XML might have "bonus" but we want to ensure it's formatted "+N"
                    # If we have mod, verify/reformat it
                    if mod_str:
                         mod_int = int(mod_str.replace("+", ""))
                         character.data_points[f"{att} Modifier"] = f"{mod_int:+d}"
                    else:
                        # Calc it
                        score = int(score_str)
                        mod = (score - 10) // 2
                        character.data_points[f"{att} Modifier"] = f"{mod:+d}"
                        logger.debug(f"Calculated {att} Mod: {mod:+d}")
                except ValueError:
                    pass

    def _clean_data(self, character: Character):
        """Clean up data based on specific user rules."""
        # Rule: "leave the spot for current hit points blank"
        character.data_points["Current HP"] = ""
        
        # Rule: "Add a Note in the notes box for Passive Perception"
        pp = character.data_points.get("Passive Perception")
        if pp:
            # Add to Notes list. Logic assumes 'Notes' list exists or we create it.
            # pdf_writer expects list of dicts with "Name"? Or we'll adapt.
            # pdf_writer currently just draws a rect. I'll need to update it to use _draw_list_box or custom.
            # Let's populate 'Notes' list with a dict.
            notes = character.lists.get("Notes", [])
            # check if already there to avoid dupes on re-run? internal logic implies single pass.
            notes.insert(0, {"Name": f"Passive Perception: {pp}"})
            character.lists["Notes"] = notes

    def _enrich_proficiency_bonus(self, character: Character):
        """Calculate Proficiency Bonus from Total Class Level."""
        if character.data_points.get("Proficiency Bonus"):
            return # Already exists

        classes = character.lists.get("Classes", [])
        total_level = 0
        for c in classes:
            try:
                total_level += int(c.get("Level", 0))
            except: pass
            
        if total_level > 0:
            pb = ((total_level - 1) // 4) + 2
            character.data_points["Proficiency Bonus"] = f"+{pb}"
            logger.info(f"Calculated Proficiency Bonus: +{pb} (Level {total_level})")
            
    def _enrich_hit_dice(self, character: Character):
        """Aggregate Hit Dice from classes e.g. '5d10 + 3d8'."""
        classes = character.lists.get("Classes", [])
        hd_list = []
        for c in classes:
            lvl = c.get("Level", "")
            die = c.get("HitDice", "") # e.g. "1d10" or "d10"
            if lvl and die:
                # If die is "1d10", we want "5d10" (Level + d-face)
                # If die is "d10", we want "5d10"
                if die.startswith("1"):
                    die = die[1:] # Strip leading 1
                hd_list.append(f"{lvl}{die}")
        
        if hd_list:
            character.data_points["Hit Dice"] = " + ".join(hd_list)

    def _enrich_spell_dc(self, character: Character):
        """Calculate Spell Save DC: 8 + Prof + Ability Mod."""
        if character.data_points.get("Spell Save DC"):
            return

        # Strategy 1: Check Power Groups (Best Source)
        power_groups = character.lists.get("Power Groups", [])
        target_stat = None
        
        # Heuristic: Find first group with 'Spell' in name or fallback to first group with a stat
        for pg in power_groups:
            name = pg.get("Name", "").lower()
            stat = pg.get("Stat") or pg.get("SaveStat")
            if stat and "spell" in name:
                target_stat = stat
                break
        
        if not target_stat and power_groups:
             # Fallback: Just use first group with a stat
             for pg in power_groups:
                 stat = pg.get("Stat") or pg.get("SaveStat")
                 if stat:
                     target_stat = stat
                     break
                     
        # Strategy 2: Fallback to Class SpellAbility
        if not target_stat:
            classes = character.lists.get("Classes", [])
            for c in classes:
                s = c.get("SpellAbility")
                if s: 
                    target_stat = s
                    break
        
        if not target_stat: return # Giving up
        
        target_stat = target_stat.capitalize() # wisdom -> Wisdom
        
        try:
            # Need Prof Bonus (Clean string)
            pb_str = character.data_points.get("Proficiency Bonus", "0").replace("+", "").strip()
            pb = int(pb_str)
            
            # Need Ability Mod
            mod_str = character.data_points.get(f"{target_stat} Modifier", "0").replace("+", "").strip()
            mod = int(mod_str)
            
            dc = 8 + pb + mod
            character.data_points["Spell Save DC"] = str(dc)
            logger.info(f"Calculated Spell DC: {dc} (8 + {pb} + {mod} {target_stat})")
        except ValueError:
            pass

    def _enrich_passive_perception(self, character: Character):
        """Calculate Passive Perception: 10 + Perception Skill Total."""
        skills = character.lists.get("Skills", [])
        for s in skills:
            if s.get("Skill") == "Perception":
                try:
                    total = int(s.get("Total", 0))
                    passive = 10 + total
                    character.data_points["Passive Perception"] = str(passive)
                    logger.debug(f"Calculated Passive Perception: {passive}")
                except: pass
                break

    def _enrich_weapons(self, character: Character):
        """Calculate Total Attack Bonus and Multi-component Damage for weapons."""
        weapons = character.lists.get("Weapons", [])
        
        pb_str = character.data_points.get("Proficiency Bonus", "0").replace("+", "").strip()
        try:
            prof_bonus = int(pb_str)
        except: prof_bonus = 0

        for w in weapons:
            # --- 1. Attack Calculation ---
            if not w.get("Total Attack"):
                try:
                    # Determine Stat to use
                    stat_name = w.get("Stat", "").capitalize()
                    properties_str = w.get("Properties", "").lower()
                    w_type = w.get("type", "0") # 0=Melee, 1=Ranged
                    
                    if "finesse" in properties_str:
                        try:
                            str_mod = int(character.data_points.get("Strength Modifier", "0").replace("+", ""))
                            dex_mod = int(character.data_points.get("Dexterity Modifier", "0").replace("+", ""))
                            if dex_mod > str_mod: stat_name = "Dexterity"
                            elif not stat_name: stat_name = "Strength"
                        except: pass
                    
                    if not stat_name:
                        # Baseline fallback: Melee = Strength, Ranged = Dexterity
                        stat_name = "Dexterity" if w_type == "1" else "Strength"
                    
                    stat_mod = 0
                    if stat_name:
                        try: stat_mod = int(character.data_points.get(f"{stat_name} Modifier", "0").replace("+", ""))
                        except: pass
                    
                    usage_prof = prof_bonus if w.get("Proficient") == "1" else 0
                    
                    # FGU has both attackbonus AND magic bonus sometimes
                    atk_bonus = 0
                    try: atk_bonus = int(w.get("Attack Bonus", "0"))
                    except: pass
                    
                    magic_bonus = 0
                    try: magic_bonus = int(w.get("Magic Bonus", "0"))
                    except: pass
                    
                    # Heuristic: If weapon-level bonuses are 0, check first damage component's bonus
                    # This helps with inconsistent FGU data where bonus is only in damagelist
                    if atk_bonus == 0 and magic_bonus == 0:
                        damage_data = w.get("DamageData", {})
                        if isinstance(damage_data, dict) and damage_data:
                            first_id = sorted(damage_data.keys())[0]
                            first_comp = damage_data[first_id]
                            if isinstance(first_comp, dict):
                                try: atk_bonus = int(first_comp.get("bonus", "0"))
                                except: pass
                    
                    total = stat_mod + usage_prof + atk_bonus + magic_bonus
                    if total != 0:
                        w["Total Attack"] = f"{total:+d}"
                    
                    logger.info(f"Weapon '{w.get('Name')}': Atk={w.get('Total Attack')} (Stat:{stat_mod} + Prof:{usage_prof} + Bonus:{atk_bonus+magic_bonus})")
                except Exception as e:
                    logger.warning(f"Failed to calculate attack for '{w.get('Name')}': {e}")

            # --- 2. Advanced Damage Calculation ---
            # Formula: [dice] + (Modifier * statmult) + [bonus] [type]
            damage_data = w.get("DamageData", {})
            damage_components = []
            
            # DamageData is a dict of dicts (id-00001: {...}) from subtree extraction
            if isinstance(damage_data, dict):
                # Sort items by key to maintain order
                items = sorted(damage_data.items())
                for _, d in items:
                    if not isinstance(d, dict): continue
                    
                    dice = d.get("dice", "")
                    if dice and dice.startswith("d"):
                        dice = "1" + dice
                    
                    bonus_val = 0
                    try: bonus_val = int(d.get("bonus", "0"))
                    except: pass
                    
                    stat_key = d.get("stat")
                    # Smart Fallback for "base"
                    if stat_key == "base":
                        stat_key = w.get("Stat", "")
                        if not stat_key:
                            stat_key = "dexterity" if w_type == "1" else "strength"
                    
                    mod_val = 0
                    if stat_key and stat_key.lower() != "na":
                        # Lookup modifier
                        mod_str = character.data_points.get(f"{stat_key.capitalize()} Modifier", "0")
                        try: mod_val = int(mod_str.replace("+", ""))
                        except: pass
                    
                    # statmult logic
                    mult = 1.0
                    try: mult = float(d.get("statmult", "1"))
                    except: pass
                    
                    component_total_int = int(mod_val * mult) + bonus_val
                    dmg_type = d.get("type", "")
                    
                    # Construct part
                    part = ""
                    if dice:
                        part = dice
                        if component_total_int > 0:
                            part += f" + {component_total_int}"
                        elif component_total_int < 0:
                            part += f" - {abs(component_total_int)}"
                    elif component_total_int != 0:
                        part = str(component_total_int)
                    
                    if part:
                        if dmg_type:
                            part += f" {dmg_type}"
                        damage_components.append(part)
            
            if damage_components:
                w["Damage"] = " + ".join(damage_components)
                logger.info(f"Weapon '{w.get('Name')}': Damage='{w.get('Damage')}'")
