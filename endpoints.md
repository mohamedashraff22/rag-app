# RAG Application Endpoints

This document outlines all the available API endpoints for the RAG application, designed to help set up a Postman collection.

## Base URL
Assuming the app is running locally on port 8000:
`http://localhost:8000`

---

## 1. Base Endpoint

### Welcome
*   **Method**: `GET`
*   **Endpoint**: `/api/v1/`
*   **Description**: Checks if the API is up and returns basic application information.
*   **Payload**: None
*   **Successful Output (HTTP 200)**:
    ```json
    {
      "app_name": "rag-app",
      "app_version": "0.1"
    }
    ```

---

## 2. Data Endpoints

### Upload File
*   **Method**: `POST`
*   **Endpoint**: `/api/v1/data/upload/{project_id}`
*   **Description**: Uploads a document (e.g., PDF, TXT) to be associated with a specific project.
*   **Path Variables**:
    *   `project_id` (string): The identifier for your project.
*   **Payload (form-data)**:
    *   `file`: The file to upload.
*   **Successful Output (HTTP 200)**:
    ```json
    {
        "signal": "File uploaded successfully.",
        "file_id": "651a2b3c4d5e..."
    }
    ```
*   **Error Output (HTTP 400)**: returns appropriate `signal` message (e.g. invalid type, size exceeded, upload failed).

### Process Files
*   **Method**: `POST`
*   **Endpoint**: `/api/v1/data/process/{project_id}`
*   **Description**: Parses and chunks either a specific file or all files in a project, preparing them for vectorization.
*   **Path Variables**:
    *   `project_id` (string): The identifier for your project.
*   **Payload (JSON)**:
    ```json
    {
        "file_id": "string",  // Optional. If null, processes all files in project
        "chunk_size": 100,    // Optional. Default 100
        "chunk_overlap": 20,  // Optional. Default 20
        "do_reset": 0         // Optional. 1 to reset chunks & vectors, 0 to append (default)
    }
    ```
*   **Successful Output (HTTP 200)**:
    ```json
    {
        "signal": "Processing successfully.",
        "inserted_chunks": 54,
        "processed_files": 1
    }
    ```
*   **Error Output (HTTP 400)**: returns appropriate `signal` message.

---

## 3. NLP Endpoints

### Push to Vector DB
*   **Method**: `POST`
*   **Endpoint**: `/api/v1/nlp/index/push/{project_id}`
*   **Description**: Embeds the processed text chunks and indexes them into the vector database.
*   **Path Variables**:
    *   `project_id` (string): The identifier for your project.
*   **Payload (JSON)**:
    ```json
    {
        "do_reset": 0  // Optional. 1 to recreate collection, 0 to append (default)
    }
    ```
*   **Successful Output (HTTP 200)**:
    ```json
    {
        "signal": "Successfully inserted into vector database.",
        "inserted_items_count": 54
    }
    ```
*   **Error Output (HTTP 400)**: returns appropriate `signal` message.

### Get Index Info
*   **Method**: `GET`
*   **Endpoint**: `/api/v1/nlp/index/info/{project_id}`
*   **Description**: Retrieves statistics and metadata about the project's vector collection.
*   **Path Variables**:
    *   `project_id` (string): The identifier for your project.
*   **Payload**: None
*   **Successful Output (HTTP 200)**:
    ```json
    {
        "signal": "Vector database collection retrieved.",
        "collection_info": {
            // ... detailed DB specific stats
        }
    }
    ```

### Search Index
*   **Method**: `POST`
*   **Endpoint**: `/api/v1/nlp/index/search/{project_id}`
*   **Description**: Performs semantic search against the indexed documents.
*   **Path Variables**:
    *   `project_id` (string): The identifier for your project.
*   **Payload (JSON)**:
    ```json
    {
        "text": "Your search query here", // Required
        "limit": 5                      // Optional. Default is 5
    }
    ```
*   **Successful Output (HTTP 200)**:
    ```json
    {
        "signal": "Vector database search successful.",
        "results": [
            {
                "text": "The relevant chunk text...",
                "score": 0.893
            },
            // ... more results
        ]
    }
    ```
*   **Error Output (HTTP 400)**: returns appropriate `signal` message if search errors occur.

### Answer Question (RAG)
*   **Method**: `POST`
*   **Endpoint**: `/api/v1/nlp/index/answer/{project_id}`
*   **Description**: Queries the system using Retrieval-Augmented Generation to get a generated answer based on retrieved documents.
*   **Path Variables**:
    *   `project_id` (string): The identifier for your project.
*   **Payload (JSON)**:
    ```json
    {
        "text": "Your factual question here", // Required
        "limit": 5                          // Optional. Default is 5
    }
    ```
*   **Successful Output (HTTP 200)**:
    ```json
    {
        "signal": "RAG answer generated successfully.",
        "answer": "The generated answer from the LLM.",
        "full_prompt": "The complete prompt sent to the LLM (including retrieved context)",
        "chat_history": [
            // List of message dictionaries sent to the LLM
        ]
    }
    ```
*   **Error Output (HTTP 400)**: returns appropriate `signal` message if answering fails.
