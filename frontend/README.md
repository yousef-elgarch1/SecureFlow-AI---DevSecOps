# AI Security Policy Generator - Frontend

Professional React frontend with real-time WebSocket updates for the AI Security Policy Generator.

## Features

- **Drag & Drop File Upload**: Upload SAST, SCA, and DAST reports
- **Real-Time Updates**: WebSocket connection shows live progress of AI processing
- **Professional UI/UX**: Modern design with Tailwind CSS
- **Interactive Charts**: Visualize vulnerability distribution and statistics
- **Policy Viewer**: Expandable policy cards with compliance mappings
- **Multi-Format Export**: Download policies in TXT and HTML formats
- **Evaluation Metrics**: Display BLEU-4 and ROUGE-L scores

## Tech Stack

- **React 18**: Modern React with hooks
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Interactive charts and visualizations
- **Lucide React**: Beautiful icon library
- **Axios**: HTTP client for API calls
- **WebSocket**: Real-time bidirectional communication

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend API running on http://localhost:8000

## Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

## Running the Frontend

1. Start the development server:
```bash
npm run dev
```

2. Open your browser to:
```
http://localhost:3000
```

The frontend will automatically proxy API requests to the backend at `http://localhost:8000`.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── UploadMode.jsx          # File upload interface with drag & drop
│   │   ├── RealTimeDashboard.jsx   # Live progress dashboard
│   │   ├── ResultsView.jsx         # Policy results and charts
│   │   └── StatsCard.jsx           # Reusable statistics card
│   ├── utils/
│   │   └── api.js                  # API client with WebSocket support
│   ├── App.jsx                     # Main application component
│   ├── main.jsx                    # React entry point
│   └── index.css                   # Global styles with Tailwind
├── public/
├── index.html
├── vite.config.js                  # Vite configuration
├── tailwind.config.js              # Tailwind CSS configuration
├── postcss.config.js               # PostCSS configuration
└── package.json
```

## Components Overview

### UploadMode
- Drag & drop file upload for SAST/SCA/DAST reports
- File validation and preview
- Support for .json and .xml formats
- Visual feedback for file selection

### RealTimeDashboard
- Live progress updates via WebSocket
- 4 phases displayed:
  1. **Parsing**: Extracting vulnerabilities from reports
  2. **RAG Retrieval**: Fetching compliance context
  3. **LLM Generation**: AI policy generation with per-vulnerability progress
  4. **Saving**: Saving results to disk
- Real-time vulnerability counts and LLM model display

### ResultsView
- Statistics cards showing totals and severity distribution
- Interactive bar charts and pie charts
- Expandable policy cards with:
  - Vulnerability details
  - Generated policy text
  - Compliance mappings (NIST CSF, ISO 27001)
  - BLEU-4 and ROUGE-L scores
- Download buttons for TXT and HTML formats

### StatsCard
- Reusable statistics display component
- Color-coded by severity/type
- Trend indicators

## API Integration

The frontend communicates with the FastAPI backend through:

1. **REST API**:
   - `POST /api/generate-policies`: Upload files and generate policies
   - `GET /api/health`: Check backend status
   - `GET /api/download/{filename}`: Download generated files

2. **WebSocket** (`ws://localhost:8000/ws`):
   - Real-time progress updates during policy generation
   - Phase status updates
   - Live vulnerability processing information

## Building for Production

```bash
npm run build
```

This creates an optimized production build in the `dist/` directory.

To preview the production build:
```bash
npm run preview
```

## Configuration

### Vite Configuration (vite.config.js)
- Development server on port 3000
- Proxy for API requests to backend
- WebSocket proxy for real-time updates

### Tailwind Configuration (tailwind.config.js)
- Custom color palette
- Extended animations
- Responsive breakpoints

## Troubleshooting

### Backend Connection Error
If you see "Backend Offline" status:
1. Ensure the FastAPI backend is running: `uvicorn backend.api.main:app --reload`
2. Check backend is accessible at http://localhost:8000
3. Verify CORS settings in backend allow localhost:3000

### WebSocket Connection Issues
1. Check browser console for WebSocket errors
2. Ensure backend WebSocket endpoint is running
3. Verify firewall isn't blocking WebSocket connections

### File Upload Errors
1. Check file format (must be .json for SAST/SCA, .json or .xml for DAST)
2. Ensure at least one file is uploaded
3. Check browser console for detailed error messages

## Development Tips

1. **Hot Module Replacement**: Vite provides instant HMR for fast development
2. **Component Development**: Each component is isolated and reusable
3. **Real Data Only**: No mock data - all information comes from actual backend processing
4. **Responsive Design**: All components work on mobile, tablet, and desktop

## Environment Variables

Create a `.env` file in the frontend directory if needed:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

## Next Steps

1. Start the backend API (see main project README)
2. Run the frontend development server
3. Upload security reports
4. Watch real-time AI policy generation
5. Download generated policies
