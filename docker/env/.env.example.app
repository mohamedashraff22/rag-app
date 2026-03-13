APP_NAME="rag-app"
APP_VERSION="0.1"
OPENAI_API_KEY=""

# only allow text files and PDFs
FILE_ALLOWED_TYPES=["text/plain", "application/pdf"] 
FILE_MAX_SIZE=10 
# 512KB , as if we have many users with large sized files we dont want the temporary memory to be filled with them at a time so we use chunks
FILE_DEFAULT_CHUNCK_SIZE=512000 

# MONGODB_URL="mongodb://admin:admin@localhost:27007"
# MONGODB_DATABASE="rag-app"

POSTGRES_USERNAME="postgres"
POSTGRES_PASSWORD="ragapp22"
POSTGRES_HOST="pgvector"
POSTGRES_PORT=5432
POSTGRES_MAIN_DATABASE="ragapp"

# ========================= LLM Config =========================
GENERATION_BACKEND = "OPENAI"
EMBEDDING_BACKEND = "OPENAI"

OPENAI_API_URL=
OPENAI_API_URL="https://brycen-obliterative-camie.ngrok-free.dev/v1" # generated from ngrok
COHERE_API_KEY=""

 # "gpt-5-nano"  "text-embedding-3-small"
GENERATION_MODEL_ID_LITERAL = ["gpt-5-nano", "gemma2:9b-instruct-q5_0"]
GENERATION_MODEL_ID="gemma2:9b-instruct-q5_0"
EMBEDDING_MODEL_ID="qwen3-embedding:0.6b"
EMBEDDING_MODEL_SIZE=1024 # 1536

INPUT_DAFAULT_MAX_CHARACTERS=2024
GENERATION_DAFAULT_MAX_TOKENS=2000
GENERATION_DAFAULT_TEMPERATURE=1.0

# ========================= Vector DB Config =========================
VECTOR_DB_BACKEND_LITERAL = ["QDRANT", "PGVECTOR"]
VECTOR_DB_BACKEND="PGVECTOR"
VECTOR_DB_PATH="qdrant_db"
VECTOR_DB_DISTANCE_METHOD="cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD=300

# ========================= Template Configs =========================
PRIMARY_LANG="en"
DEFAULT_LANG="en"