import { redirect } from 'next/navigation';

export default function DashboardPage() {
  // Redirect to boards page as the main dashboard view
  redirect('/dashboard/boards');
}
