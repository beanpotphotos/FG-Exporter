import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import logging
import sys
import threading
from PIL import Image, ImageTk

# Import Core Logic
from adapters.input.xml_reader import XMLReader
from adapters.output.markdown_writer import MarkdownWriter
# PDFWriter is imported lazily to capture errors in the GUI log
from core.logic.factory import EnricherFactory

# --- Setup Logging to a String (for Status Box) ---
class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)

class ExporterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fantasy Grounds Exporter v0.9-beta")
        self.root.geometry("700x650")
        
        # --- Theme Colors ---
        self.colors = {
            "bg": "#2b2b2b",
            "fg": "#ffffff",
            "panel": "#3c3f41",
            "accent": "#3a96dd", # Nice blue
            "accent_hover": "#307eba",
            "text_log": "#dcdcdc"
        }
        
        self.root.configure(bg=self.colors["bg"])
        
        # --- Configure TTK Styles (Modern Dark) ---
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frames
        style.configure('TFrame', background=self.colors["bg"])
        style.configure('TLabelframe', background=self.colors["bg"], foreground=self.colors["accent"], borderwidth=1)
        style.configure('TLabelframe.Label', background=self.colors["bg"], foreground=self.colors["accent"], font=('Segoe UI', 10, 'bold'))
        
        # Labels
        style.configure('TLabel', background=self.colors["bg"], foreground=self.colors["fg"], font=('Segoe UI', 10))
        style.configure('Dark.TLabel', background=self.colors["panel"], foreground=self.colors["fg"], font=('Segoe UI', 10))
        
        # Buttons
        style.configure('TButton', 
                        font=('Segoe UI', 10, 'bold'), 
                        background=self.colors["accent"], 
                        foreground="white", 
                        borderwidth=0, 
                        focuscolor=self.colors["bg"])
        style.map('TButton', 
                  background=[('active', self.colors["accent_hover"]), ('pressed', self.colors["accent_hover"])])
        
        # Combobox
        style.configure('TCombobox', 
                        fieldbackground=self.colors["panel"], 
                        background=self.colors["panel"], 
                        foreground=self.colors["fg"],
                        arrowcolor=self.colors["fg"])
        style.map('TCombobox', fieldbackground=[('readonly', self.colors["panel"])])
        
        # Base Directory (Frozen vs Normal)
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # --- Layout ---
        self._build_header()
        self._build_main_content()
        self._build_log_panel()

        self.input_path = None

    def _build_header(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg=self.colors["bg"])
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # Logo
        logo_path = os.path.join(self.base_dir, "logo.png")
        if os.path.exists(logo_path):
            try:
                # Resize specifically for header
                pil_image = Image.open(logo_path)
                pil_image = pil_image.resize((64, 64), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(pil_image)
                lbl_logo = tk.Label(header_frame, image=self.logo_img, bg=self.colors["bg"])
                lbl_logo.pack(side="left", padx=(0, 15))
            except Exception as e:
                print(f"Logo error: {e}")

        # Title Text
        title_frame = tk.Frame(header_frame, bg=self.colors["bg"])
        title_frame.pack(side="left", fill="y")
        
        lbl_title = tk.Label(title_frame, text="Fantasy Grounds Exporter", 
                             font=('Segoe UI', 18, 'bold'), 
                             bg=self.colors["bg"], fg="white")
        lbl_title.pack(anchor="w")
        
        lbl_subtitle = tk.Label(title_frame, text="Convert your characters to PDF & Markdown with ease.", 
                                font=('Segoe UI', 10), 
                                bg=self.colors["bg"], fg="#aaaaaa")
        lbl_subtitle.pack(anchor="w")

    def _build_main_content(self):
        main_frame = tk.Frame(self.root, bg=self.colors["bg"])
        main_frame.pack(fill="x", padx=20, pady=10)
        
        # --- 1. File Selection Section ---
        grp_input = ttk.LabelFrame(main_frame, text="  1. Source File  ", padding=15)
        grp_input.pack(fill="x", pady=(0, 15))
        
        self.btn_select = ttk.Button(grp_input, text="Browse XML...", command=self.select_file)
        self.btn_select.pack(side="left")
        
        self.lbl_file = ttk.Label(grp_input, text="No file selected", font=('Segoe UI', 10, 'italic'), foreground="#888888")
        self.lbl_file.pack(side="left", padx=15, fill="x", expand=True)

        # --- 2. Configuration Section ---
        grp_config = ttk.LabelFrame(main_frame, text="  2. Configuration  ", padding=15)
        grp_config.pack(fill="x", pady=(0, 15))
        
        # Grid Layout for configs
        frame_grid = tk.Frame(grp_config, bg=self.colors["bg"])
        frame_grid.pack(fill="x")
        
        # Ruleset
        ttk.Label(frame_grid, text="Ruleset Definition:").grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.rules_var = tk.StringVar()
        self.combo_rules = ttk.Combobox(frame_grid, textvariable=self.rules_var, state="readonly", width=30)
        self.combo_rules.grid(row=0, column=1, sticky="w")
        
        # Enricher
        ttk.Label(frame_grid, text="Logic Engine:").grid(row=0, column=2, sticky="w", padx=(25, 10))
        self.enricher_var = tk.StringVar()
        self.combo_enricher = ttk.Combobox(frame_grid, textvariable=self.enricher_var, state="readonly", width=15)
        self.combo_enricher['values'] = ["dnd5e", "none"]
        self.combo_enricher.current(0)
        self.combo_enricher.grid(row=0, column=3, sticky="w")
        
        self.populate_rules()

        # --- 3. Export Actions ---
        grp_actions = ttk.LabelFrame(main_frame, text="  3. Export  ", padding=15)
        grp_actions.pack(fill="x")
        
        btn_frame = tk.Frame(grp_actions, bg=self.colors["bg"])
        btn_frame.pack(fill="x")
        
        # PDF Button
        self.btn_pdf = ttk.Button(btn_frame, text="Generate PDF", command=lambda: self.run_export("pdf"))
        self.btn_pdf.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # MD Button
        self.btn_md = ttk.Button(btn_frame, text="Generate Markdown", command=lambda: self.run_export("md"))
        self.btn_md.pack(side="left", fill="x", expand=True, padx=(10, 0))

    def _build_log_panel(self):
        log_frame = ttk.LabelFrame(self.root, text="  Process Log  ", padding=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Text Widget
        self.txt_log = tk.Text(log_frame, height=8, state="disabled", 
                               bg=self.colors["panel"], fg=self.colors["text_log"], 
                               font=("Consolas", 10), borderwidth=0, highlightthickness=0)
        
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.txt_log.yview)
        scrollbar.pack(side="right", fill="y")
        self.txt_log.configure(yscrollcommand=scrollbar.set)
        
        self.txt_log.pack(side="left", fill="both", expand=True)
        
        # Setup Logger
        handler = TextHandler(self.txt_log)
        formatter = logging.Formatter('[%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger = logging.getLogger() # Root Logger
        logger.setLevel(logging.INFO)
        
        # Remove existing handlers needed to avoid dupes in re-runs
        for h in logger.handlers: logger.removeHandler(h)
        logger.addHandler(handler)

    def populate_rules(self):
        # Scan for *_rules.yaml in the script directory
        try:
            files = [f for f in os.listdir(self.base_dir) if f.endswith('_rules.yaml') or f == 'rules.yaml']
        except FileNotFoundError:
            files = []
            
        if not files:
            files = ["dnd5e_rules.yaml"]
        
        self.combo_rules['values'] = files
        if files:
            self.combo_rules.current(0)

    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("XML Files", "*.xml")])
        if path:
            self.input_path = path
            self.lbl_file.config(text=path, foreground=self.colors["accent"])

    def run_export(self, format_type):
        if not self.input_path:
            messagebox.showwarning("Warning", "Please select an XML file first.")
            return
            
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        initial_dir = os.path.dirname(self.input_path) 
        
        file_ext = f".{format_type}"
        file_types = [(f"{format_type.upper()} Files", f"*{file_ext}"), ("All Files", "*.*")]
        
        out_path = filedialog.asksaveasfilename(
            defaultextension=file_ext,
            filetypes=file_types,
            initialdir=initial_dir,
            initialfile=f"{base_name}{file_ext}",
            title=f"Export {format_type.upper()}"
        )
        
        if not out_path:
            return 

        rules_filename = self.rules_var.get()
        rules_path = os.path.join(self.base_dir, rules_filename)
        enricher_name = self.enricher_var.get()
        
        # Disable buttons during processing
        self._toggle_buttons(False)
        
        # Run in thread
        t = threading.Thread(target=self._process, args=(self.input_path, rules_path, enricher_name, format_type, out_path))
        t.start()
    
    def _toggle_buttons(self, state):
        self.btn_select.configure(state="normal" if state else "disabled")
        self.btn_pdf.configure(state="normal" if state else "disabled")
        self.btn_md.configure(state="normal" if state else "disabled")

    def _process(self, input_path, rules_path, enricher_name, format_type, output_path):
        logging.info(f"--- Starting {format_type.upper()} Export ---")
        try:
            # 1. Read
            logging.info(f"Loading rules: {os.path.basename(rules_path)}")
            reader = XMLReader(rules_path)
            logging.info(f"Parsing: {os.path.basename(input_path)}")
            character = reader.parse(input_path)
            
            # 2. Enrich
            logging.info(f"Enriching with logic module: {enricher_name}")
            enricher = EnricherFactory.get(enricher_name)
            character = enricher.enrich(character)
            
            # 3. Write
            success = False
            if format_type == "pdf":
                try:
                    from adapters.output.pdf_writer import PDFWriter
                    logging.info(f"Generating PDF...")
                    writer = PDFWriter()
                    writer.write(character, output_path)
                    success = True
                except ImportError as e:
                    logging.error(f"PDF support missing: {e}")
                except Exception as e:
                    logging.error(f"PDF error: {e}")
                
            elif format_type == "md":
                logging.info(f"Generating Markdown...")
                writer = MarkdownWriter()
                writer.write(character, output_path)
                success = True
                
            if success:
                logging.info(f"SUCCESS! Saved to: {os.path.basename(output_path)}")
                # Removed popup as requested
            else:
                logging.warning("Export finished with errors.")
            
        except Exception as e:
            logging.error(f"Critical Error: {e}")
        finally:
             self.root.after(0, lambda: self._toggle_buttons(True))

if __name__ == "__main__":
    root = tk.Tk()
    
    # Attempt to set icon if available
    # try: root.iconbitmap("icon.ico")
    # except: pass
    
    app = ExporterGUI(root)
    root.mainloop()
