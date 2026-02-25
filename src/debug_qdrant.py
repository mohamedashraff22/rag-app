import qdrant_client
import sys

print("--- Qdrant Debug Info ---")
print(f"Library Location: {qdrant_client.__file__}")

try:
    print(f"Library Version: {qdrant_client.__version__}")
except AttributeError:
    print("⚠️ Version attribute missing (Ignored)")

from qdrant_client import QdrantClient

print(f"\nImported QdrantClient: {QdrantClient}")

# THE REAL TEST: Check for 'search'
if hasattr(QdrantClient, 'search'):
    print("✅ Success: QdrantClient has the 'search' method.")
else:
    print("❌ Error: QdrantClient is missing 'search'.")
    print("Available public methods:", [m for m in dir(QdrantClient) if not m.startswith("_")])

# Try to initialize
try:
    client = QdrantClient(":memory:")
    print("✅ Client initialized successfully.")
except Exception as e:
    print(f"❌ Client initialization failed: {e}")