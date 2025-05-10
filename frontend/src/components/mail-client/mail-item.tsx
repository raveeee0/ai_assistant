import { cn } from '@/lib/utils';
import { MailItem as MailItemType } from '@/types/mail';
import React from 'react';

interface Props {
  mail: MailItemType;
  onSelectMail: (mail: MailItemType) => void;
  selectedMailId?: string;
}

export default function MailItem({
  mail,
  onSelectMail,
  selectedMailId
}: Props) {
  // Format date for display
  const formatDate = (date: Date) => {
    const today = new Date();
    const isToday =
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear();

    if (isToday) {
      return date.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit'
      });
    } else {
      return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  };

  return (
    <div
      key={mail.id}
      onClick={() => onSelectMail({ ...mail })}
      className={cn(
        'hover:bg-accent/50 border-accent flex cursor-pointer items-start gap-2 rounded-md border p-3 transition-colors',
        selectedMailId === mail.id && 'bg-accent'
      )}
    >
      <div className='min-w-0 flex-1'>
        <div className='flex items-center justify-between'>
          <div className='flex items-center gap-2'>
            <span className={cn('truncate text-sm', 'font-medium')}>
              {mail.sender.name}
            </span>
          </div>
          <span className='text-muted-foreground text-xs'>
            {formatDate(mail.date)}
          </span>
        </div>

        <div className='truncate text-sm'>{mail.subject}</div>

        <div className='text-muted-foreground line-clamp-2 text-xs'>
          {mail.snippet}
        </div>
      </div>
    </div>
  );
}
