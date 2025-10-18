# NetWiz Frontend

PCB Netlist Visualizer + Validator Frontend Application

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- npm or yarn
- Backend API running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Generate TypeScript types from OpenAPI schema
npm run generate-api-types

# Start development server
npm run dev
```

The application will be available at `http://localhost:3000`

## 📁 Project Structure

```
src/
├── components/           # Reusable UI components
│   ├── common/          # Generic components (Button, Modal, etc.)
│   ├── layout/          # Layout components (Header, Sidebar, etc.)
│   └── netlist/         # Netlist-specific components
├── pages/               # Page components
├── hooks/               # Custom React hooks
├── services/            # API client and services
├── types/               # TypeScript type definitions
├── utils/               # Utility functions
└── styles/              # Global styles and themes
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run type-check` - Run TypeScript type checking
- `npm run generate-api-types` - Generate TypeScript types from OpenAPI schema
- `npm run generate-api-types:watch` - Watch for OpenAPI schema changes

## 🔧 Key Features

### Type-Safe API Client
- Generated TypeScript types from OpenAPI schema
- Automatic type checking for API requests/responses
- Error handling and response parsing

### Real-Time Validation
- Live validation as you type in the JSON editor
- Error and warning markers with line/column positions
- Auto-fill suggestions for missing net types

### Interactive Visualization
- D3.js-based schematic visualization
- Zoom, pan, and drag functionality
- Component and net highlighting

### Modern UI/UX
- Split-pane layout for optimal workflow
- Monaco Editor with syntax highlighting
- Responsive design with Tailwind CSS

## 🎨 UI Components

### Core Components
- **JsonEditor**: Monaco Editor-based JSON editor with validation markers
- **GraphVisualization**: D3.js-based interactive schematic visualization
- **ValidationPanel**: Displays validation results, errors, warnings, and suggestions
- **FileUpload**: Drag-and-drop file upload with validation

### Layout Components
- **NetlistPage**: Main application page with split-pane layout
- **Header**: Application header with navigation and actions

## 🔌 API Integration

The frontend uses a type-safe API client that automatically generates TypeScript interfaces from the backend's OpenAPI schema:

```typescript
import { apiClient } from '@/services/api'

// Type-safe API calls
const response = await apiClient.validateNetlist({ netlist })
// response is fully typed based on OpenAPI schema
```

## 🎯 Development Workflow

1. **Start Backend**: Ensure the NetWiz backend is running on port 8000
2. **Generate Types**: Run `npm run generate-api-types` to sync with backend schema
3. **Start Frontend**: Run `npm run dev` to start the development server
4. **Hot Reload**: Changes to the frontend will automatically reload

## 📦 Dependencies

### Core Dependencies
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool and dev server
- **Tailwind CSS**: Utility-first CSS framework

### UI Libraries
- **Monaco Editor**: Code editor with syntax highlighting
- **D3.js**: Data visualization library
- **React Split Pane**: Resizable split-pane layout
- **Lucide React**: Icon library

### API & State Management
- **Axios**: HTTP client
- **React Query**: Data fetching and caching
- **React Router**: Client-side routing

## 🔄 Type Generation

The frontend automatically generates TypeScript types from the backend's OpenAPI schema:

```bash
# Generate types once
npm run generate-api-types

# Watch for schema changes during development
npm run generate-api-types:watch
```

This ensures the frontend stays in sync with backend API changes and provides full type safety.

## 🚀 Deployment

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

The built application will be in the `dist/` directory, ready for deployment to any static hosting service.

## 🤝 Contributing

1. Follow the existing code structure and patterns
2. Use TypeScript for all new code
3. Run `npm run lint` before committing
4. Update types when backend API changes
5. Test with real netlist data

## 📝 Notes

- The application is designed to work with the NetWiz backend API
- All API calls are type-safe thanks to OpenAPI code generation
- The JSON editor provides real-time validation with error markers
- The graph visualization supports interactive exploration of netlist schematics
