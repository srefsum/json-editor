# Frontend - JSON Editor

Vue.js frontend for JSON Editor application.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
# Create .env file
echo "VITE_API_URL=http://localhost:8000" > .env
```

3. Start development server:
```bash
npm run dev
```

The application will be available at http://localhost:5173

## Build for Production

```bash
npm run build
```

## Project Structure

```
src/
├── assets/          # Static assets and styles
├── components/      # Reusable Vue components
├── views/          # Page components
├── stores/         # Pinia stores for state management
├── services/       # API service layer
├── router/         # Vue Router configuration
├── App.vue         # Root component
└── main.js         # Application entry point
```

## Features

- List and manage JSON documents
- List and manage JSON schemas
- Create and edit JSON with syntax highlighting
- Validate JSON documents against schemas
- Clean, modern UI with Tailwind CSS
