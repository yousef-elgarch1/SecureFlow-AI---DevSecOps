"""
Initialize vector database with compliance documents
Run this script once to populate the database
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.document_loader import DocumentLoader
from rag.vector_store import VectorStore


def initialize_database(reset=False):
    """
    Initialize vector database with NIST CSF and ISO 27001 documents

    Args:
        reset: If True, reset existing database before adding documents
    """
    print("="*60)
    print("INITIALIZING VECTOR DATABASE")
    print("="*60)

    # Paths to compliance documents
    nist_path = os.path.join(
        os.path.dirname(__file__),
        "../../data/compliance_docs/nist_csf_summary.txt"
    )
    iso_path = os.path.join(
        os.path.dirname(__file__),
        "../../data/compliance_docs/iso27001_annexa.txt"
    )

    vector_db_path = os.path.join(
        os.path.dirname(__file__),
        "../../vector_db"
    )

    try:
        # Step 1: Load documents
        print("\nStep 1: Loading compliance documents...")
        loader = DocumentLoader()
        chunks = loader.load_all_documents(nist_path, iso_path)

        if not chunks:
            print("ERROR: No documents loaded!")
            return False

        # Step 2: Initialize vector store
        print("\nStep 2: Initializing vector store...")
        vector_store = VectorStore(persist_directory=vector_db_path)

        # Reset if requested
        if reset:
            print("\nResetting existing database...")
            vector_store.reset()

        # Check if already populated
        existing_count = vector_store.count()
        if existing_count > 0 and not reset:
            print(f"\nDatabase already contains {existing_count} documents")
            response = input("Do you want to add more documents anyway? (y/n): ")
            if response.lower() != 'y':
                print("Initialization cancelled")
                return True

        # Step 3: Add documents to vector store
        print("\nStep 3: Adding documents to vector database...")
        print(f"(This may take a moment - embedding {len(chunks)} chunks)")
        vector_store.add_documents(chunks)

        # Step 4: Verify
        print("\nStep 4: Verifying database...")
        final_count = vector_store.count()
        print(f"Total documents in database: {final_count}")

        # Step 5: Test search
        print("\nStep 5: Testing search functionality...")
        test_queries = [
            "SQL injection prevention",
            "access control management",
            "incident response"
        ]

        for query in test_queries:
            results = vector_store.search(query, top_k=2)
            print(f"\nQuery: '{query}'")
            if results['documents']:
                print(f"  Top result: {results['metadatas'][0].get('source')} - {results['metadatas'][0].get('control_id', results['metadatas'][0].get('category', 'N/A'))}")
            else:
                print("  No results found")

        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        print(f"\nDatabase location: {vector_db_path}")
        print(f"Total documents: {final_count}")
        print("\nYou can now use the RAG system for policy generation!")

        return True

    except Exception as e:
        print(f"\nERROR: Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Initialize vector database with compliance documents")
    parser.add_argument("--reset", action="store_true", help="Reset database before initialization")
    args = parser.parse_args()

    success = initialize_database(reset=args.reset)

    if success:
        print("\nInitialization successful!")
        sys.exit(0)
    else:
        print("\nInitialization failed!")
        sys.exit(1)
