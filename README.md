<h1 align="center">Ask-CSV</h1>

<h4 align="center">Query CSV files using natural language powered by GPT-4</h4>

<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python 3.11+">
  </a>
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
  </a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> -
  <a href="#features">Features</a> -
  <a href="#api">API</a> -
  <a href="#examples">Examples</a> -
  <a href="#contributing">Contributing</a>
</p>

---

## Quick Start

### Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Royofficely/ask-csv.git
cd ask-csv

# Configure environment
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and API_TOKEN

# Start with Docker Compose
docker-compose up -d
```

### Manual Installation

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

---

## Features

- **Natural Language Queries** - Ask questions about your CSV data in plain English
- **GPT-4 Powered** - Uses OpenAI's GPT-4 for intelligent data analysis
- **Multi-File Support** - Query across multiple CSV files simultaneously
- **No Size Limits** - Handle large CSV files stored in PostgreSQL
- **REST API** - Simple HTTP endpoints for integration
- **Docker Ready** - One-command deployment with Docker Compose
- **Token Authentication** - Secure API access

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
curl -X POST http://localhost:5000/upload \
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
curl -X POST http://localhost:5000/query \
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

### List Files

```bash
curl http://localhost:5000/files \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

### Health Check

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "database": true,
  "openai_configured": true
}
```

---

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `API_TOKEN` | Yes | - | API authentication token |
| `OPENAI_MODEL` | No | gpt-4o | OpenAI model to use |
| `PORT` | No | 5000 | Server port |

---

## Use Cases

| Use Case | Description |
|----------|-------------|
| **Business Analytics** | Query sales, revenue, and performance data |
| **Data Exploration** | Quickly understand large datasets |
| **Reporting** | Generate insights without SQL knowledge |
| **Integration** | Embed CSV analysis in your applications |

---

## Requirements

- Python 3.11+
- PostgreSQL
- OpenAI API key

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

<p align="center">
  <sub>Built by <a href="https://github.com/Royofficely">Roy Nativ</a></sub>
</p>
