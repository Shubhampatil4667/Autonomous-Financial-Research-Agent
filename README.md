# Autonomous Financial Research Agent

A complete production-level AI system that replicates a junior financial analyst workflow using agentic AI with tools, memory, and reasoning.

## Features

- **ReAct Framework**: Thought → Action → Observation loop for dynamic reasoning
- **Plan-and-Execute Mode**: Structured planning and execution
- **Tool Registry**: 12 specialized tools for financial analysis
- **Memory System**: Short-term, long-term, and episodic memory with caching
- **RAG Pipeline**: Query transformation, multi-source retrieval, re-ranking, synthesis
- **Synthesis Engine**: Combines SEC filings, financial data, and news with conflict resolution
- **Error Handling**: Retry logic, fallback tools, graceful degradation
- **Structured Reports**: Professional investment analysis reports
- **Async Processing**: Background task processing for long analyses
- **Logging System**: Comprehensive logging with file and console output
- **Caching**: TTL-based caching for improved performance
- **Containerization**: Docker and Docker Compose support

## Architecture

```
app/
├── agent/          # ReAct & Plan-Execute agents
├── tools/          # 12 financial analysis tools
├── services/       # Memory, RAG, Synthesis, Logging, Cache services
├── models/         # Pydantic schemas
└── api/            # FastAPI backend

frontend/           # Streamlit UI
vector_db/          # Chroma vector store
tests/              # Unit tests
logs/               # Application logs
cache/              # Cache files
```

## Tools Available

1. **sec_filing_search** - Search SEC EDGAR filings
2. **web_search** - Web search via SerpAPI
3. **financial_data_api** - Real-time financial data via yfinance
4. **earnings_transcript** - Earnings call transcripts
5. **news_sentiment** - Sentiment analysis of news
6. **vector_db_search** - Semantic search in vector DB
7. **vector_db_store** - Store content in vector DB
8. **company_profile** - Company profile information
9. **peer_comparison** - Industry peer comparison
10. **report_generator** - Generate investment reports
11. **fact_checker** - Verify facts against context
12. **calculation_engine** - Financial calculations

## Installation

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key
   SERPAPI_KEY=your_serpapi_key  # Optional
   ```

### Docker Deployment

1. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Or build individual containers:
   ```bash
   docker build -t financial-agent .
   docker run -p 8000:8000 -e OPENAI_API_KEY=your_key financial-agent
   ```

## Usage

### Backend API

Start the FastAPI server:
```bash
python -m app.api.main
```

API endpoints:
- `POST /analyze` - Run financial analysis
- `POST /analyze-async` - Run analysis asynchronously
- `GET /tools` - List available tools
- `GET /health` - Health check

### Frontend

Start the Streamlit app:
```bash
streamlit run frontend/app.py
```

### Example API Call

```python
import requests

response = requests.post("http://localhost:8000/analyze", json={
    "query": "Analyze Tesla stock performance",
    "mode": "react"
})

print(response.json())
```

## Sample Output

```
Analysis Result:
Tesla shows strong growth potential with P/E ratio of 30.2, above industry average. Recent news sentiment is positive with 0.7 compound score. SEC filings indicate consistent revenue growth.

Investment Report:
Executive Summary: Tesla Inc. demonstrates robust financial health...

Company Overview: Tesla designs and manufactures electric vehicles...

Financial Analysis: Market Cap: $500B, EPS: $8.00, P/E: 30.2...

Risk Assessment: Competition in EV market, supply chain constraints...

Competitive Analysis: Outperforms peers in innovation...

Final Insight: Buy recommendation for long-term investors.
```

## Testing

Run tests:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_agent.py tests/test_tools.py -v
```

## Production Considerations

- **Security**: API key management, input validation, rate limiting
- **Scalability**: Async processing, caching layer, horizontal scaling
- **Monitoring**: Comprehensive logging, health checks, metrics
- **Data Quality**: Source validation, fact-checking, data freshness
- **Performance**: Caching, async operations, optimized queries
- **Reliability**: Error handling, fallback mechanisms, graceful degradation

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for LLM functionality
- `SERPAPI_KEY`: Optional for web search functionality
- `BACKEND_URL`: Frontend configuration for backend location

### Logging

Logs are stored in the `logs/` directory with daily rotation. Configure logging levels in `app/services/logging_service.py`.

### Caching

Cache files are stored in `cache/` with 24-hour TTL. Configure cache settings in `app/services/cache_service.py`.

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **API Key Issues**: Verify OpenAI API key is set correctly
3. **Vector DB Errors**: Check Chroma installation and permissions
4. **Memory Issues**: Ensure sufficient RAM for vector operations

### Logs

Check `logs/financial_agent_YYYYMMDD.log` for detailed error information.