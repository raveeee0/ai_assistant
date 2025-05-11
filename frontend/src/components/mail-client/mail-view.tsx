'use client';

import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import {
  ArrowLeft,
  Archive,
  Trash2,
  Reply,
  ReplyAll,
  Forward,
  MoreHorizontal,
  ChevronDown,
  Loader2, // Added for loading animation
  AlertCircle // Added for error icon
} from 'lucide-react';
import { MailItem } from '@/types/mail';
import { toast } from 'sonner'; // Added import for toast

import Markdown from 'react-markdown';
import { useEffect, useState } from 'react';
import { DraftRequest, Request } from '@/types/utils';
import { cn } from '@/lib/utils';

interface MailViewProps {
  mail: MailItem;
  onBack: () => void;
  summary?: Request;
  draft?: DraftRequest;
}

export default function MailView({
  mail,
  onBack,
  summary,
  draft
}: MailViewProps) {
  const [reply, setReply] = useState('');
  const [isSending, setIsSending] = useState(false); // Added state for tracking send status

  useEffect(() => {
    setReply(draft?.result || '');
  }, [draft]);

  // Format date for display
  const formatDate = (date: Date) => {
    return date.toLocaleString([], {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const sendEmail = () => {
    if (!reply.trim()) {
      toast.error('Cannot send empty reply');
      return;
    }

    setIsSending(true);
    toast.loading('Sending reply...');

    // Create quoted original message with header
    const quoteHeader = `On ${mail.date.toLocaleString([], {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })} ${mail.sender.name} <${mail.sender.email}> wrote:`;

    // Format the original content with '>' prefix for each line
    const quotedContent = mail.content
      ? `${quoteHeader}\n>${mail.content.split('\n').join('\n> ')}`
      : '';

    // Combine reply with quoted original message
    const fullReplyContent = `${reply}\n\n${quotedContent}`;

    fetch('http://localhost:8000/reply-mail', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        to: mail.sender.email,
        subject: mail.subject,
        original_message_id: mail.originalMessageId,
        thread_id: mail.threadId,
        message: fullReplyContent
      })
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error('Failed to send email');
        }
        return response.json();
      })
      .then((data) => {
        console.log('Email sent successfully:', data);
        toast.dismiss(); // Dismiss the loading toast
        toast.success('Reply sent successfully');
        setReply(''); // Clear the reply field after successful send

        // read the email
        fetch('http://localhost:8000/mark-as-read', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            message_id: mail.originalMessageId
          })
        });
      })
      .catch((error) => {
        console.error(error);
        toast.dismiss(); // Dismiss the loading toast
        toast.error(`Failed to send: ${error.message}`);
      })
      .finally(() => {
        setIsSending(false); // Reset sending state
      });
  };

  return (
    <div className='flex h-full flex-col'>
      {/* Mail actions toolbar */}
      <div className='bg-background flex items-center justify-between border-b p-2'>
        <div className='flex items-center gap-1'>
          <Button
            variant='ghost'
            size='icon'
            onClick={onBack}
            className='md:hidden'
          >
            <ArrowLeft size={18} />
          </Button>
          <Button variant='ghost' size='icon'>
            <Archive size={18} />
          </Button>
          <Button variant='ghost' size='icon'>
            <Trash2 size={18} />
          </Button>
          <Button variant='ghost' size='icon'>
            <Reply size={18} />
          </Button>
          <Button variant='ghost' size='icon'>
            <ReplyAll size={18} />
          </Button>
          <Button variant='ghost' size='icon'>
            <Forward size={18} />
          </Button>
        </div>

        <div>
          <Button variant='ghost' size='icon'>
            <MoreHorizontal size={18} />
          </Button>
        </div>
      </div>

      {/* Email header */}
      <div className='border-b p-4'>
        <div className='mb-3 flex items-start justify-between'>
          <h2 className='text-xl font-semibold'>{mail.subject}</h2>
        </div>

        <div className='flex items-start gap-3'>
          <Avatar className='h-10 w-10'>
            <AvatarFallback>
              {mail.sender.name
                .split(' ')
                .map((x) => x.charAt(0))
                .concat()}
            </AvatarFallback>
          </Avatar>

          <div className='flex-1'>
            <div className='flex items-center justify-between'>
              <div>
                <div className='font-medium'>{mail.sender.name}</div>
                <div className='text-muted-foreground text-sm'>
                  &lt;{mail.sender.email}&gt;
                </div>
              </div>

              <div className='text-muted-foreground flex items-center gap-2 text-sm'>
                <span>{formatDate(mail.date)}</span>
                <Button variant='ghost' size='icon' className='h-6 w-6'>
                  <MoreHorizontal size={14} />
                </Button>
              </div>
            </div>

            <div className='text-muted-foreground mt-1 flex flex-wrap items-center gap-2 text-sm'>
              <div className='flex items-center gap-1'>
                <span>To: me</span>
              </div>

              <Button variant='ghost' size='sm' className='h-6 px-1 text-xs'>
                Show details <ChevronDown size={12} />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Email body */}
      <div className='prose prose-invert prose-sm max-w-none flex-1 overflow-auto p-4'>
        {summary && (
          <div className='bg-muted/30 mb-4 rounded-md border p-3'>
            <h3 className='mt-1 mb-1 text-sm font-semibold'>Summary:</h3>
            {summary.isLoading ? (
              summary.result == null || summary.result == '' ? (
                <div className='text-muted-foreground flex items-center text-sm italic'>
                  <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                  Loading summary...
                </div>
              ) : (
                <div className='text-sm'>
                  <Markdown
                    children={summary.result || 'No summary available.'}
                  />
                </div>
              )
            ) : summary.error ? (
              <div className='text-destructive flex items-center text-sm'>
                <AlertCircle className='mr-2 h-4 w-4' />
                {summary.result}
              </div>
            ) : (
              <div className='text-sm'>
                <Markdown
                  children={summary.result || 'No summary available.'}
                />
              </div>
            )}
          </div>
        )}
        <Markdown>{mail.content}</Markdown>
      </div>

      {/* Reply section */}
      <div className='border-t p-4'>
        {draft?.error && (
          <div className='text-destructive mb-2 flex items-center text-sm'>
            <AlertCircle className='mr-2 h-4 w-4' />
            Error loading draft: {draft.error}
          </div>
        )}
        {draft && draft.thinks.length > 0 && (
          <div className='mb-2 flex items-center text-sm text-gray-300'>
            {draft.thinks.map((think, index) => (
              <p key={index} className='mr-1'>
                {think}
              </p>
            ))}
          </div>
        )}
        <textarea
          className={cn(
            'w-full resize-none rounded-md border p-4',
            draft?.isLoading && '!text-gray-500'
          )}
          placeholder={
            draft?.isLoading
              ? 'Loading draft...'
              : 'Reply to ' + mail.sender.name + '...'
          }
          rows={4}
          value={reply} // Use reply state, fallback to draft result
          onChange={(e) => setReply(e.target.value)}
          disabled={draft?.isLoading || isSending}
        ></textarea>
        <div className='mt-2 flex justify-end'>
          <Button
            className='cursor-pointer gap-1'
            onClick={() => sendEmail()}
            disabled={isSending}
          >
            {isSending ? (
              <>
                <Loader2 size={14} className='animate-spin' /> Sending...
              </>
            ) : (
              <>
                <Reply size={14} /> Send
              </>
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
