'use client';

import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';
import {
  ArrowLeft,
  Archive,
  Trash2,
  Reply,
  ReplyAll,
  Forward,
  Star,
  Clock,
  Tag,
  MoreHorizontal,
  ChevronDown,
  Paperclip
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Mail } from '@/types/mail';

interface MailViewProps {
  mail: Mail;
  onBack: () => void;
}

export default function MailView({ mail, onBack }: MailViewProps) {
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

  // Sample content (for demo)
  let content;

  if (mail.id === '1') {
    content = `
      <p>Hi there,</p>
      <p>I'd like your feedback on the latest project deliverables. We've made significant progress, and I value your input to ensure we're on the right track.</p>
      <p>I've attached the deliverables for your review, and I'm particularly interested in any areas where you think we can further enhance the quality or efficiency.</p>
      <p>Your feedback is invaluable, and I appreciate your time and expertise. Let's work together to make this project a success.</p>
      <p>Regards,<br>${mail.sender.name}</p>
    `;
  } else {
    content = `
      <p>Hi there,</p>
      <p>${mail.preview}</p>
      <p>Let me know if you have any questions.</p>
      <p>Best regards,<br>${mail.sender.name}</p>
    `;
  }

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
          <div className='flex items-center gap-2'>
            <Button variant='ghost' size='icon' className='h-8 w-8'>
              <Star
                size={16}
                className={
                  mail.isStarred ? 'fill-amber-500 text-amber-500' : ''
                }
              />
            </Button>
          </div>
        </div>

        <div className='flex items-start gap-3'>
          <Avatar className='h-10 w-10'>
            <div className='bg-primary text-primary-foreground'>
              {mail.sender.name.charAt(0)}
            </div>
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

            {mail.labels && mail.labels.length > 0 && (
              <div className='mt-2 flex flex-wrap gap-1'>
                {mail.labels.map((label, i) => (
                  <Badge key={i} variant='outline' className='text-xs'>
                    <Tag size={10} className='mr-1' />
                    {label}
                  </Badge>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Email body */}
      <div className='flex-1 overflow-auto p-4'>
        <div
          className='prose prose-sm max-w-none'
          dangerouslySetInnerHTML={{ __html: content }}
        />

        {/* Attachments (sample) */}
        <div className='mt-6'>
          <h3 className='mb-2 flex items-center gap-1 text-sm font-medium'>
            <Paperclip size={14} />
            <span>2 Attachments</span>
          </h3>

          <div className='grid grid-cols-1 gap-2 md:grid-cols-2'>
            <div className='flex items-center gap-2 rounded-md border p-2'>
              <div className='bg-muted flex h-10 w-10 items-center justify-center rounded'>
                <Paperclip size={16} />
              </div>
              <div className='min-w-0 flex-1'>
                <div className='truncate text-sm font-medium'>document.pdf</div>
                <div className='text-muted-foreground text-xs'>2.4 MB</div>
              </div>
            </div>

            <div className='flex items-center gap-2 rounded-md border p-2'>
              <div className='bg-muted flex h-10 w-10 items-center justify-center rounded'>
                <Paperclip size={16} />
              </div>
              <div className='min-w-0 flex-1'>
                <div className='truncate text-sm font-medium'>
                  presentation.pptx
                </div>
                <div className='text-muted-foreground text-xs'>4.1 MB</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Reply section */}
      <div className='border-t p-4'>
        <textarea
          className='w-full resize-none rounded-md border p-4'
          placeholder='Reply Daniel Johnson...'
          rows={4}
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
