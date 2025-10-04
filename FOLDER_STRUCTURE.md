# Jarvis-Lite v0.2: Detailed Folder Structure & Architecture

## 📁 Complete Folder Structure

```
jarvis-lite/
├── 📄 main.py                    # CLI entry point and user interface
├── 📄 agent.py                   # Core agent logic and tool orchestration
├── 📄 planner.py                 # LLM-powered tool selection and planning
├── 📄 memory.py                  # Conversation and long-term memory management
├── 📄 llm_client.py              # LLM provider abstraction layer
├── 📄 api_server.py              # FastAPI REST server for programmatic access
├── 📄 rag_index.py               # RAG index building and management
├── 📄 requirements.txt           # Python dependencies
├── 📄 .env.example              # Environment configuration template
├── 📄 .env                      # Actual environment configuration (user-created)
├── 📄 README.md                 # Project documentation
├── 📄 CAPABILITIES.md           # Detailed capabilities and examples
├── 📄 FOLDER_STRUCTURE.md       # This file - architecture documentation
├── 📁 tools/                    # Tool implementations
│   ├── 📄 __init__.py           # Python package initialization
│   ├── 📄 news.py               # Advanced news aggregation tool
│   ├── 📄 web_search.py         # Web search and content extraction
│   ├── 📄 notes.py              # Note management system
│   ├── 📄 tasks.py              # Task management system
│   ├── 📄 rag.py                # RAG query interface
│   └── 📄 python_tool.py        # Safe Python evaluation
├── 📁 knowledge/                # User documents for RAG (user-created)
│   ├── 📄 *.pdf                 # Research papers, reports
│   ├── 📄 *.md                  # Markdown documents
│   └── 📄 *.txt                 # Text files
├── 📁 .chroma/                  # ChromaDB vector storage (auto-created)
│   ├── 📄 chroma.sqlite3        # Vector database
│   └── 📄 [collection data]     # Embeddings and metadata
└── 📄 jarvis.db                 # SQLite database for memory/tasks/notes
```

## 🏗️ Core Components Explained

### 📄 `main.py` - CLI Interface
**Purpose**: Command-line interface for user interaction

**Key Functions**:
- `run()`: Main interactive loop
- User input handling and display formatting
- Rich library integration for beautiful output

**Flow**:
1. Initialize Agent instance
2. Display welcome message
3. Enter interactive loop
4. Process user input through Agent.step()
5. Display responses with formatting
6. Handle exit commands

**Dependencies**: `agent.py`, `rich` library

---

### 📄 `agent.py` - Core Agent Logic
**Purpose**: Central orchestrator implementing ReAct (Reason → Act → Reflect) pattern

**Key Classes**:
- `Agent`: Main agent class with tool orchestration

**Key Methods**:
- `__init__(db_path)`: Initialize with memory and LLM client
- `step(user_input)`: Process user query through complete cycle
- `_llm(messages)`: Helper for LLM calls

**Processing Flow**:
1. **Reason**: Get conversation history from memory
2. **Plan**: Use LLM to select appropriate tool and arguments
3. **Act**: Execute selected tool with provided arguments
4. **Reflect**: Generate final response based on tool output
5. **Remember**: Store conversation in memory

**Tool Integration**:
- `news_query`: Advanced news aggregation
- `web_search`: General web search
- `notes_add/notes_find`: Note management
- `task_add/task_list/task_done`: Task management
- `rag_query`: Document search
- `python_calc`: Safe calculations

**Dependencies**: `memory.py`, `llm_client.py`, `planner.py`, all tools

---

### 📄 `planner.py` - Tool Selection Logic
**Purpose**: LLM-powered decision making for tool selection

**Key Components**:
- `SYSTEM`: System prompt defining available tools and JSON format
- `build_messages()`: Construct conversation context for LLM
- `parse_plan()`: Extract JSON plan from LLM response

**Tool Selection Process**:
1. Build message history with system prompt
2. Send to LLM for tool selection
3. Parse JSON response with tool, args, and thought
4. Fallback to web_search if parsing fails

**Available Tools**:
- `news_query`: News aggregation
- `web_search`: Web search
- `notes_add/notes_find`: Note operations
- `task_add/task_list/task_done`: Task operations
- `rag_query`: Document search
- `python_calc`: Calculations
- `final`: Direct response

**Dependencies**: `json` library

---

### 📄 `memory.py` - Persistent Storage
**Purpose**: Conversation and long-term memory management

**Key Classes**:
- `Memory`: SQLite-based memory management

**Database Tables**:
- `conv`: Conversation history (id, role, content)
- `long_memory`: Persistent key-value storage (k, v)

**Key Methods**:
- `add_conv(role, content)`: Store conversation turn
- `last_k(k)`: Retrieve last k conversation messages
- `set(key, value)`: Store persistent data
- `get(key, default)`: Retrieve persistent data

**Features**:
- Automatic database migration
- Conversation context management
- User preference storage
- Tool result caching

**Dependencies**: `sqlite3`, `json`, `os`

---

### 📄 `llm_client.py` - LLM Abstraction
**Purpose**: Unified interface for multiple LLM providers

**Key Classes**:
- `LLMClient`: Multi-provider LLM interface

**Supported Providers**:
- **Ollama**: Local models (default)
- **OpenAI**: OpenAI API and compatible servers
- **Groq**: Groq API for fast inference

**Configuration**:
- Provider selection via environment variables
- Model configuration per provider
- API key and endpoint management
- Timeout and error handling

**Key Methods**:
- `__init__()`: Initialize provider and model
- `chat(messages, temperature)`: Send chat completion request

**Dependencies**: `os`, `json`, `requests`, `dotenv`

---

## 🛠️ Tools Directory Deep Dive

### 📄 `tools/news.py` - Advanced News Tool
**Purpose**: Multi-source news aggregation with credibility scoring

**Key Functions**:
- `search_news()`: Search news from multiple sources
- `multi_fetch_and_merge()`: Fetch content from multiple URLs
- `credibility()`: Calculate source credibility scores
- `news_bundle()`: High-level news processing with LLM

**Features**:
- **Multi-source aggregation**: Reuters, BBC, NDTV, The Hindu, etc.
- **Credibility scoring**: 0.5-0.95 based on source trustworthiness
- **API integration**: GNews and NewsAPI support
- **Retry logic**: Tenacity-based error handling
- **Hierarchical summarization**: Process long content in chunks
- **Fallback mechanisms**: Title-only summaries when content fails

**Credibility Scores**:
```python
TRUST = {
    "bbc.com": 0.95,
    "reuters.com": 0.95,
    "thehindu.com": 0.9,
    "indianexpress.com": 0.85,
    "ndtv.com": 0.85,
    "timesofindia.indiatimes.com": 0.8,
}
```

**Dependencies**: `requests`, `ddgs`, `tenacity`, `beautifulsoup4`, `readability`

---

### 📄 `tools/web_search.py` - Web Search Tool
**Purpose**: General web search with content extraction

**Key Functions**:
- `search(query, max_results)`: DuckDuckGo search
- `fetch_clean(url, max_chars)`: Extract and clean web content

**Features**:
- DuckDuckGo search integration
- Content extraction using readability-lxml
- HTML cleaning with BeautifulSoup
- Timeout and error handling
- Character limit enforcement

**Dependencies**: `ddgs`, `requests`, `beautifulsoup4`, `readability`

---

### 📄 `tools/notes.py` - Note Management
**Purpose**: Personal note storage and retrieval

**Key Functions**:
- `add(conn, text)`: Add new note with timestamp
- `find(conn, query, limit)`: Search notes by keywords

**Database Schema**:
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    text TEXT,
    created_at DEFAULT CURRENT_TIMESTAMP
);
```

**Features**:
- Full-text search with LIKE queries
- Automatic timestamps
- SQLite persistence
- Keyword-based retrieval

**Dependencies**: `sqlite3`

---

### 📄 `tools/tasks.py` - Task Management
**Purpose**: Personal task tracking and completion

**Key Functions**:
- `add(conn, text)`: Add new task
- `list_tasks(conn, only_open)`: List pending/completed tasks
- `mark_done(conn, task_id)`: Mark task as complete

**Database Schema**:
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    text TEXT,
    done INTEGER DEFAULT 0,
    created_at DEFAULT CURRENT_TIMESTAMP
);
```

**Features**:
- Task creation and completion
- Status tracking (pending/done)
- Timestamped entries
- SQLite persistence

**Dependencies**: `sqlite3`

---

### 📄 `tools/rag.py` - RAG Query Interface
**Purpose**: Document search and retrieval using vector embeddings

**Key Functions**:
- `query(q, k)`: Semantic search over documents
- `_embedder()`: Lazy loading of embedding model

**Features**:
- Sentence-transformers embeddings
- ChromaDB vector storage
- Semantic similarity search
- Path-based source tracking

**Configuration**:
- Embed model: `sentence-transformers/all-MiniLM-L6-v2`
- Vector store: ChromaDB persistent client
- Collection: `jarvis_knowledge`

**Dependencies**: `chromadb`, `sentence-transformers`, `os`

---

### 📄 `tools/python_tool.py` - Safe Python Evaluation
**Purpose**: Secure Python expression evaluation for calculations

**Key Functions**:
- `calc(expr)`: Evaluate mathematical expressions

**Security Features**:
- No imports allowed
- Limited builtins (`abs`, `round`)
- Sandboxed execution environment
- Expression-only evaluation

**Allowed Operations**:
- Mathematical calculations
- Basic data structures
- String operations
- List comprehensions

**Dependencies**: None (pure Python)

---

## 🗄️ Data Storage Architecture

### 📄 `jarvis.db` - SQLite Database
**Purpose**: Central storage for conversations, notes, and tasks

**Tables**:
1. **conv**: Conversation history
   - `id`: Primary key
   - `role`: user/assistant/system
   - `content`: Message content

2. **long_memory**: Persistent key-value storage
   - `k`: Key (string)
   - `v`: JSON value

3. **notes**: User notes
   - `id`: Primary key
   - `text`: Note content
   - `created_at`: Timestamp

4. **tasks**: Task management
   - `id`: Primary key
   - `text`: Task description
   - `done`: Completion status
   - `created_at`: Timestamp

**Features**:
- ACID compliance
- Automatic migrations
- Index optimization
- Cross-platform compatibility

---

### 📁 `.chroma/` - Vector Database
**Purpose**: ChromaDB storage for document embeddings

**Contents**:
- `chroma.sqlite3`: Main vector database
- Collection metadata and embeddings
- Document chunks and metadata

**Configuration**:
- Persistent client mode
- Local file storage
- Automatic indexing
- Metadata preservation

**Features**:
- Semantic search capabilities
- Efficient similarity queries
- Scalable storage
- Metadata filtering

---

### 📁 `knowledge/` - User Documents
**Purpose**: User-provided documents for RAG system

**Supported Formats**:
- **PDF**: Research papers, reports, books
- **Markdown**: Documentation, notes, articles
- **Text**: Plain text documents

**Processing**:
- Automatic text extraction
- Chunking for large documents
- Metadata preservation
- Embedding generation

**Best Practices**:
- Organize by topic/project
- Use descriptive filenames
- Keep documents updated
- Remove duplicates

---

## 🌐 API Server Architecture

### 📄 `api_server.py` - FastAPI Server
**Purpose**: REST API for programmatic access to Jarvis-Lite

**Key Components**:
- FastAPI application instance
- Agent integration
- Pydantic models for validation

**Endpoints**:
- `POST /ask`: Query the agent
  - Request: `{"prompt": "user query"}`
  - Response: `{"answer": "agent response"}`

**Features**:
- Automatic documentation
- Request validation
- Error handling
- CORS support
- Health checks

**Dependencies**: `fastapi`, `uvicorn`, `pydantic`

---

## ⚙️ Configuration System

### 📄 `.env` - Environment Configuration
**Purpose**: Runtime configuration and secrets

**Key Sections**:
1. **LLM Configuration**
   - Provider selection
   - Model specification
   - API keys and endpoints

2. **News Configuration**
   - API integration settings
   - Source preferences
   - Regional settings

3. **RAG Configuration**
   - Embedding models
   - Storage paths
   - Database settings

4. **System Configuration**
   - Database paths
   - Timeout settings
   - Debug options

**Security**:
- Never commit to version control
- Use `.env.example` as template
- Restrict file permissions
- Validate on startup

---

## 🔄 Data Flow Architecture

### Query Processing Flow
```
User Input → main.py → agent.step()
    ↓
1. Memory: Get conversation context
    ↓
2. Planner: Select tool and arguments
    ↓
3. Tool Execution: Process request
    ↓
4. Reflection: Generate response
    ↓
5. Memory: Store conversation
    ↓
Response → main.py → User Display
```

### Tool-Specific Flows

#### News Query Flow:
```
news: query → news_tool.search_news()
    ↓
Multi-source aggregation (APIs + DDG)
    ↓
Credibility sorting
    ↓
Content fetching (3 sources)
    ↓
Hierarchical summarization
    ↓
Response with citations
```

#### RAG Query Flow:
```
ask rag: query → rag.query()
    ↓
Embedding generation
    ↓
ChromaDB similarity search
    ↓
Document retrieval
    ↓
Context assembly
    ↓
LLM response generation
```

---

## 🚀 Deployment Architecture

### Development Setup
```
Virtual Environment
├── Python 3.8+
├── Dependencies (requirements.txt)
├── Environment (.env)
└── Local storage (SQLite + ChromaDB)
```

### Production Considerations
```
Production Server
├── Container/Docker deployment
├── Environment variable management
├── Persistent volume mounting
├── Load balancing (API mode)
└── Monitoring and logging
```

### Scaling Architecture
```
Horizontal Scaling
├── Multiple API instances
├── Shared database storage
├── Load balancer
└── Caching layer
```

---

## 🔧 Extension Points

### Adding New Tools
1. Create tool file in `tools/`
2. Implement required functions
3. Add tool to `planner.py` system prompt
4. Add tool handling in `agent.py`
5. Update documentation

### Custom LLM Providers
1. Add provider logic to `llm_client.py`
2. Update environment configuration
3. Test integration
4. Update documentation

### Database Extensions
1. Modify `memory.py` migration logic
2. Add new tables/indices
3. Update relevant tools
4. Handle backward compatibility

---

## 📊 Performance & Monitoring

### Key Metrics
- Response time per tool
- Database query performance
- Memory usage patterns
- Error rates and types
- User interaction patterns

### Optimization Points
- Database indexing
- Caching strategies
- Connection pooling
- Async operations
- Resource cleanup

### Monitoring Tools
- SQLite query analysis
- ChromaDB performance metrics
- LLM response times
- System resource usage
- Application logging

This architecture provides a robust, scalable foundation for an AI assistant that can be easily extended and maintained while preserving user privacy through local-first design.
