"""
Compliance Retriever
Searches vector database for relevant compliance sections based on vulnerabilities
"""

import sys
import os
from typing import List, Dict, Optional

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.vector_store import VectorStore


class ComplianceRetriever:
    """Retrieves relevant compliance sections for vulnerabilities"""

    def __init__(self, vector_store: Optional[VectorStore] = None):
        """
        Initialize compliance retriever

        Args:
            vector_store: VectorStore instance (creates new one if not provided)
        """
        if vector_store:
            self.vector_store = vector_store
        else:
            vector_db_path = os.path.join(
                os.path.dirname(__file__),
                "../../vector_db"
            )
            self.vector_store = VectorStore(persist_directory=vector_db_path)

    def retrieve_for_vulnerability(
        self,
        vulnerability: Dict,
        top_k: int = 5
    ) -> Dict:
        """
        Retrieve relevant compliance sections for a single vulnerability

        Args:
            vulnerability: Vulnerability dict with 'title', 'description', 'category'
            top_k: Number of results to retrieve

        Returns:
            Dict with search results and formatted context
        """
        # Build search query from vulnerability details
        query_parts = []

        if 'title' in vulnerability:
            query_parts.append(vulnerability['title'])

        if 'category' in vulnerability:
            query_parts.append(vulnerability['category'])

        if 'description' in vulnerability:
            # Truncate long descriptions
            desc = vulnerability['description'][:200]
            query_parts.append(desc)

        query = " ".join(query_parts)

        # Search vector database
        results = self.vector_store.search(query, top_k=top_k)

        # Format results
        formatted = self._format_results(results)

        return {
            'query': query,
            'raw_results': results,
            'formatted_context': formatted,
            'num_results': len(results['documents'])
        }

    def retrieve_for_vulnerabilities(
        self,
        vulnerabilities: List[Dict],
        top_k: int = 3
    ) -> Dict:
        """
        Retrieve relevant compliance sections for multiple vulnerabilities

        Args:
            vulnerabilities: List of vulnerability dicts
            top_k: Number of results per vulnerability

        Returns:
            Dict with aggregated results
        """
        all_results = []
        seen_controls = set()

        # Retrieve for each vulnerability
        for vuln in vulnerabilities:
            result = self.retrieve_for_vulnerability(vuln, top_k=top_k)
            all_results.append({
                'vulnerability': vuln.get('title', 'Unknown'),
                'results': result
            })

            # Track unique controls
            for metadata in result['raw_results']['metadatas']:
                control_id = metadata.get('control_id') or metadata.get('category')
                if control_id:
                    seen_controls.add(control_id)

        # Build aggregated context
        aggregated_context = self._build_aggregated_context(all_results)

        return {
            'vulnerability_count': len(vulnerabilities),
            'unique_controls': list(seen_controls),
            'individual_results': all_results,
            'aggregated_context': aggregated_context
        }

    def retrieve_by_category(
        self,
        category: str,
        top_k: int = 10
    ) -> Dict:
        """
        Retrieve compliance sections by vulnerability category

        Args:
            category: Vulnerability category (e.g., "SQL Injection", "XSS")
            top_k: Number of results to retrieve

        Returns:
            Dict with search results
        """
        results = self.vector_store.search(category, top_k=top_k)
        formatted = self._format_results(results)

        return {
            'category': category,
            'raw_results': results,
            'formatted_context': formatted,
            'num_results': len(results['documents'])
        }

    def _format_results(self, results: Dict) -> str:
        """
        Format search results into readable context for LLM

        Args:
            results: Raw search results from vector store

        Returns:
            Formatted string
        """
        if not results['documents']:
            return "No relevant compliance sections found."

        formatted_sections = []

        for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
            source = metadata.get('source', 'Unknown')
            control_id = metadata.get('control_id') or metadata.get('category', 'N/A')

            section = f"[{i+1}] {source} - {control_id}\n{doc}\n"
            formatted_sections.append(section)

        return "\n".join(formatted_sections)

    def _build_aggregated_context(self, all_results: List[Dict]) -> str:
        """
        Build aggregated context from multiple vulnerability results

        Args:
            all_results: List of individual retrieval results

        Returns:
            Aggregated context string
        """
        sections = []

        sections.append("RELEVANT COMPLIANCE REQUIREMENTS")
        sections.append("=" * 60)

        for i, item in enumerate(all_results):
            vuln_title = item['vulnerability']
            result = item['results']

            sections.append(f"\n{i+1}. Vulnerability: {vuln_title}")
            sections.append("-" * 60)

            if result['num_results'] > 0:
                # Add top 2 results for each vulnerability
                for j in range(min(2, result['num_results'])):
                    doc = result['raw_results']['documents'][j]
                    metadata = result['raw_results']['metadatas'][j]

                    source = metadata.get('source', 'Unknown')
                    control_id = metadata.get('control_id') or metadata.get('category', 'N/A')

                    sections.append(f"\n  [{source}] {control_id}")
                    sections.append(f"  {doc[:300]}...")
            else:
                sections.append("  No specific compliance sections found")

        return "\n".join(sections)

    def get_stats(self) -> Dict:
        """
        Get statistics about the vector database

        Returns:
            Dict with database stats
        """
        total_docs = self.vector_store.count()

        # Sample search to get framework distribution
        nist_sample = self.vector_store.search("NIST", top_k=100)
        iso_sample = self.vector_store.search("ISO 27001", top_k=100)

        nist_count = sum(1 for m in nist_sample['metadatas'] if m.get('source') == 'NIST CSF')
        iso_count = sum(1 for m in iso_sample['metadatas'] if m.get('source') == 'ISO 27001')

        return {
            'total_documents': total_docs,
            'estimated_nist_docs': nist_count,
            'estimated_iso_docs': iso_count
        }


# Test function
if __name__ == "__main__":
    print("="*60)
    print("COMPLIANCE RETRIEVER TEST")
    print("="*60)

    try:
        # Initialize retriever
        print("\n1. Initializing retriever...")
        retriever = ComplianceRetriever()
        print("Retriever initialized successfully")

        # Get stats
        print("\n2. Vector database statistics:")
        stats = retriever.get_stats()
        print(f"  Total documents: {stats['total_documents']}")
        print(f"  NIST CSF sections: {stats['estimated_nist_docs']}")
        print(f"  ISO 27001 controls: {stats['estimated_iso_docs']}")

        if stats['total_documents'] == 0:
            print("\nWARNING: Vector database is empty!")
            print("Run: python backend/rag/init_vectordb.py")
            sys.exit(1)

        # Test single vulnerability retrieval
        print("\n3. Testing single vulnerability retrieval...")
        test_vuln = {
            'title': 'SQL Injection in login endpoint',
            'category': 'Injection',
            'description': 'User input not properly sanitized in SQL query',
            'severity': 'CRITICAL'
        }

        result = retriever.retrieve_for_vulnerability(test_vuln, top_k=3)
        print(f"\nQuery: {result['query'][:100]}...")
        print(f"Found {result['num_results']} relevant compliance sections")

        if result['num_results'] > 0:
            print("\nTop result:")
            top_meta = result['raw_results']['metadatas'][0]
            top_doc = result['raw_results']['documents'][0][:200]
            print(f"  Source: {top_meta.get('source')}")
            print(f"  Control: {top_meta.get('control_id') or top_meta.get('category')}")
            print(f"  Content: {top_doc}...")

        # Test multiple vulnerabilities
        print("\n4. Testing multiple vulnerabilities retrieval...")
        test_vulns = [
            {
                'title': 'Cross-Site Scripting (XSS)',
                'category': 'XSS',
                'description': 'Reflected XSS in search parameter'
            },
            {
                'title': 'Weak Password Policy',
                'category': 'Authentication',
                'description': 'No minimum password length enforced'
            }
        ]

        multi_result = retriever.retrieve_for_vulnerabilities(test_vulns, top_k=2)
        print(f"\nProcessed {multi_result['vulnerability_count']} vulnerabilities")
        print(f"Found {len(multi_result['unique_controls'])} unique controls:")
        for control in multi_result['unique_controls'][:5]:
            print(f"  - {control}")

        # Test category search
        print("\n5. Testing category-based retrieval...")
        category_result = retriever.retrieve_by_category("access control", top_k=5)
        print(f"\nCategory: {category_result['category']}")
        print(f"Found {category_result['num_results']} sections")

        # Show formatted context example
        print("\n6. Example formatted context:")
        print("-" * 60)
        print(result['formatted_context'][:500])
        print("...")
        print("-" * 60)

        print("\nCompliance Retriever test completed successfully!")

    except FileNotFoundError:
        print("\nERROR: Vector database not found!")
        print("Please run: python backend/rag/init_vectordb.py")
        sys.exit(1)

    except Exception as e:
        print(f"\nERROR: Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
