# Dashboard Layout Components

This directory contains the dashboard layout components for KanbanFlow.

## Components

### Sidebar (`sidebar.tsx`)
- Displays navigation links (Boards, Team)
- Team link only visible to admin users
- Collapsible on mobile devices with overlay
- Active route highlighting
- Responsive design (fixed on desktop, slide-in on mobile)

### TopBar (`topbar.tsx`)
- Displays user information (name, email, avatar)
- Dark mode toggle button
- User dropdown menu with logout functionality
- Mobile menu button to toggle sidebar
- Sticky positioning at top of viewport

### Layout (`app/dashboard/layout.tsx`)
- Main dashboard layout wrapper
- Fetches current user data using React Query
- Handles loading and error states
- Redirects to login if user is not authenticated
- Manages sidebar open/close state
- Provides layout structure: Sidebar + (TopBar + Content)

## Features

### Authentication
- Uses `useCurrentUser` hook to fetch user data from `/api/users/me`
- Automatically redirects to login if not authenticated
- Displays loading spinner while fetching user data

### Role-Based UI
- Admin users see Team navigation link
- Employee users only see Boards navigation link
- Role determined from user data fetched via API

### Responsive Design
- Desktop: Sidebar always visible, fixed position
- Mobile: Sidebar hidden by default, slides in when menu button clicked
- Overlay backdrop on mobile when sidebar is open
- Smooth transitions for sidebar animation

### Dark Mode
- Toggle button in TopBar
- Uses next-themes for theme management
- Persists theme preference

### User Menu
- Avatar with user initials fallback
- Displays user name and email
- Logout functionality with API call to `/api/auth/logout`
- Toast notifications for logout success/failure

## Usage

The dashboard layout is automatically applied to all routes under `/dashboard/*` by Next.js App Router.

```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({ children }) {
  // Layout logic
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex flex-col flex-1">
        <TopBar />
        <main>{children}</main>
      </div>
    </div>
  );
}
```

## Dependencies

- `@tanstack/react-query` - Data fetching and caching
- `next-themes` - Dark mode support
- `lucide-react` - Icons
- `sonner` - Toast notifications
- `@radix-ui/react-avatar` - Avatar component
- `@radix-ui/react-dropdown-menu` - Dropdown menu
- shadcn/ui components - UI primitives
