'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { LordIcon } from '@/components/ui/lord-icon';

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 glass-nav">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <LordIcon
                src="https://cdn.lordicon.com/wuvorxbv.json"
                trigger="hover"
                colors="primary:#3b82f6,secondary:#1e40af"
                size={32}
              />
              <h1 className="text-xl font-semibold text-foreground">KanbanFlow</h1>
            </div>
            <div className="flex items-center space-x-3">
              <Link href="/login">
                <Button variant="ghost" className="btn-ghost">
                  Sign In
                </Button>
              </Link>
              <Link href="/register">
                <Button className="btn-primary">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-24 px-4 sm:px-6 lg:px-8 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-subtle"></div>
        <div className="relative max-w-7xl mx-auto">
          <div className="text-center max-w-4xl mx-auto">
            <Badge variant="secondary" className="glass-subtle mb-6 animate-fade-in">
              <LordIcon
                src="https://cdn.lordicon.com/jvucoldz.json"
                trigger="hover"
                colors="primary:#3b82f6"
                size={16}
                className="mr-2"
              />
              Trusted by 10,000+ teams worldwide
            </Badge>
            
            <h1 className="text-display text-5xl md:text-6xl lg:text-7xl font-normal text-foreground mb-6 animate-slide-up text-balance">
              Project management
              <span className="block text-primary">made simple</span>
            </h1>
            
            <p className="text-body text-xl text-muted-foreground mb-8 max-w-2xl mx-auto animate-fade-in text-pretty">
              Transform your team's workflow with intuitive Kanban boards, powerful collaboration tools, and real-time insights that drive results.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center animate-scale-in">
              <Link href="/register">
                <Button size="lg" className="btn-primary text-lg px-8 py-4 h-auto">
                  <LordIcon
                    src="https://cdn.lordicon.com/jgnvfzqg.json"
                    trigger="hover"
                    colors="primary:#ffffff"
                    size={20}
                    className="mr-2"
                  />
                  Start free trial
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="outline" size="lg" className="text-lg px-8 py-4 h-auto interactive">
                  <LordIcon
                    src="https://cdn.lordicon.com/hrjifpbq.json"
                    trigger="hover"
                    colors="primary:#3b82f6"
                    size={20}
                    className="mr-2"
                  />
                  Login
                </Button>
              </Link>
            </div>
            
            <p className="text-sm text-muted-foreground mt-4 animate-fade-in">
              No credit card required • 14-day free trial • Cancel anytime
            </p>
          </div>
        </div>
      </section>

      {/* Logo Bar */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 border-t glass-subtle">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-sm text-muted-foreground mb-8">
            Trusted by leading companies worldwide
          </p>
          <div className="flex justify-center items-center space-x-12 opacity-60">
            <div className="text-2xl font-bold text-muted-foreground">Acme Corp</div>
            <div className="text-2xl font-bold text-muted-foreground">TechFlow</div>
            <div className="text-2xl font-bold text-muted-foreground">InnovateLab</div>
            <div className="text-2xl font-bold text-muted-foreground">DataSync</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge variant="outline" className="glass-subtle mb-4">
              Features
            </Badge>
            <h2 className="text-display text-4xl md:text-5xl font-normal text-foreground mb-6 text-balance">
              Everything you need to
              <span className="block text-primary">succeed together</span>
            </h2>
            <p className="text-body text-xl text-muted-foreground max-w-2xl mx-auto text-pretty">
              Powerful features designed to streamline your workflow and boost team productivity.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="card-glass group">
              <CardContent className="p-8">
                <div className="mb-6">
                  <LordIcon
                    src="https://cdn.lordicon.com/wuvorxbv.json"
                    trigger="hover"
                    colors="primary:#3b82f6,secondary:#1e40af"
                    size={48}
                  />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  Visual Kanban Boards
                </h3>
                <p className="text-muted-foreground text-pretty">
                  Organize tasks with intuitive drag-and-drop boards that make workflow visualization effortless and engaging.
                </p>
              </CardContent>
            </Card>

            <Card className="card-glass group">
              <CardContent className="p-8">
                <div className="mb-6">
                  <LordIcon
                    src="https://cdn.lordicon.com/dxjqoygy.json"
                    trigger="hover"
                    colors="primary:#10b981,secondary:#059669"
                    size={48}
                  />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  Real-time Collaboration
                </h3>
                <p className="text-muted-foreground text-pretty">
                  Work together seamlessly with live updates, comments, and notifications that keep everyone in sync.
                </p>
              </CardContent>
            </Card>

            <Card className="card-glass group">
              <CardContent className="p-8">
                <div className="mb-6">
                  <LordIcon
                    src="https://cdn.lordicon.com/qhviklyi.json"
                    trigger="hover"
                    colors="primary:#f59e0b,secondary:#d97706"
                    size={48}
                  />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  Advanced Analytics
                </h3>
                <p className="text-muted-foreground text-pretty">
                  Track progress with detailed insights and reports that help you make data-driven decisions.
                </p>
              </CardContent>
            </Card>

            <Card className="card-glass group">
              <CardContent className="p-8">
                <div className="mb-6">
                  <LordIcon
                    src="https://cdn.lordicon.com/kbtmbyzy.json"
                    trigger="hover"
                    colors="primary:#ef4444,secondary:#dc2626"
                    size={48}
                  />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  Enterprise Security
                </h3>
                <p className="text-muted-foreground text-pretty">
                  Bank-level security with role-based access control and data encryption you can trust.
                </p>
              </CardContent>
            </Card>

            <Card className="card-glass group">
              <CardContent className="p-8">
                <div className="mb-6">
                  <LordIcon
                    src="https://cdn.lordicon.com/jgnvfzqg.json"
                    trigger="hover"
                    colors="primary:#8b5cf6,secondary:#7c3aed"
                    size={48}
                  />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  Lightning Fast
                </h3>
                <p className="text-muted-foreground text-pretty">
                  Built for speed with modern architecture ensuring smooth performance at any scale.
                </p>
              </CardContent>
            </Card>

            <Card className="card-glass group">
              <CardContent className="p-8">
                <div className="mb-6">
                  <LordIcon
                    src="https://cdn.lordicon.com/nocovwne.json"
                    trigger="hover"
                    colors="primary:#06b6d4,secondary:#0891b2"
                    size={48}
                  />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">
                  Smart Automation
                </h3>
                <p className="text-muted-foreground text-pretty">
                  Automate repetitive tasks and workflows to focus on what matters most to your business.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 glass-subtle">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <Badge variant="outline" className="glass-subtle mb-4">
              How it works
            </Badge>
            <h2 className="text-display text-4xl md:text-5xl font-normal text-foreground mb-6 text-balance">
              Get started in
              <span className="block text-primary">three simple steps</span>
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="mb-6 flex justify-center">
                <div className="w-16 h-16 glass rounded-full flex items-center justify-center">
                  <LordIcon
                    src="https://cdn.lordicon.com/jvucoldz.json"
                    trigger="hover"
                    colors="primary:#3b82f6"
                    size={32}
                  />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                1. Create your workspace
              </h3>
              <p className="text-muted-foreground text-pretty">
                Set up your team workspace in seconds with our intuitive onboarding process.
              </p>
            </div>

            <div className="text-center">
              <div className="mb-6 flex justify-center">
                <div className="w-16 h-16 glass rounded-full flex items-center justify-center">
                  <LordIcon
                    src="https://cdn.lordicon.com/dxjqoygy.json"
                    trigger="hover"
                    colors="primary:#3b82f6"
                    size={32}
                  />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                2. Invite your team
              </h3>
              <p className="text-muted-foreground text-pretty">
                Add team members and start collaborating with powerful permission controls.
              </p>
            </div>

            <div className="text-center">
              <div className="mb-6 flex justify-center">
                <div className="w-16 h-16 glass rounded-full flex items-center justify-center">
                  <LordIcon
                    src="https://cdn.lordicon.com/qhviklyi.json"
                    trigger="hover"
                    colors="primary:#3b82f6"
                    size={32}
                  />
                </div>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-3">
                3. Track progress
              </h3>
              <p className="text-muted-foreground text-pretty">
                Monitor your team's progress with real-time updates and detailed analytics.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-display text-4xl md:text-5xl font-normal text-foreground mb-6 text-balance">
            Ready to transform
            <span className="block text-primary">your workflow?</span>
          </h2>
          <p className="text-body text-xl text-muted-foreground mb-8 text-pretty">
            Join thousands of teams already using KanbanFlow to deliver projects faster and more efficiently.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link href="/register">
              <Button size="lg" className="btn-primary text-lg px-8 py-4 h-auto">
                <LordIcon
                  src="https://cdn.lordicon.com/jgnvfzqg.json"
                  trigger="hover"
                  colors="primary:#ffffff"
                  size={20}
                  className="mr-2"
                />
                Start your free trial
              </Button>
            </Link>
            <Link href="/login">
              <Button variant="outline" size="lg" className="text-lg px-8 py-4 h-auto interactive">
                Sign in to your account
              </Button>
            </Link>
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            No credit card required • 14-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t glass-subtle">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <LordIcon
                src="https://cdn.lordicon.com/wuvorxbv.json"
                trigger="hover"
                colors="primary:#3b82f6,secondary:#1e40af"
                size={24}
              />
              <span className="text-lg font-semibold text-foreground">KanbanFlow</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2026 KanbanFlow. Built with modern web technologies.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
