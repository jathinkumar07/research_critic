# Research Paper Analysis Backend - Local Setup

This backend works **100% locally without any API keys**, using mock data for external services when keys are not available.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Server**
   ```bash
   python3 app.py
   ```
   The server will start on `http://localhost:5000`

3. **Test the API**
   ```bash
   # Test with curl
   curl -X POST -F "file=@uploads/sample.pdf" http://localhost:5000/analyze

   # Or run the test script
   python3 simple_test.py
   ```

## 📋 API Endpoint

### POST /analyze

Upload and analyze a PDF research paper.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `file` (PDF file)

**Response:**
```json
{
  "summary": "Generated summary of the paper...",
  "plagiarism": 12.5,
  "citations": [
    {"reference": "Smith et al., 2021", "valid": true},
    {"reference": "Johnson, 2019", "valid": false}
  ],
  "fact_check": {
    "facts": [
      {"claim": "This research uses dataset X", "status": "Verified"},
      {"claim": "The model achieved 99% accuracy", "status": "Unverified"}
    ]
  },
  "stats": {
    "word_count": 2500,
    "plagiarism_percent": 12.5,
    "citations_count": 2
  }
}
```

## 🔧 Configuration

The backend automatically detects missing API keys and falls back to mock data:

### Environment Variables (Optional)
```bash
# Fact-checking (Google Fact Check API)
GOOGLE_API_KEY=your_google_api_key
FACTCHECK_USE=api_key  # or "disabled" or "service_account"

# Citation validation
CROSSREF_API_KEY=your_crossref_key
SEMANTIC_SCHOLAR_KEY=your_semantic_scholar_key
```

### Mock Data Behavior

When API keys are **not set**:
- ✅ **Fact-checking**: Returns mock verification results
- ✅ **Citation validation**: Returns mock citation status
- ✅ **PDF extraction**: Uses PyMuPDF (no API needed)
- ✅ **Summarization**: Uses local text processing
- ✅ **Plagiarism detection**: Uses mock similarity scores

When API keys **are set**:
- 🌐 Uses real external APIs for fact-checking and citation validation
- 📊 Provides more accurate results

## 🧪 Testing

### 1. Service Tests
```bash
python3 simple_test.py
```
Tests all services individually with mock data.

### 2. Full Endpoint Test
```bash
python3 test_local.py
```
Tests the complete `/analyze` endpoint (requires `requests` library).

### 3. Curl Test
```bash
./test_curl.sh
```
Simple curl-based test of the endpoint.

## 📁 File Structure

```
backend/
├── app.py                     # Flask application
├── config.py                  # Configuration settings
├── src/
│   ├── routes/
│   │   └── simple_analyze.py  # /analyze endpoint
│   └── services/
│       ├── pdf_service.py     # PDF text extraction
│       ├── factcheck_service.py    # Fact-checking (real)
│       ├── factcheck_service_mock.py # Fact-checking (mock)
│       ├── citations_service.py     # Citation validation (real)
│       ├── citations_service_mock.py # Citation validation (mock)
│       ├── summarizer_service.py    # Text summarization
│       ├── plagiarism_service.py    # Plagiarism detection
│       └── ...
├── uploads/
│   └── sample.pdf            # Sample PDF for testing
└── test_local.py            # Comprehensive test script
```

## ✨ Features

- 🔄 **Automatic fallback**: Uses mock data when API keys are missing
- 🛡️ **Error handling**: Never crashes, always returns valid JSON
- 📊 **Complete analysis**: Summary, plagiarism, citations, fact-checking
- 🚀 **No setup required**: Works immediately without configuration
- 🔍 **Comprehensive logging**: Detailed error messages and progress tracking

## 🎯 Production Notes

For production use with real APIs:
1. Set the appropriate environment variables
2. The backend will automatically use real APIs when keys are available
3. Mock services provide realistic data structure for development/testing

## 🤝 Frontend Integration

The response format exactly matches what the frontend expects:
- `summary`: String summary of the paper
- `plagiarism`: Number (percentage)
- `citations`: Array of citation objects with `reference` and `valid` fields
- `fact_check.facts`: Array of fact objects with `claim` and `status` fields
- `stats`: Object with word count, plagiarism percentage, and citation count