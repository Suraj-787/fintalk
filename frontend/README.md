# FinTalk - AI-Powered Loan Advisor

A modern, multilingual AI-powered loan advisory application built with Next.js. Get personalized loan guidance using voice and text chat with an intelligent AI assistant.

## Features

- **Chat Interface**: Ask questions about loans, interest rates, EMI calculations, and financial guidance
- **Voice Input & Output**: Record voice questions and listen to AI responses in your preferred language
- **Multilingual Support**: Get advice in multiple languages powered by Sarvam AI
- **Credit Score Integration**: Personalized recommendations based on your credit score
- **Dark Fintech UI**: Premium dark theme optimized for financial applications
- **Privacy-First**: All API keys stored locally in your browser, never sent to servers
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices

## Tech Stack

- **Frontend**: Next.js 16, React 19, Tailwind CSS v4, TypeScript
- **State Management**: Zustand
- **UI Components**: shadcn/ui, Radix UI
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Notifications**: Sonner
- **Audio**: Web Audio API (MediaRecorder)
- **Theme**: next-themes with forced dark mode

## Prerequisites

- Node.js 18+ and pnpm
- FastAPI backend running (see Backend Setup below)
- Google API key for language processing
- Sarvam API key for voice features

## Installation

1. Clone and install dependencies:
```bash
git clone <repository-url>
cd fintalk
pnpm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update `.env.local` with your backend URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

## Usage

### Home Page
- Landing page with feature overview and CTAs
- Quick access to chat and settings

### Chat Page
- **Text Chat**: Type your questions about loans and financial topics
- **Voice Recording**: Click the microphone button to record voice questions
  - Recording indicator shows elapsed time
  - Audio is automatically transcribed using Sarvam AI
- **Audio Responses**: Click the play button to listen to AI responses
- **Suggested Questions**: Use pre-written questions for quick guidance
- **Chat History**: All messages persist during the session

### Settings Page
- **API Keys Configuration**:
  - Add Google API key for language processing
  - Add Sarvam API key for voice features
  - Keys are stored locally in browser localStorage
  - Only used when sending requests to your backend
  
- **Profile Information**:
  - Full Name and Email
  - Desired Loan Amount
  - Annual Income
  - Employment Status
  - Credit Score with color-coded rating:
    - 300-579: Poor (Red)
    - 580-669: Fair (Orange)
    - 670-739: Good (Yellow)
    - 740-900: Excellent (Green)

## Backend Integration

The frontend expects a FastAPI backend with the following endpoints:

### POST /api/chat
Sends a chat message and returns a response.

**Request Body:**
```json
{
  "message": "What loan options do I qualify for?",
  "googleApiKey": "your-google-key",
  "sarvamApiKey": "your-sarvam-key",
  "language": "en",
  "creditScore": 750,
  "chatHistory": [
    {"role": "user", "content": "previous message"},
    {"role": "assistant", "content": "previous response"}
  ]
}
```

**Response:**
```json
{
  "response": "Based on your credit score of 750...",
  "audioUrl": "https://..."  // Optional TTS audio URL
}
```

### POST /api/transcribe
Transcribes audio files to text.

**Request:** Multipart form-data
- `audio`: Audio file (WAV/MP3)
- `sarvamApiKey`: Sarvam API key
- `language`: Language code (e.g., "en")

**Response:**
```json
{
  "text": "What loan options do I qualify for?"
}
```

### POST /api/tts
Converts text to speech audio.

**Request Body:**
```json
{
  "text": "Based on your credit score...",
  "sarvamApiKey": "your-sarvam-key",
  "language": "en"
}
```

**Response:**
```json
{
  "audioUrl": "https://..."
}
```

## Project Structure

```
├── app/
│   ├── layout.tsx              # Root layout with providers
│   ├── page.tsx                # Home page
│   ├── chat/
│   │   └── page.tsx            # Chat page
│   ├── settings/
│   │   └── page.tsx            # Settings page
│   └── globals.css             # Global styles
├── components/
│   ├── Navigation.tsx          # Navigation bar
│   ├── chat/
│   │   ├── ChatMessages.tsx    # Message display
│   │   └── ChatInput.tsx       # Input and recording
│   ├── settings/
│   │   ├── ApiKeysForm.tsx    # API keys configuration
│   │   └── FinCardForm.tsx    # Profile form
│   └── ui/                     # shadcn/ui components
├── lib/
│   ├── store.ts               # Zustand stores
│   ├── api.ts                 # Axios API client
│   └── utils.ts               # Utility functions
└── public/                     # Static assets
```

## State Management

### Settings Store (`useSettingsStore`)
- Persists to localStorage
- Stores: Google API key, Sarvam API key, FinCard profile
- Methods: setters for each field, load/save to localStorage

### Chat Store (`useChatStore`)
- In-memory only (not persisted)
- Stores: messages array, loading state
- Methods: add message, clear messages, set loading

## Styling

The app uses a premium dark fintech theme with:
- **Colors**: Dark backgrounds with accent highlights
- **Typography**: Clean, readable fonts (Geist family)
- **Components**: Rounded corners, subtle shadows
- **Responsive**: Mobile-first design with tailwind breakpoints

All styling is configured via CSS variables in `globals.css` and `tailwind.config.ts`.

## Environment Variables

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

API keys are NOT stored in environment variables. Users configure them in the Settings page, and they're stored locally in browser localStorage.

## Deployment

### Vercel Deployment (Recommended)
1. Push code to GitHub
2. Import project in Vercel
3. Add environment variable: `NEXT_PUBLIC_API_URL`
4. Deploy

### Docker Deployment
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY . .
RUN pnpm install
RUN pnpm build
EXPOSE 3000
CMD ["pnpm", "start"]
```

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## API Key Safety

- API keys are entered in the Settings page
- Keys are stored in browser's localStorage (encrypted via HTTPS)
- Keys are sent with each request to your backend
- Keys are never stored on servers or transmitted to third parties
- Clear your browser cache to delete stored keys

## Troubleshooting

### Microphone not working
- Check browser permissions (Settings > Privacy > Microphone)
- Ensure HTTPS is used in production
- Try different browser if issue persists

### Audio playback not working
- Check browser autoplay policy settings
- Ensure audio URLs are accessible
- Try clearing browser cache

### Chat not responding
- Verify API keys are correctly set in Settings
- Check backend server is running at configured URL
- Review browser console for error messages
- Check network tab in DevTools for failed requests

## License

MIT License - feel free to use and modify for your needs.

## Support

For issues or feature requests, please create an issue in the repository.
