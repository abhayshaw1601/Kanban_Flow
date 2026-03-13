'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCurrentUser } from '@/hooks/use-current-user';
import { AuditDashboard } from '@/components/admin/audit-dashboard';
import { DiagramAnalyzer } from '@/components/admin/diagram-analyzer';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Brain } from 'lucide-react';
import { toast } from 'sonner';

export default function AuditPage() {
  const router = useRouter();
  const { data: currentUser, isLoading: userLoading } = useCurrentUser();

  // Redirect non-admin users
  useEffect(() => {
    if (!userLoading && currentUser && currentUser.role !== 'admin') {
      router.push('/dashboard');
      toast.error('Access denied. Admin privileges required.');
    }
  }, [currentUser, userLoading, router]);

  // Don't render anything while checking user role
  if (userLoading || (currentUser && currentUser.role !== 'admin')) {
    return null;
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-gray-100">
            Admin Tools
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Project audit system and AI-powered diagram analysis
          </p>
        </div>
      </div>

      {/* Tabs for different admin tools */}
      <Tabs defaultValue="audit" className="space-y-6">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="audit" className="flex items-center gap-2">
            <Search className="w-4 h-4" />
            Project Audit
          </TabsTrigger>
          <TabsTrigger value="diagram" className="flex items-center gap-2">
            <Brain className="w-4 h-4" />
            Diagram Analyzer
          </TabsTrigger>
        </TabsList>

        <TabsContent value="audit">
          <AuditDashboard />
        </TabsContent>

        <TabsContent value="diagram">
          <DiagramAnalyzer />
        </TabsContent>
      </Tabs>
    </div>
  );
}