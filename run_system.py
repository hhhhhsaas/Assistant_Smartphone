"""
Main script to run the Phone Assistant system
"""

import argparse
import logging
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from knowledge_base import VectorStore, EmbeddingModel, PhoneRetriever, DataIndexer
from utils.config import Config
from utils.data_loader import DataLoader

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_knowledge_base():
    """Setup and initialize the knowledge base"""
    logger.info("Setting up Knowledge Base...")

    # Create directories
    Config.create_directories()

    # Initialize components
    embedding_model = EmbeddingModel(Config.EMBEDDING_MODEL)
    vector_store = VectorStore(str(Config.CHROMA_DB_DIR))
    retriever = PhoneRetriever(vector_store, embedding_model)
    indexer = DataIndexer(vector_store, embedding_model)

    return embedding_model, vector_store, retriever, indexer


def index_data(indexer, data_path: str, clear_existing: bool = False):
    """Index data into the knowledge base"""
    logger.info(f"Indexing data from {data_path}...")

    # Load and preprocess data
    data = DataLoader.load_and_preprocess(data_path)
    logger.info(f"Loaded {len(data)} valid phones")

    # Clear existing if requested
    if clear_existing:
        indexer.vector_store.clear_all()
        logger.info("Cleared existing data")

    # Index in batches
    batch_size = 32
    total_indexed = 0

    for i in range(0, len(data), batch_size):
        batch = data[i:i + batch_size]

        # Generate embeddings
        embeddings = []
        ids = []

        for phone in batch:
            embedding = indexer.embedding_model.encode_phone_specs(phone)
            embeddings.append(embedding[0].tolist())

            # Generate ID
            brand = phone.get('brand', 'unknown').lower().replace(' ', '_')
            name = phone.get('name', 'unknown').lower().replace(' ', '_')
            phone_id = f"{brand}_{name}"
            ids.append(phone_id)

        # Add to vector store
        indexer.vector_store.add_phones(batch, embeddings, ids)
        total_indexed += len(batch)

        logger.info(f"Indexed batch {i//batch_size + 1}: {len(batch)} phones")

    logger.info(f"Successfully indexed {total_indexed} phones")
    return total_indexed


def interactive_search(retriever):
    """Run interactive search session"""
    print("\n" + "="*60)
    print("INTERACTIVE SEARCH MODE")
    print("="*60)
    print("Type 'quit' to exit")
    print("Type 'help' for commands")
    print("="*60)

    while True:
        try:
            query = input("\n> Enter your query: ").strip()

            if query.lower() == 'quit':
                print("Goodbye!")
                break

            elif query.lower() == 'help':
                print("\nAvailable commands:")
                print("  search <query>     - Search for phones")
                print("  similar <phone_id> - Find similar phones")
                print("  compare <id1> <id2> - Compare two phones")
                print("  price <min> <max>  - Find phones in price range")
                print("  stats              - Show database statistics")
                print("  quit               - Exit")

            elif query.lower() == 'stats':
                stats = retriever.vector_store.get_stats()
                print(f"\nDatabase Statistics:")
                print(f"  Total phones: {stats['total_phones']}")
                print(f"  Collection: {stats['collection_name']}")

            elif query.lower().startswith('similar '):
                phone_id = query[8:].strip()
                results = retriever.retrieve_similar_phones(phone_id, 5)

                if results:
                    print(f"\nPhones similar to {phone_id}:")
                    for i, result in enumerate(results, 1):
                        phone = result['data']
                        print(f"  {i}. {phone['name']} - {phone['brand']}")
                        print(f"     Price: {phone['price']:,.0f} VND")
                        print(f"     Similarity: {result['score']:.3f}")
                else:
                    print("Phone not found!")

            elif query.lower().startswith('compare '):
                parts = query[8:].strip().split()
                if len(parts) >= 2:
                    comparison = retriever.retrieve_by_comparison(parts[:2])

                    if comparison['phones']:
                        print(f"\nComparing phones:")
                        for phone in comparison['phones']:
                            print(f"  - {phone['name']}")

                        if comparison['comparison']['differences']:
                            print("\nKey differences:")
                            for feature, values in comparison['comparison']['differences'].items():
                                print(f"  {feature}:")
                                for i, phone in enumerate(comparison['phones']):
                                    print(f"    {phone['name']}: {values[i]}")

            elif query.lower().startswith('price '):
                parts = query[6:].strip().split()
                if len(parts) >= 2:
                    try:
                        min_price = int(parts[0])
                        max_price = int(parts[1])

                        phones = retriever.retrieve_by_price_range(min_price, max_price, 10)

                        print(f"\nPhones between {min_price:,} - {max_price:,} VND:")
                        for phone in phones:
                            print(f"  - {phone['name']}: {phone['price']:,.0f} VND")
                    except ValueError:
                        print("Invalid price format! Use: price <min> <max>")

            elif query:
                # Default search
                results = retriever.retrieve_by_query(query, n_results=5)

                if results:
                    print(f"\nSearch results for '{query}':")
                    for i, result in enumerate(results, 1):
                        phone = result['data']
                        print(f"\n{i}. {phone['name']} - {phone['brand']}")
                        print(f"   Price: {phone.get('price', 'N/A'):,.0f} VND")
                        print(f"   Screen: {phone.get('screen_size', 'N/A')}")
                        print(f"   RAM/Storage: {phone.get('ram', 'N/A')}/{phone.get('storage', 'N/A')}")
                        print(f"   Processor: {phone.get('processor', 'N/A')}")
                        print(f"   Relevance: {result['score']:.3f}")
                else:
                    print("No results found!")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_api_server():
    """Run the FastAPI server"""
    import uvicorn
    from api.main import app

    logger.info(f"Starting API server on {Config.API_HOST}:{Config.API_PORT}")
    uvicorn.run(
        app,
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=False
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Phone Assistant System")
    parser.add_argument(
        'command',
        choices=['setup', 'index', 'search', 'api', 'test'],
        help='Command to run'
    )
    parser.add_argument(
        '--data-path',
        default='data/sample_phones.json',
        help='Path to data file for indexing'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing data before indexing'
    )

    args = parser.parse_args()

    # Setup knowledge base
    embedding_model, vector_store, retriever, indexer = setup_knowledge_base()

    if args.command == 'setup':
        logger.info("Knowledge Base setup complete!")
        stats = vector_store.get_stats()
        logger.info(f"Current database has {stats['total_phones']} phones")

    elif args.command == 'index':
        total = index_data(indexer, args.data_path, args.clear)
        logger.info(f"Indexing complete! Indexed {total} phones")

    elif args.command == 'search':
        interactive_search(retriever)

    elif args.command == 'api':
        run_api_server()

    elif args.command == 'test':
        # Run tests
        from test_knowledge_base import test_knowledge_base
        test_knowledge_base()


if __name__ == "__main__":
    main()