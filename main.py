import argparse
import logging
import sys
import os
from adapters.input.xml_reader import XMLReader
from adapters.output.markdown_writer import MarkdownWriter

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("Main")

def main():
    """
    Traffic Controller:
    1. Parsing Arguments (Input/Output sources)
    2. Instantiating Adapters
    3. Orchestrating the flow
    """
    parser = argparse.ArgumentParser(description="Fantasy Grounds Character Exporter")
    parser.add_argument("--input", "-i", required=False, help="Path to input FGU XML file")
    parser.add_argument("--output", "-o", required=False, help="Path to output Markdown file")
    parser.add_argument("--rules", "-r", default="dnd5e_rules.yaml", help="Path to configuration file")
    parser.add_argument("--enricher", "-e", default="dnd5e", help="Logic Module to use (dnd5e, none)")
    parser.add_argument("--format", "-f", default="both", help="Output format (pdf, md, both)")
    
    args = parser.parse_args()

    # Default to hardcoded test file if not provided (for ease of use during dev)
    input_path = args.input
    if not input_path:
        # Fallback for dev/demo purpose
        default_test = os.path.join("input FGU characters", "Rook.xml")
        if os.path.exists(default_test):
            input_path = default_test
            print(f"No input specified. Using default: {input_path}")
        else:
            logger.error("No input file passed and default 'Rook.xml' not found.")
            sys.exit(1)

    output_path = args.output
    if not output_path:
        # Auto-generate output name in /output folder
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        
        # Use filename as character name basis
        base_name = os.path.basename(input_path)
        name_without_ext = os.path.splitext(base_name)[0]
        output_path = os.path.join(output_dir, f"{name_without_ext}.md")
        print(f"No output specified. Generating: {output_path}")
    else:
        # Ensure directory exists if user provided one
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

    rules_path = args.rules
    if not os.path.exists(rules_path):
        logger.error(f"Rules config not found at: {rules_path}")
        sys.exit(1)

    # --- HEXAGONAL ORCHESTRATION ---
    
    # 1. Init Adapters
    try:
        reader = XMLReader(rules_path)
        writer = MarkdownWriter()
    except Exception as e:
        logger.error(f"Failed to initialize adapters: {e}")
        sys.exit(1)

    # 2. Extract Data (Input -> Domain)
    try:
        logger.info(f"Reading character from {input_path}...")
        character = reader.parse(input_path)
    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        sys.exit(1)

    # 2.5 Enrich Data (Strategy Pattern)
    try:
        from core.logic.factory import EnricherFactory
        enricher = EnricherFactory.get(args.enricher)
        character = enricher.enrich(character)
    except Exception as e:
        logger.warning(f"Enrichment step failed: {e}")

    # 3. Write
    base_output = output_path.replace(".md", "")
    
    fmt = args.format.lower()
    
    try:
        if fmt in ["md", "both"]:
            logger.info(f"Writing markdown to {base_output}.md...")
            writer = MarkdownWriter()
            writer.write(character, base_output + ".md")

        if fmt in ["pdf", "both"]:
            try:
                from adapters.output.pdf_writer import PDFWriter
                logger.info(f"Writing PDF to {base_output}.pdf...")
                pdf_writer = PDFWriter()
                pdf_writer.write(character, base_output + ".pdf")
            except ImportError:
                logger.warning("ReportLab not found. Skipping PDF generation.")
            except Exception as e:
                logger.error(f"Failed to generate PDF: {e}")

        logger.info("Done!")
    except Exception as e:
        logger.error(f"Writing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
