'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useCurrentUser } from '@/hooks/use-current-user';
import { AuditDashboard } from '@/components/admin/audit-dashboard';
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
            Project Audit
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Monitor project deadlines and automatically flag overdue tasks as blockers
          </p>
        </div>
      </div>

      {/* Audit Dashboard */}
      <AuditDashboard />
    </div>
  );
}