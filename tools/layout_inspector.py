import pdfplumber
import sys
import os

def inspect_layout(pdf_path):
    print(f"Inspecting {pdf_path}...")
    
    if not os.path.exists(pdf_path):
        print("PDF not found.")
        return False

    with pdfplumber.open(pdf_path) as pdf:
        p1 = pdf.pages[0]
        width = p1.width
        height = p1.height
        
        print(f"Page Size: {width}x{height}")
        
        # Define Zones
        zone_col1 = (0, 100) # Attributes
        zone_col2 = (100, 250) # Skills
        zone_col3 = (250, 600) # Stats
        
        # Check Elements
        errors = []
        
        def check_text_in_zone(text, zone_x_range, name):
            words = p1.extract_words()
            found = [w for w in words if text in w['text']]
            if not found:
                print(f"[WARN] '{text}' not found.")
                return 0
            
            # Check X coord of first hit
            hit = found[0]
            x_mid = (hit['x0'] + hit['x1']) / 2
            
            if not (zone_col1[0] <= x_mid <= zone_col1[1]):
                 # Strict check?
                 pass

            print(f"'{text}' found at X={hit['x0']:.2f}")
            
            if not (zone_x_range[0] <= hit['x0'] <= zone_x_range[1]):
                msg = f"[FAIL] '{name}' (Expected X {zone_x_range}) found at {hit['x0']:.2f}"
                print(msg)
                errors.append(msg)
            else:
                print(f"[PASS] '{name}' aligned.")

        # 1. Check Attributes in Col 1
        check_text_in_zone("STR", (30, 100), "Attribute Label")

        # 2. Check Skills in Col 2 (Approx)
        check_text_in_zone("Perception", (100, 250), "Skill: Perception")
        
        # 3. Check Combat Stats in Col 3
        check_text_in_zone("Init", (250, 500), "Initiative Box")

        # 4. Weapons Table Headers
        # NAME ~ 260+? No, Weapons table is in Col 3 area? 
        # In `pdf_writer.py`, `col3_x = margin + 230` -> 266.
        # Header "NAME" at col3_x + 5 -> ~271.
        check_text_in_zone("NAME", (260, 300), "Weapon: NAME")
        check_text_in_zone("ATK", (350, 400), "Weapon: ATK")
        check_text_in_zone("DAMAGE", (400, 500), "Weapon: DAMAGE")
        
        if errors:
            print("\nErrors Found (Page 1):")
            for e in errors: print(e)
            return False
            
    # Page 2 Check
    with pdfplumber.open(pdf_path) as pdf:
        if len(pdf.pages) > 1:
            p2 = pdf.pages[1]
            words = p2.extract_words()
            
            # Check Inventory Header
            inv_header = [w for w in words if "Inventory" in w['text']]
            if inv_header:
                print(f"[PASS] Page 2: 'Inventory' found at Y={inv_header[0]['top']:.2f}")
            else:
                 print("[WARN] Page 2: 'Inventory' not found.")
        else:
             print("[INFO] No Page 2 found.")

    print("\nLayout looks roughly correct!")
    return True

if __name__ == "__main__":
    target = "output/Rook.pdf"
    if len(sys.argv) > 1: target = sys.argv[1]
    inspect_layout(target)
