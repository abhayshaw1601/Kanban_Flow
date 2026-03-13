import { useMutation, useQuery } from '@tanstack/react-query';
import { aiAnalyzer, type TaskAnalysis, type AnalyzeTaskRequest } from '@/lib/ai-analyzer';

/**
 * Hook for analyzing tasks with AI
 */
export function useAnalyzeTask() {
  return useMutation<TaskAnalysis, Error, AnalyzeTaskRequest>({
    mutationFn: (request) => aiAnalyzer.analyzeTask(request),
    onError: (error) => {
      console.error('Task analysis failed:', error);
    },
  });
}

/**
 * Hook for enhancing tasks with AI
 */
export function useEnhanceTask() {
  return useMutation<any, Error, { taskId: number; request: AnalyzeTaskRequest }>({
    mutationFn: ({ taskId, request }) => aiAnalyzer.enhanceTask(taskId, request),
    onError: (error) => {
      console.error('Task enhancement failed:', error);
    },
  });
}

/**
 * Hook for checking AI analyzer health
 */
export function useAIAnalyzerHealth() {
  return useQuery({
    queryKey: ['ai-analyzer-health'],
    queryFn: () => aiAnalyzer.checkHealth(),
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}

/**
 * Hook for bulk creating sub-tasks from AI analysis
 */
export function useCreateSubTasks() {
  return useMutation({
    mutationFn: async ({ 
      subTasks, 
      createTaskFn 
    }: { 
      subTasks: any[], 
      createTaskFn: (task: any) => Promise<any> 
    }) => {
      const results = [];
      for (const task of subTasks) {
        const result = await createTaskFn(task);
        results.push(result);
      }
      return results;
    },
  });
}