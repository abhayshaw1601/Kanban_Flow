'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { LayoutDashboard, Users, Settings, X, Search, Zap, Brain, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';

interface SidebarProps {
  isAdmin: boolean;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isAdmin, isOpen, onClose }: SidebarProps) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);

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
      aiPowered: true,
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
      {/* Mobile overlay with glassmorphism */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar with premium glassmorphism */}
      <aside
        className={cn(
          'fixed top-0 left-0 z-50 h-full sidebar-glass transition-all duration-300 ease-in-out lg:translate-x-0 lg:static lg:z-0',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          isCollapsed ? 'w-20' : 'w-64'
        )}
      >
        <div className="flex flex-col h-full">
          {/* Logo and controls */}
          <div className="flex items-center justify-between p-6 border-b border-white/10">
            <Link 
              href="/dashboard" 
              className={cn(
                "flex items-center space-x-3 transition-all duration-300",
                isCollapsed && "justify-center"
              )}
            >
              <div className="relative w-10 h-10 bg-gradient-to-br from-ai-violet-600 to-electric-blue-600 rounded-xl flex items-center justify-center shadow-lg">
                <Brain className="h-6 w-6 text-white" />
                <div className="absolute inset-0 bg-gradient-to-br from-ai-violet-600 to-electric-blue-600 rounded-xl opacity-0 hover:opacity-20 transition-opacity duration-300" />
              </div>
              {!isCollapsed && (
                <div className="flex flex-col">
                  <span className="font-bold text-xl tracking-tight bg-gradient-to-r from-white to-white/80 bg-clip-text text-transparent">
                    KanbanFlow
                  </span>
                  <span className="text-xs text-muted-foreground font-medium">
                    AI-Powered PM
                  </span>
                </div>
              )}
            </Link>
            
            <div className="flex items-center space-x-2">
              {/* Collapse button for desktop */}
              <Button
                variant="ghost"
                size="icon"
                className="hidden lg:flex h-8 w-8 hover:bg-white/10 transition-colors duration-200"
                onClick={() => setIsCollapsed(!isCollapsed)}
              >
                {isCollapsed ? (
                  <ChevronRight className="h-4 w-4" />
                ) : (
                  <ChevronLeft className="h-4 w-4" />
                )}
              </Button>
              
              {/* Close button for mobile */}
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden h-8 w-8 hover:bg-white/10 transition-colors duration-200"
                onClick={onClose}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
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
                    'group relative flex items-center rounded-xl transition-all duration-300 ease-in-out',
                    isCollapsed ? 'justify-center p-3' : 'space-x-3 px-4 py-3',
                    isActive
                      ? 'bg-gradient-to-r from-ai-violet-600/20 to-electric-blue-600/20 text-white border border-ai-violet-500/30 shadow-lg'
                      : 'text-muted-foreground hover:bg-white/5 hover:text-white hover:border-white/10 border border-transparent'
                  )}
                >
                  <div className="relative">
                    <Icon className={cn(
                      "transition-all duration-300",
                      isCollapsed ? "h-6 w-6" : "h-5 w-5",
                      isActive && "text-ai-violet-400"
                    )} />
                    {item.aiPowered && (
                      <div className="absolute -top-1 -right-1 w-2 h-2 bg-ai-violet-500 rounded-full animate-pulse" />
                    )}
                  </div>
                  
                  {!isCollapsed && (
                    <div className="flex items-center justify-between flex-1">
                      <span className="font-medium tracking-tight">{item.label}</span>
                      {item.aiPowered && (
                        <Zap className="h-3 w-3 text-ai-violet-400 animate-pulse" />
                      )}
                    </div>
                  )}

                  {/* Tooltip for collapsed state */}
                  {isCollapsed && (
                    <div className="absolute left-full ml-2 px-3 py-2 bg-charcoal-800 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50 border border-white/10">
                      {item.label}
                      <div className="absolute top-1/2 left-0 transform -translate-y-1/2 -translate-x-1 w-2 h-2 bg-charcoal-800 rotate-45 border-l border-b border-white/10" />
                    </div>
                  )}

                  {/* Active indicator */}
                  {isActive && (
                    <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-ai-violet-500 to-electric-blue-500 rounded-r-full" />
                  )}
                </Link>
              );
            })}
          </nav>

          {/* AI Status Indicator */}
          {!isCollapsed && (
            <div className="p-4 border-t border-white/10">
              <div className="flex items-center space-x-3 p-3 rounded-xl bg-gradient-to-r from-ai-violet-600/10 to-electric-blue-600/10 border border-ai-violet-500/20">
                <div className="relative">
                  <Brain className="h-5 w-5 text-ai-violet-400" />
                  <div className="absolute inset-0 animate-pulse">
                    <Brain className="h-5 w-5 text-ai-violet-400 opacity-50" />
                  </div>
                </div>
                <div className="flex-1">
                  <div className="text-sm font-medium text-white">AI Assistant</div>
                  <div className="text-xs text-muted-foreground">Online & Ready</div>
                </div>
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              </div>
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
