'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { MessageCircle, Bot, User, Send } from 'lucide-react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { apiClient } from '@/lib/api';

interface Comment {
  id: number;
  content: string;
  is_ai_generated: boolean;
  author: {
    id: number | null;
    name: string;
    email: string;
  };
  created_at: string;
  updated_at: string;
}

interface TaskCommentsProps {
  taskId: number;
}

export function TaskComments({ taskId }: TaskCommentsProps) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch comments
  const fetchComments = async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get(`/api/comments/task/${taskId}`);
      setComments(response.data.comments);
    } catch (error) {
      console.error('Error fetching comments:', error);
      toast.error('Failed to load comments');
    } finally {
      setIsLoading(false);
    }
  };

  // Submit new comment
  const handleSubmitComment = async () => {
    if (!newComment.trim()) return;

    try {
      setIsSubmitting(true);
      const response = await apiClient.post(`/api/comments/task/${taskId}`, {
        content: newComment.trim()
      });
      
      setComments(prev => [...prev, response.data]);
      setNewComment('');
      toast.success('Comment added successfully');
    } catch (error) {
      console.error('Error adding comment:', error);
      toast.error('Failed to add comment');
    } finally {
      setIsSubmitting(false);
    }
  };

  useEffect(() => {
    if (taskId) {
      fetchComments();
    }
  }, [taskId]);

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2">
          <MessageCircle className="w-5 h-5" />
          <h3 className="text-lg font-semibold">Comments</h3>
        </div>
        <div className="text-center py-4 text-gray-500">Loading comments...</div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <MessageCircle className="w-5 h-5" />
        <h3 className="text-lg font-semibold">Comments</h3>
        {comments.length > 0 && (
          <Badge variant="outline">{comments.length}</Badge>
        )}
      </div>

      {/* Comments list */}
      <div className="space-y-3 max-h-60 overflow-y-auto">
        {comments.length === 0 ? (
          <div className="text-center py-4 text-gray-500">
            No comments yet. Be the first to add one!
          </div>
        ) : (
          comments.map((comment) => (
            <div
              key={comment.id}
              className={`p-3 rounded-lg border ${
                comment.is_ai_generated
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
                  : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  {comment.is_ai_generated ? (
                    <Bot className="w-4 h-4 text-blue-600" />
                  ) : (
                    <User className="w-4 h-4 text-gray-600" />
                  )}
                  <span className="font-medium text-sm">
                    {comment.author.name}
                  </span>
                  {comment.is_ai_generated && (
                    <Badge className="bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 text-xs">
                      🤖 AI
                    </Badge>
                  )}
                </div>
                <span className="text-xs text-gray-500">
                  {format(new Date(comment.created_at), 'MMM d, HH:mm')}
                </span>
              </div>
              <p className={`text-sm ${
                comment.is_ai_generated 
                  ? 'text-blue-800 dark:text-blue-200 italic' 
                  : 'text-gray-700 dark:text-gray-300'
              }`}>
                {comment.content}
              </p>
            </div>
          ))
        )}
      </div>

      {/* Add new comment */}
      <div className="space-y-2">
        <Textarea
          placeholder="Add a comment..."
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          className="min-h-[80px]"
        />
        <div className="flex justify-end">
          <Button
            onClick={handleSubmitComment}
            disabled={!newComment.trim() || isSubmitting}
            size="sm"
          >
            {isSubmitting ? (
              'Adding...'
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Add Comment
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}