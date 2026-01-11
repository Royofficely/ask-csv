<h1 align="center">Ask-CSV</h1>

<h4 align="center">Query CSV files using natural language powered by GPT-4. No SQL required.</h4>

<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+">
  </a>
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker">
  </a>
  <a href="https://github.com/Royofficely/ask-csv/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Royofficely/ask-csv" alt="License">
  </a>
  <a href="https://github.com/Royofficely/ask-csv/stargazers">
    <img src="https://img.shields.io/github/stars/Royofficely/ask-csv?style=social" alt="Stars">
  </a>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-why-ask-csv">Why Ask-CSV</a> •
  <a href="#-features">Features</a> •
  <a href="#-api">API</a> •
  <a href="#-examples">Examples</a> •
  <a href="#-contributing">Contributing</a>
</p>

---

## Quick Start

```bash
# Clone and configure
git clone https://github.com/Royofficely/ask-csv.git
cd ask-csv && cp .env.example .env

# Add your keys to .env
# OPENAI_API_KEY=sk-...
# API_TOKEN=your-secret-token

# Run with Docker
docker-compose up -d
```

**That's it.** API ready at `http://localhost:5001`

---

## Why Ask-CSV?

| Problem | How We Solve It |
|---------|-----------------|
| **Need SQL knowledge** | Natural language queries - just ask in English |
| **CSV size limits** | DuckDB backend handles files of any size |
| **Complex setup** | One command Docker deployment, no database server needed |
| **Security concerns** | Token-based auth, no hardcoded secrets |
| **Multi-file analysis** | Query across multiple CSVs simultaneously |
| **Integration hassle** | Simple REST API for any application |

---

## Features

```
Natural Language       Ask questions in plain English, get instant answers
GPT-4 Powered          OpenAI's latest models for intelligent analysis
Multi-File Support     Query across multiple CSV files at once
No Size Limits         DuckDB handles large files efficiently
REST API               Simple HTTP endpoints for easy integration
Docker Ready           One-command deployment with Docker Compose
Token Auth             Secure API access with Bearer tokens
Zero Config DB         DuckDB embedded - no PostgreSQL needed
```

---

## API

### Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/health` | GET | No | Health check |
| `/upload` | POST | Yes | Upload CSV file |
| `/query` | POST | Yes | Query CSV files |
| `/files` | GET | Yes | List uploaded files |
| `/files/<id>` | DELETE | Yes | Delete a file |

### Authentication

Include the API token in all protected requests:

```
Authorization: Bearer YOUR_API_TOKEN
```

---

## Examples

### Upload a CSV File

```bash
curl -X POST http://localhost:5001/upload \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -F "file=@sales_data.csv"
```

Response:
```json
{
  "message": "File uploaded successfully",
  "file_id": "1",
  "filename": "sales_data.csv"
}
```

### Query Your Data

```bash
curl -X POST http://localhost:5001/query \
  -H "Authorization: Bearer YOUR_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is the total revenue by region?",
    "file_ids": ["1"]
  }'
```

Response:
```json
{
  "status": "success",
  "data": {
    "query": "What is the total revenue by region?",
    "result": "The total revenue by region is: North: $45,000, South: $38,000, East: $52,000, West: $41,000"
  }
}
```

### Example Queries

| Query Type | Example |
|------------|---------|
| **Aggregation** | "What is the average salary by department?" |
| **Filtering** | "Show me all customers from California" |
| **Comparison** | "Which product has the highest sales?" |
| **Trend** | "How did revenue change month over month?" |
| **Cross-file** | "Compare Q1 and Q2 performance" |

<details>
<summary><strong>More API Examples</strong></summary>

### List Files

```bash
curl http://localhost:5001/files \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

Response:
```json
{
  "files": [
    {"id": "1", "filename": "sales_data.csv", "created_at": "2024-01-15T10:30:00"},
    {"id": "2", "filename": "customers.csv", "created_at": "2024-01-15T10:35:00"}
  ]
}
```

### Delete File

```bash
curl -X DELETE http://localhost:5001/files/1 \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Health Check

```bash
curl http://localhost:5001/api/health
```

Response:
```json
{
  "status": "healthy",
  "database": true,
  "openai_configured": true
}
```

</details>

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `API_TOKEN` | Yes | - | API authentication token |
| `OPENAI_MODEL` | No | gpt-4o | OpenAI model to use |
| `PORT` | No | 5000 | Server port |
| `DATA_DIR` | No | /data | Storage directory |

<details>
<summary><strong>Manual Installation (without Docker)</strong></summary>

```bash
# Clone and setup
git clone https://github.com/Royofficely/ask-csv.git
cd ask-csv

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
python app.py
```

</details>

---

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Business Analytics** | Query sales, revenue, and performance data |
| **Data Exploration** | Quickly understand large datasets without SQL |
| **Reporting** | Generate insights for non-technical stakeholders |
| **Integration** | Embed CSV analysis in your applications |
| **Chatbots** | Add data querying to conversational interfaces |
| **Internal Tools** | Build dashboards without backend development |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 5000 in use | Change port in docker-compose.yml or use `-p 5002:5000` |
| OpenAI rate limit | Use GPT-3.5-turbo in OPENAI_MODEL for higher limits |
| Large file timeout | Increase timeout in client, queries may take 30s+ |
| Auth errors | Ensure Bearer token matches API_TOKEN exactly |
| Container crash | Check logs with `docker-compose logs -f` |

---

## Requirements

- Python 3.11+
- OpenAI API key
- Docker (recommended) or pip

```bash
pip install flask langchain langchain-experimental langchain-openai duckdb pandas
```

---

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## AI Prompt

Copy this to quickly set up CSV querying with AI assistants:

```
I need to query CSV files with natural language. Use Ask-CSV from github.com/Royofficely/ask-csv

Setup:
1. Clone repo, copy .env.example to .env
2. Add OPENAI_API_KEY and API_TOKEN
3. docker-compose up -d

Then:
- Upload: curl -X POST localhost:5001/upload -H "Authorization: Bearer TOKEN" -F "file=@data.csv"
- Query: curl -X POST localhost:5001/query -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"query": "YOUR QUESTION", "file_ids": ["1"]}'
```

---

<p align="center">
  <sub>Built by <a href="https://github.com/Royofficely">Roy Nativ</a> at <a href="https://officely.ai">Officely AI</a></sub>
</p>

<p align="center">
  <a href="https://github.com/Royofficely/ask-csv/issues">Report Bug</a> •
  <a href="https://github.com/Royofficely/ask-csv/issues">Request Feature</a>
</p>
