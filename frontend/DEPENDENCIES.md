# Frontend Dependencies

This document lists all the frontend dependencies installed for the KanbanFlow application and their purposes.

## Core Framework

### Next.js 14.1.0
- **Purpose**: React framework with App Router for server-side rendering and routing
- **Compatibility**: Fully compatible with all other dependencies
- **Configuration**: `next.config.js`, `tsconfig.json`

### React 18.2.0
- **Purpose**: Core UI library
- **Compatibility**: Required by Next.js 14

### TypeScript 5.3.3
- **Purpose**: Type safety and better developer experience
- **Configuration**: `tsconfig.json`

## Styling

### Tailwind CSS 3.4.1
- **Purpose**: Utility-first CSS framework
- **Configuration**: `tailwind.config.ts`, `postcss.config.js`
- **Plugins**: autoprefixer

### shadcn/ui Components
- **Purpose**: Pre-built, accessible UI components based on Radix UI
- **Configuration**: `components.json`
- **Installed Components**:
  - Button
  - Dialog
  - Input
  - Select
  - Label
  - Textarea
  - Card
  - Dropdown Menu
  - Avatar
  - Badge
  - Calendar
  - Popover

### Radix UI Primitives
- **Purpose**: Unstyled, accessible component primitives (installed by shadcn/ui)
- **Packages**:
  - @radix-ui/react-avatar
  - @radix-ui/react-dialog
  - @radix-ui/react-dropdown-menu
  - @radix-ui/react-label
  - @radix-ui/react-popover
  - @radix-ui/react-select
  - @radix-ui/react-slot

### next-themes 0.2.1
- **Purpose**: Dark mode support
- **Configuration**: Configured in `components/theme-provider.tsx`

### Utility Libraries
- **class-variance-authority**: Type-safe component variants
- **clsx**: Conditional className utility
- **tailwind-merge**: Merge Tailwind classes without conflicts
- **lucide-react**: Icon library

## Data Fetching & State Management

### @tanstack/react-query 5.17.19
- **Purpose**: Data fetching, caching, and synchronization
- **Configuration**: `components/providers/query-provider.tsx`
- **Features**:
  - Automatic caching with 1-minute stale time
  - Disabled refetch on window focus
  - Optimistic updates support

### axios 1.6.5
- **Purpose**: HTTP client for API requests
- **Configuration**: Will be configured in `lib/api.ts` (Task 15.3)
- **Features**:
  - Cookie support with `withCredentials: true`
  - Request/response interceptors
  - TypeScript support

## Feature-Specific Libraries

### @hello-pangea/dnd 16.5.0
- **Purpose**: Drag-and-drop functionality for Kanban board
- **Use Case**: Moving tasks between columns
- **Note**: Maintained fork of react-beautiful-dnd

### @uiw/react-md-editor 4.0.4
- **Purpose**: Markdown editor for task descriptions
- **Features**:
  - Live preview
  - Syntax highlighting
  - Toolbar with formatting options

### sonner 1.3.1
- **Purpose**: Toast notifications
- **Configuration**: Toaster component added to root layout
- **Features**:
  - Rich colors
  - Position: top-right
  - Success/error variants

### date-fns 4.1.0
- **Purpose**: Date manipulation and formatting
- **Use Case**: Due date handling and display

### react-day-picker 9.14.0
- **Purpose**: Date picker component (used by Calendar component)
- **Use Case**: Selecting task due dates

## Validation

### zod 3.22.4
- **Purpose**: Schema validation for forms and API responses
- **Use Case**: Form validation, type-safe API contracts

## Development Dependencies

### ESLint 8.56.0
- **Purpose**: Code linting
- **Configuration**: `.eslintrc.json`
- **Plugins**: eslint-config-next

### PostCSS 8.4.33
- **Purpose**: CSS processing
- **Plugins**: autoprefixer, tailwindcss

### Type Definitions
- @types/node
- @types/react
- @types/react-dom

## Compatibility Notes

All dependencies are compatible with:
- Next.js 14 App Router
- React 18
- TypeScript 5
- Node.js 20+

## Provider Setup

The following providers are configured in the root layout (`app/layout.tsx`):

1. **QueryProvider**: Wraps the app for React Query functionality
2. **ThemeProvider**: Enables dark mode support
3. **Toaster**: Provides toast notification functionality

## Next Steps

- Task 15.3: Create API client configuration (`lib/api.ts`)
- Configure axios with baseURL and interceptors
- Set up React Query hooks for data fetching
