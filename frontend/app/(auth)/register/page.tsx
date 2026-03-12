'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Textarea } from '@/components/ui/textarea';
import { apiClient } from '@/lib/api';
import { toast } from 'sonner';
import Link from 'next/link';

interface Company {
  id: number;
  name: string;
  company_id: string;
  description?: string;
}

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('');
  const [companyOption, setCompanyOption] = useState(''); // 'existing' or 'new'
  const [selectedCompanyId, setSelectedCompanyId] = useState('');
  const [newCompanyName, setNewCompanyName] = useState('');
  const [newCompanyId, setNewCompanyId] = useState('');
  const [newCompanyDescription, setNewCompanyDescription] = useState('');
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(true);

  useEffect(() => {
    // Fetch available companies
    const fetchCompanies = async () => {
      try {
        const response = await apiClient.get('/api/companies');
        setCompanies(response.data);
      } catch (error) {
        console.error('Failed to fetch companies:', error);
      } finally {
        setIsLoadingCompanies(false);
      }
    };

    fetchCompanies();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name || !email || !password || !role) {
      toast.error('Please fill in all required fields');
      return;
    }

    if (password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    if (!companyOption) {
      toast.error('Please select a company option');
      return;
    }

    if (companyOption === 'existing' && !selectedCompanyId) {
      toast.error('Please select a company');
      return;
    }

    if (companyOption === 'new' && (!newCompanyName || !newCompanyId)) {
      toast.error('Please provide company name and identifier');
      return;
    }

    setIsLoading(true);

    try {
      const registrationData: any = {
        name,
        email,
        password,
        role,
      };

      if (companyOption === 'existing') {
        registrationData.company_id = parseInt(selectedCompanyId);
      } else {
        registrationData.company_name = newCompanyName;
        registrationData.company_identifier = newCompanyId;
        registrationData.company_description = newCompanyDescription || undefined;
      }

      await apiClient.post('/api/auth/register', registrationData);

      toast.success('Registration successful! Please log in.');
      router.push('/login');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
      toast.error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-lg">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Create an account</CardTitle>
          <CardDescription>
            Enter your information to get started
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Personal Information */}
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="John Doe"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                required
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={isLoading}
                required
              />
              <p className="text-xs text-muted-foreground">
                Password must be at least 8 characters
              </p>
            </div>

            {/* Role Selection */}
            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Select value={role} onValueChange={setRole} disabled={isLoading}>
                <SelectTrigger>
                  <SelectValue placeholder="Select your role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="admin">Admin</SelectItem>
                  <SelectItem value="employee">Employee</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Company Selection */}
            <div className="space-y-2">
              <Label htmlFor="company-option">Company</Label>
              <Select value={companyOption} onValueChange={setCompanyOption} disabled={isLoading || isLoadingCompanies}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose company option" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="existing">Join existing company</SelectItem>
                  <SelectItem value="new">Create new company</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Existing Company Selection */}
            {companyOption === 'existing' && (
              <div className="space-y-2">
                <Label htmlFor="existing-company">Select Company</Label>
                <Select value={selectedCompanyId} onValueChange={setSelectedCompanyId} disabled={isLoading}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose a company" />
                  </SelectTrigger>
                  <SelectContent>
                    {companies.map((company) => (
                      <SelectItem key={company.id} value={company.id.toString()}>
                        <div>
                          <div className="font-medium">{company.name}</div>
                          <div className="text-xs text-muted-foreground">ID: {company.company_id}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* New Company Creation */}
            {companyOption === 'new' && (
              <div className="space-y-4 p-4 border rounded-lg bg-muted/50">
                <h4 className="font-medium">Create New Company</h4>
                
                <div className="space-y-2">
                  <Label htmlFor="company-name">Company Name</Label>
                  <Input
                    id="company-name"
                    type="text"
                    placeholder="Acme Corporation"
                    value={newCompanyName}
                    onChange={(e) => setNewCompanyName(e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="company-id">Company ID</Label>
                  <Input
                    id="company-id"
                    type="text"
                    placeholder="acme-corp"
                    value={newCompanyId}
                    onChange={(e) => setNewCompanyId(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, ''))}
                    disabled={isLoading}
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Unique identifier for your company (lowercase, letters, numbers, and hyphens only)
                  </p>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="company-description">Company Description (Optional)</Label>
                  <Textarea
                    id="company-description"
                    placeholder="Brief description of your company"
                    value={newCompanyDescription}
                    onChange={(e) => setNewCompanyDescription(e.target.value)}
                    disabled={isLoading}
                    rows={3}
                  />
                </div>
              </div>
            )}

            <Button
              type="submit"
              className="w-full"
              disabled={isLoading}
            >
              {isLoading ? 'Creating account...' : 'Create account'}
            </Button>
          </form>
          
          <div className="mt-4 text-center text-sm text-muted-foreground">
            Already have an account?{' '}
            <Link href="/login" className="text-primary hover:underline">
              Sign in
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
