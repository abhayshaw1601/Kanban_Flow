'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { LayoutDashboard, Users, Settings, X, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  isAdmin: boolean;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isAdmin, isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();

  const navItems = [
    {
      href: '/dashboard/boards',
      label: 'Boards',
      icon: LayoutDashboard,
      adminOnly: false,
    },
    {
      href: '/dashboard/team',
      label: 'Team',
      icon: Users,
      adminOnly: true,
    },
    {
      href: '/dashboard/audit',
      label: 'Audit',
      icon: Search,
      adminOnly: true,
    },
    {
      href: '/dashboard/settings',
      label: 'Settings',
      icon: Settings,
      adminOnly: false,
    },
  ];

  const filteredNavItems = navItems.filter(
    (item) => !item.adminOnly || isAdmin
  );

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-full w-64 bg-background border-r transition-transform duration-300 lg:translate-x-0 lg:static lg:z-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo and close button */}
          <div className="flex items-center justify-between p-6 border-b">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-primary-foreground font-bold text-lg">K</span>
              </div>
              <span className="font-bold text-xl">KanbanFlow</span>
            </Link>
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={onClose}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-2">
            {filteredNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href || pathname.startsWith(item.href + '/');

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    'flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{item.label}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </aside>
    </>
  );
}
