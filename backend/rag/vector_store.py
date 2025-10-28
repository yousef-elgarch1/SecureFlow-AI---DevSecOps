"""
Vector database management using ChromaDB
"""

import os
from typing import List, Dict, Optional
try:
    import chromadb
    from chromadb.utils import embedding_functions
except ImportError:
    print("Warning: chromadb not installed. Run: pip install chromadb")
    chromadb = None


class VectorStore:
    """Manage vector database for compliance documents"""

    def __init__(self, persist_directory: str = "./vector_db", collection_name: str = "compliance_docs"):
        """
        Initialize ChromaDB vector store

        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection
        """
        if chromadb is None:
            raise ImportError("chromadb not installed. Run: pip install chromadb")

        self.persist_directory = persist_directory
        self.collection_name = collection_name

        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Use sentence transformers for embeddings
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
            metadata={"description": "NIST CSF and ISO 27001 compliance documents"}
        )

    def add_documents(self, documents: List[Dict]) -> None:
        """
        Add documents to vector store

        Args:
            documents: List of document dicts with 'text' and metadata
        """
        if not documents:
            print("No documents to add")
            return

        # Extract texts and metadata
        texts = [doc["text"] for doc in documents]
        metadatas = []
        ids = []

        for i, doc in enumerate(documents):
            # Create metadata dict (exclude 'text' field)
            metadata = {k: str(v) for k, v in doc.items() if k != "text"}
            metadatas.append(metadata)

            # Create unique ID
            doc_id = f"{doc.get('source', 'unknown').replace(' ', '_')}_{i}"
            ids.append(doc_id)

        # Add to collection in batches
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            end_idx = min(i + batch_size, len(documents))

            self.collection.add(
                documents=texts[i:end_idx],
                metadatas=metadatas[i:end_idx],
                ids=ids[i:end_idx]
            )

            print(f"  Added batch {i//batch_size + 1}: {end_idx - i} documents")

        print(f"Successfully added {len(documents)} documents to vector store")

    def search(self, query: str, top_k: int = 10, filter_dict: Optional[Dict] = None) -> Dict:
        """
        Search for relevant documents

        Args:
            query: Search query
            top_k: Number of results to return
            filter_dict: Optional metadata filter

        Returns:
            Dict with documents, metadatas, and distances
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=filter_dict if filter_dict else None
            )

            return {
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else []
            }

        except Exception as e:
            print(f"Search error: {e}")
            return {"documents": [], "metadatas": [], "distances": []}

    def count(self) -> int:
        """Get number of documents in collection"""
        return self.collection.count()

    def reset(self) -> None:
        """Delete all documents from collection"""
        try:
            self.client.delete_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' deleted")

            # Recreate collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"description": "NIST CSF and ISO 27001 compliance documents"}
            )
            print(f"Collection '{self.collection_name}' recreated")

        except Exception as e:
            print(f"Error resetting collection: {e}")


# Test function
if __name__ == "__main__":
    print("="*60)
    print("VECTOR STORE TEST")
    print("="*60)

    try:
        # Initialize vector store
        print("\n1. Initializing vector store...")
        vector_store = VectorStore(persist_directory="../../vector_db_test")

        # Test with sample documents
        print("\n2. Adding sample documents...")
        sample_docs = [
            {
                "text": "All database queries must use parameterized statements to prevent SQL injection attacks per ISO 27001 A.14.2.5",
                "source": "ISO 27001",
                "control_id": "A.14.2.5",
                "theme": "Technological"
            },
            {
                "text": "Access permissions and authorizations must be managed according to least privilege principle (NIST CSF PR.AC-4)",
                "source": "NIST CSF",
                "function": "PROTECT",
                "category": "PR.AC"
            },
            {
                "text": "Security testing must be performed in development lifecycle per ISO 27001 A.8.29",
                "source": "ISO 27001",
                "control_id": "A.8.29",
                "theme": "Technological"
            }
        ]

        vector_store.add_documents(sample_docs)

        # Test search
        print("\n3. Testing search...")
        query = "SQL injection prevention database security"
        results = vector_store.search(query, top_k=2)

        print(f"\nSearch query: '{query}'")
        print(f"Found {len(results['documents'])} results:")

        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'],
            results['metadatas'],
            results['distances']
        )):
            print(f"\nResult {i+1}:")
            print(f"  Source: {metadata.get('source', 'N/A')}")
            print(f"  Distance: {distance:.4f}")
            print(f"  Text: {doc[:150]}...")

        # Test count
        print(f"\n4. Total documents in store: {vector_store.count()}")

        print("\nVector Store test completed successfully!")

    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
