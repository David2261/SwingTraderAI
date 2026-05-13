# SwingTrader AI Frontend

A modern React + TypeScript frontend for swing trading platform built with Vite, Zustand, TanStack Query, and TailwindCSS.

## Tech Stack

- **React 19** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Zustand** - State management
- **TanStack React Query** - Server state management
- **Axios** - HTTP client
- **Zod** - Schema validation
- **TailwindCSS** - Styling
- **React Router** - Routing
- **React Hook Form** - Form handling
- **Sonner** - Toast notifications
- **Lucide React** - Icons
- **Next Themes** - Theme management
- **Date-fns** - Date utilities
- **Lightweight Charts** - Trading charts

## Features

- 🔐 Authentication (login/register/logout)
- 📊 Dashboard with portfolio overview
- 📈 Real-time trading charts
- 📋 Watchlist management
- 💼 Portfolio tracking
- 🎯 Technical indicators
- 🌙 Dark/Light theme
- 📱 Responsive design
- 🔄 Refresh token flow
- 🛡️ Route guards
- 🎨 Modern trading terminal UI

## Getting Started

1. **Install dependencies:**
   ```bash
   yarn install
   ```

2. **Environment setup:**
   ```bash
   cp .env.example .env
   ```

3. **Start development server:**
   ```bash
   yarn dev
   ```

4. **Build for production:**
   ```bash
   yarn build
   ```

## Project Structure

```
src/
├── app/                    # Application configuration
│   ├── providers.tsx       # React providers
│   ├── router.tsx          # Route configuration
│   ├── query-client.ts     # React Query setup
│   └── layouts/            # Layout components
├── features/               # Feature-based modules
│   ├── auth/              # Authentication feature
│   ├── tickers/           # Ticker management
│   ├── watchlist/         # Watchlist feature
│   ├── portfolio/         # Portfolio management
│   └── indicators/        # Technical indicators
├── entities/              # Business entities
├── shared/                # Shared code
│   ├── api/              # API layer
│   ├── ui/               # UI components
│   ├── lib/              # Utilities
│   └── hooks/            # Shared hooks
├── widgets/              # Composite UI components
├── pages/                # Page components
└── main.tsx              # Application entry point
```

## API Integration

The frontend integrates with a REST API. Configure the API base URL in `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Development

### Available Scripts

- `yarn dev` - Start development server
- `yarn build` - Build for production
- `yarn preview` - Preview production build
- `yarn lint` - Run ESLint

### Code Quality

- TypeScript for type safety
- ESLint for code linting
- Prettier for code formatting (via ESLint)
- Husky for git hooks (if configured)

## Architecture Principles

- **Feature-Sliced Design (FSD)** - Feature-based architecture
- **Composition over Inheritance** - Component composition
- **Separation of Concerns** - Clear boundaries between layers
- **Type Safety** - Full TypeScript coverage
- **Performance** - Optimized rendering and data fetching

## Contributing

1. Follow the established project structure
2. Use TypeScript for all new code
3. Write meaningful commit messages
4. Test your changes thoroughly
5. Update documentation as needed
