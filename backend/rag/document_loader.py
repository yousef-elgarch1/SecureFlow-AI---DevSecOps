"""
Load and process compliance documents (NIST CSF, ISO 27001)
"""

import os
from typing import List, Dict
import re


class DocumentLoader:
    """Load and chunk compliance documents for RAG system"""

    def __init__(self):
        self.documents = []

    def load_nist_csf(self, file_path: str) -> List[Dict]:
        """
        Load NIST Cybersecurity Framework document

        Args:
            file_path: Path to NIST CSF text file

        Returns:
            List of document chunks with metadata
        """
        chunks = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split by function sections
            sections = re.split(r'={5,}\s*\d+\.\s*([A-Z]+\s*\([A-Z]+\))\s*={5,}', content)

            current_function = None
            for i, section in enumerate(sections):
                if i % 2 == 1:  # This is a function name
                    current_function = section.strip()
                elif i % 2 == 0 and current_function and section.strip():  # This is content
                    # Further split by categories (e.g., ID.AM, PR.AC)
                    category_pattern = r'([A-Z]{2}\.[A-Z]{2})\s*-\s*([^\n]+)'
                    categories = re.split(category_pattern, section)

                    current_category = None
                    current_category_name = None

                    for j, part in enumerate(categories):
                        if j % 3 == 1:  # Category ID (e.g., ID.AM)
                            current_category = part
                        elif j % 3 == 2:  # Category name
                            current_category_name = part.strip()
                        elif j % 3 == 0 and current_category and part.strip():  # Category content
                            chunk = {
                                "text": f"{current_category} - {current_category_name}\n\n{part.strip()}",
                                "source": "NIST CSF",
                                "function": current_function,
                                "category": current_category,
                                "category_name": current_category_name
                            }
                            chunks.append(chunk)

        except Exception as e:
            print(f"Error loading NIST CSF: {e}")

        return chunks

    def load_iso27001(self, file_path: str) -> List[Dict]:
        """
        Load ISO 27001 Annex A controls

        Args:
            file_path: Path to ISO 27001 text file

        Returns:
            List of document chunks with metadata
        """
        chunks = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split by control sections (A.X.X pattern)
            control_pattern = r'(A\.\d+\.\d+)\s+([^\n]+)\n([^\n]+(?:\n(?!A\.\d+\.\d+)[^\n]+)*)'
            matches = re.finditer(control_pattern, content, re.MULTILINE)

            # Also detect theme sections
            theme_pattern = r'={5,}\s*([A-Z\s]+CONTROLS)\s*={5,}'
            themes = re.finditer(theme_pattern, content)

            theme_sections = {}
            last_pos = 0
            current_theme = "General"

            for theme_match in themes:
                if last_pos > 0:
                    theme_sections[current_theme] = (last_pos, theme_match.start())
                current_theme = theme_match.group(1).strip()
                last_pos = theme_match.end()

            if last_pos > 0:
                theme_sections[current_theme] = (last_pos, len(content))

            for match in re.finditer(control_pattern, content, re.MULTILINE):
                control_id = match.group(1)
                control_name = match.group(2).strip()
                control_desc = match.group(3).strip()

                # Find which theme this control belongs to
                theme = "General"
                for theme_name, (start, end) in theme_sections.items():
                    if start <= match.start() < end:
                        theme = theme_name
                        break

                chunk = {
                    "text": f"{control_id} {control_name}\n\n{control_desc}",
                    "source": "ISO 27001",
                    "control_id": control_id,
                    "control_name": control_name,
                    "theme": theme
                }
                chunks.append(chunk)

        except Exception as e:
            print(f"Error loading ISO 27001: {e}")

        return chunks

    def load_all_documents(self, nist_path: str, iso_path: str) -> List[Dict]:
        """
        Load all compliance documents

        Args:
            nist_path: Path to NIST CSF file
            iso_path: Path to ISO 27001 file

        Returns:
            Combined list of all document chunks
        """
        all_chunks = []

        print("Loading NIST CSF...")
        nist_chunks = self.load_nist_csf(nist_path)
        print(f"  Loaded {len(nist_chunks)} NIST chunks")
        all_chunks.extend(nist_chunks)

        print("Loading ISO 27001...")
        iso_chunks = self.load_iso27001(iso_path)
        print(f"  Loaded {len(iso_chunks)} ISO chunks")
        all_chunks.extend(iso_chunks)

        print(f"Total chunks loaded: {len(all_chunks)}")

        return all_chunks


# Test function
if __name__ == "__main__":
    print("="*60)
    print("DOCUMENT LOADER TEST")
    print("="*60)

    loader = DocumentLoader()

    nist_path = "../../data/compliance_docs/nist_csf_summary.txt"
    iso_path = "../../data/compliance_docs/iso27001_annexa.txt"

    try:
        # Load all documents
        chunks = loader.load_all_documents(nist_path, iso_path)

        print(f"\nSuccessfully loaded {len(chunks)} document chunks")

        # Show sample chunks
        print("\n" + "-"*60)
        print("Sample NIST Chunk:")
        print("-"*60)
        nist_samples = [c for c in chunks if c['source'] == 'NIST CSF']
        if nist_samples:
            sample = nist_samples[0]
            print(f"Function: {sample.get('function', 'N/A')}")
            print(f"Category: {sample.get('category', 'N/A')}")
            print(f"Text preview: {sample['text'][:200]}...")

        print("\n" + "-"*60)
        print("Sample ISO Chunk:")
        print("-"*60)
        iso_samples = [c for c in chunks if c['source'] == 'ISO 27001']
        if iso_samples:
            sample = iso_samples[0]
            print(f"Control ID: {sample.get('control_id', 'N/A')}")
            print(f"Theme: {sample.get('theme', 'N/A')}")
            print(f"Text preview: {sample['text'][:200]}...")

        print("\nDocument Loader test completed successfully!")

    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
