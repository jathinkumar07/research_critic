# AI Research Critic - Frontend

A modern React TypeScript frontend for the AI Research Critic application, providing document analysis capabilities including plagiarism detection, citation validation, and fact-checking.

## Features

- **Drag & Drop Upload**: Intuitive PDF file upload with validation
- **Real-time Analysis**: Connect to Flask backend for document processing
- **Responsive Design**: Mobile-first design using TailwindCSS
- **Modern UI**: Clean, professional interface with loading states
- **Results Visualization**: Comprehensive display of analysis results
- **Download Results**: Export analysis results as JSON

## Tech Stack

- **React 18** with TypeScript for type safety
- **TailwindCSS** for responsive styling
- **React Router** for client-side routing
- **Axios** for API communication
- **Modern ES6+** features and hooks

## Prerequisites

- Node.js 16+ and npm
- Backend Flask server running on port 5000

## Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
# Copy .env file is already created with:
# REACT_APP_API_URL=http://localhost:5000
```

## Development

Start the development server:
```bash
npm start
```

The app will be available at `http://localhost:3000`

## Production Build

Create production build:
```bash
npm run build
```

## Project Structure

```
src/
├── components/
│   └── Navbar.tsx          # Navigation component
├── pages/
│   ├── Home.tsx            # Upload and analysis page
│   ├── Results.tsx         # Analysis results display
│   └── About.tsx           # App information page
├── services/
│   └── api.ts              # API service layer
├── types/
│   └── index.ts            # TypeScript interfaces
├── App.tsx                 # Main app component
└── index.tsx               # App entry point
```

## API Integration

The frontend connects to the Flask backend via the `/analyze` endpoint:

- **Endpoint**: `POST /analyze`
- **Content-Type**: `multipart/form-data`
- **File**: PDF document (max 10MB)
- **Response**: Analysis results including summary, plagiarism score, citations, and fact-check results

## Features Overview

### Home Page
- Drag-and-drop PDF upload
- File validation (PDF only, ≤10MB)
- Loading spinner during analysis
- Error handling and user feedback

### Results Page
- Statistics dashboard
- AI-generated summary
- Plagiarism score with risk indicators
- Citation analysis with validation status
- Fact-check results
- Download functionality

### About Page
- Feature descriptions
- Technology stack information
- Usage instructions

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:5000)

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
