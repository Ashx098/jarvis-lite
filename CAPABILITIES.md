# Jarvis-Lite v0.2: Complete Capabilities & Examples

## 🎯 Overview

Jarvis-Lite v0.2 is a local-first AI agent that provides real tools for web search, news, note-taking, task management, and local RAG. It uses a ReAct-style (Reason → Act → Reflect) approach to answer queries and perform tasks.

## 🛠️ Available Tools

### 1. **News Tool** (`news_query`)
**Purpose**: Multi-source news headlines with credibility weighting and summarization

#### Capabilities:
- Multi-source news aggregation from trusted sources
- Credibility scoring for news sources
- API integration (GNews, NewsAPI) with fallback to web search
- Hierarchical summarization of news content
- Retry logic for robust fetching

#### Credibility Scores:
- BBC, Reuters: 0.95 (Highest)
- The Hindu: 0.90
- Indian Express, NDTV: 0.85
- Times of India: 0.80
- Other sources: 0.50 (Default)

#### Examples:
```bash
# General news queries
> news: india top headlines today
> news: latest ai policy india
> news: ISRO today
> news: technology news this week

# Specific topics
> news: climate change summit
> news: stock market today
> news: sports cricket
```

#### Sample Output:
```
Agent: Here are today's top India headlines:

• Major tech companies announce AI investments in India (Reuters)
• Government launches new digital initiative (The Hindu)
• Stock market reaches record highs (NDTV)
• Weather department issues rainfall alert (Indian Express)

Sources: https://reuters.com/world/india/, https://thehindu.com/, ...
```

---

### 2. **Web Search Tool** (`web_search`)
**Purpose**: General web search with content extraction and summarization

#### Capabilities:
- DuckDuckGo search integration
- Content extraction from web pages
- Automatic summarization of fetched content
- Timeout and error handling

#### Examples:
```bash
# Information queries
> web: what is quantum computing
> web: best cycle routes in Bangalore Koramangala 10km
> web: python machine learning libraries
> web: how to make dosa recipe

# Research queries
> web: latest developments in renewable energy
> web: history of artificial intelligence
> web: economic impact of covid-19
```

#### Sample Output:
```
Agent: Quantum computing is a revolutionary computing paradigm that uses quantum mechanical phenomena 
like superposition and entanglement to process information. Unlike classical computers that use bits 
(0 or 1), quantum computers use qubits which can exist in multiple states simultaneously...

Source: https://example.com/quantum-computing
```

---

### 3. **Notes Tool** (`notes_add`, `notes_find`)
**Purpose**: Personal note management with SQLite storage

#### Capabilities:
- Add quick notes with timestamps
- Search notes by keywords
- Persistent storage in SQLite database
- Full-text search functionality

#### Examples:
```bash
# Adding notes
> note: BRAGS ideas – try multi-objective BO
> note: Meeting with Saheb tomorrow at 3pm
> note: Buy groceries: milk, bread, eggs
> note: Python code snippet: def hello_world(): print("Hello")

# Finding notes
> find notes: BRAGS
> find notes: meeting
> find notes: python
> find notes: groceries
```

#### Sample Output:
```
Agent: Note added successfully: "BRAGS ideas – try multi-objective BO"

Agent: Found 2 matching notes:
1. "BRAGS ideas – try multi-objective BO" (2025-10-04 15:30)
2. "Review BRAGS algorithm performance" (2025-10-03 10:15)
```

---

### 4. **Tasks Tool** (`task_add`, `task_list`, `task_done`)
**Purpose**: Task management with SQLite storage

#### Capabilities:
- Add tasks with automatic timestamps
- List pending tasks
- Mark tasks as complete
- Persistent task storage

#### Examples:
```bash
# Adding tasks
> add task: email Saheb the loss curves by 6pm
> add task: finish project documentation
> add task: call mom this weekend
> add task: review pull requests

# Listing tasks
> list tasks
> show tasks

# Completing tasks
> done task: 1
> complete task: email Saheb
> mark done: 3
```

#### Sample Output:
```
Agent: Task added: "email Saheb the loss curves by 6pm"

Agent: Pending tasks:
1. email Saheb the loss curves by 6pm (Added: 2025-10-04 15:30)
2. finish project documentation (Added: 2025-10-04 14:20)
3. call mom this weekend (Added: 2025-10-04 12:10)

Agent: Task marked as complete: "email Saheb the loss curves by 6pm"
```

---

### 5. **RAG Tool** (`rag_query`)
**Purpose**: Question answering over local documents using vector search

#### Capabilities:
- Semantic search over PDF, Markdown, and text files
- Vector embeddings using sentence-transformers
- ChromaDB for efficient vector storage
- Context-aware document retrieval

#### Setup:
```bash
# 1. Place documents in knowledge/ folder
mkdir knowledge
# Add your PDFs, .md, .txt files

# 2. Build index
python rag_index.py --rebuild

# 3. Query documents
> ask rag: what did my MailGuard paper claim about privacy?
> ask rag: summarize the Q3 report
> ask rag: what are the key findings from the research?
```

#### Sample Output:
```
Agent: Based on your MailGuard paper, it claims that:
- Privacy-preserving email filtering is achievable through encrypted pattern matching
- The system maintains 95% accuracy while protecting user data
- Computational overhead is minimal (<5% performance impact)

Source: knowledge/MailGuard_Paper.pdf
```

---

### 6. **Python Tool** (`python_calc`)
**Purpose**: Safe Python expression evaluation for calculations

#### Capabilities:
- Mathematical calculations
- Safe evaluation (no imports, limited builtins)
- Quick computations and data analysis

#### Examples:
```bash
# Mathematical calculations
> calc: (15% CAGR SIP on 80k for 36 months)
> calc: 2^10 + sqrt(100)
> calc: sin(30 degrees) * cos(45 degrees)
> calc: compound_interest(100000, 0.08, 5)

# Data calculations
> calc: [1,2,3,4,5].mean()
> calc: sum(range(1, 101))
> calc: len("hello world") * 2
```

#### Sample Output:
```
Agent: (15% CAGR SIP on 80k for 36 months) = 1,52,087.50

Agent: 2^10 + sqrt(100) = 1024 + 10 = 1034
```

## 🎭 Advanced Usage Patterns

### Multi-Step Workflows:
```bash
# Research workflow
> web: latest AI research papers
> note: Found interesting papers on transformers
> add task: read and summarize transformer papers
> ask rag: what do we know about transformers already?

# Daily planning
> news: today's headlines
> list tasks
> add task: follow up on breaking news story
> note: market trends to watch

# Learning workflow
> web: python best practices 2025
> note: important python tips
> calc: time needed to complete python course
> add task: complete python modules
```

### Context-Aware Conversations:
```bash
> note: Working on machine learning project
> web: best ML libraries for 2025
> ask rag: what ML libraries have we used before?
> add task: evaluate new ML libraries
> find notes: machine learning
```

## 🔧 Configuration Options

### Environment Variables (.env):
```bash
# LLM Configuration
LLM_PROVIDER=OLLAMA          # OLLAMA | OPENAI | GROQ
MODEL=llama3.1:8b            # Model name
OPENAI_API_KEY=sk-...        # OpenAI API key
OPENAI_BASE_URL=https://...  # Custom OpenAI endpoint
GROQ_API_KEY=grq-...         # Groq API key
OLLAMA_BASE_URL=http://...   # Ollama server URL

# News Configuration
USE_NEWS_API=false           # Enable news APIs
NEWS_API_PROVIDER=GNEWS      # GNEWS | NEWSAPI
NEWS_API_KEY=...             # News API key
NEWS_COUNTRY=in              # Default country

# RAG Configuration
EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHROMA_DIR=.chroma
DB_PATH=jarvis.db
```

## 🌐 API Usage

### REST API Endpoints:
```bash
# Start API server
uvicorn api_server:app --reload --port 8000

# Make requests
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "news: india headlines"}'

# Response format
{
  "answer": "Here are today's top India headlines..."
}
```

## 📊 Performance Characteristics

### Response Times:
- News queries: 5-15 seconds (with content fetching)
- Web search: 3-10 seconds
- Notes/Tasks: <1 second
- RAG queries: 2-5 seconds
- Python calculations: <1 second

### Resource Usage:
- Memory: ~500MB base + embeddings
- Storage: SQLite DB + ChromaDB vectors
- Network: Required for news/web search
- CPU: Minimal for most operations

## 🚨 Limitations & Considerations

### News Tool:
- Rate limiting on free news APIs
- Some news sites may block access
- Content quality varies by source

### Web Search:
- Limited to DuckDuckGo results
- Some sites may be inaccessible
- Content extraction may fail on complex pages

### RAG System:
- Limited by document quality in knowledge folder
- Vector search accuracy depends on embeddings
- Large documents may need chunking

### General:
- LLM response quality varies by provider
- No real-time data beyond news/web search
- Local processing limits for very large datasets

## 🎯 Best Practices

### For News:
- Use specific queries for better results
- Consider enabling news APIs for reliability
- Verify important information from multiple sources

### For Research:
- Combine web search with RAG for comprehensive results
- Save important findings as notes
- Create tasks for follow-up actions

### For Productivity:
- Regularly review and complete tasks
- Use notes for quick information capture
- Leverage RAG for document-based questions

### For Development:
- Use Python tool for quick calculations
- Combine tools for complex workflows
- Maintain clean knowledge folder for better RAG results
