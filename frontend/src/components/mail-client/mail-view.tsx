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
  ChevronDown
} from 'lucide-react';
import { MailItem } from '@/types/mail';

import Markdown from 'react-markdown';

interface MailViewProps {
  mail: MailItem;
  onBack: () => void;
  summary?: { isLoading: boolean; result: string | null };
  draft?: { isLoading: boolean; result: string | null };
}

export default function MailView({
  mail,
  onBack,
  summary,
  draft
}: MailViewProps) {
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
              <p className='text-muted-foreground text-sm italic'>
                Loading summary...
              </p>
            ) : (
              <div className='text-sm'>
                <Markdown
                  children={summary.result || 'No summary available.'}
                />
              </div>
            )}
          </div>
        )}
        <Markdown children={mail.content} />
      </div>

      {/* Reply section */}
      <div className='border-t p-4'>
        <textarea
          className='w-full resize-none rounded-md border p-4'
          placeholder={
            draft?.isLoading
              ? 'Loading draft...'
              : draft?.result || 'Reply ' + mail.sender.name + '...'
          }
          rows={4}
          defaultValue={draft?.result || ''}
          disabled={draft?.isLoading}
        ></textarea>
        <div className='mt-2 flex justify-end'>
          <Button className='gap-1'>
            <Reply size={14} /> Send
          </Button>
        </div>
      </div>
    </div>
  );
}
