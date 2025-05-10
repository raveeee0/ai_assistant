'use client';

import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Search, Star, RefreshCcw, MoreVertical, StarOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar } from '@/components/ui/avatar';
import { Checkbox } from '@/components/ui/checkbox';
import { cn } from '@/lib/utils';
import { MailItem as MailItemType } from '@/types/mail';
import MailItem from './mail-item';

// Sample email data
const sampleEmails: MailItemType[] = [
  {
    id: '1',
    sender: {
      name: 'Daniel Johnson',
      email: 'danieljohnson@example.com'
    },
    subject: 'Feedback Request',
    preview:
      "I'd like your feedback on the latest project deliverables. We've made significant progress...",
    isRead: true,
    isStarred: true,
    date: new Date(2022, 9, 22, 9, 30, 0), // Oct 22, 2022
    labels: ['work']
  },
  {
    id: '2',
    sender: {
      name: 'James Martin',
      email: 'james@example.com'
    },
    subject: 'Re: Conference Registration',
    preview:
      "I've completed the registration for the conference next month. The event promises to be a great networking opportunity...",
    isRead: true,
    isStarred: false,
    date: new Date(2025, 4, 9, 15, 45),
    labels: ['work', 'conference']
  },
  {
    id: '3',
    sender: {
      name: 'Alex Johnson',
      email: 'alex@example.com'
    },
    subject: 'Vacation Plans',
    preview: "I'm planning my vacation for next month. Would you like to join?",
    isRead: true,
    isStarred: false,
    date: new Date(2025, 4, 8, 10, 15),
    labels: ['personal']
  },
  {
    id: '4',
    sender: {
      name: 'Tech Newsletter',
      email: 'news@tech.com'
    },
    subject: 'This Week in Tech',
    preview: 'The latest tech news: AI advancements, new gadget releases...',
    isRead: false,
    isStarred: true,
    date: new Date(2025, 4, 7, 8, 0),
    labels: []
  },
  {
    id: '5',
    sender: {
      name: 'Sarah Wilson',
      email: 'sarah@example.com'
    },
    subject: 'Project Proposal',
    preview: 'Attached is the project proposal we discussed. Please review...',
    isRead: true,
    isStarred: false,
    date: new Date(2025, 4, 6, 14, 20),
    labels: ['work']
  },
  {
    id: '6',
    sender: {
      name: 'David Brown',
      email: 'david@example.com'
    },
    subject: 'Lunch Next Week?',
    preview:
      "Would you be available for lunch next week? I'd love to catch up...",
    isRead: false,
    isStarred: false,
    date: new Date(2025, 4, 5, 11, 10),
    labels: ['personal']
  },
  {
    id: '7',
    sender: {
      name: 'Marketing Team',
      email: 'marketing@company.com'
    },
    subject: 'New Campaign Launch',
    preview: "We're launching our new marketing campaign next Monday...",
    isRead: true,
    isStarred: false,
    date: new Date(2025, 4, 4, 16, 30),
    labels: ['work']
  }
];

interface MailListProps {
  onSelectMail: (mail: any) => void;
  selectedMailId?: string;
}

export default function MailList({
  onSelectMail,
  selectedMailId
}: MailListProps) {
  const [emails] = useState(sampleEmails);

  // Auto-select first email on component mount
  useEffect(() => {
    if (emails.length > 0 && !selectedMailId) {
      onSelectMail(emails[0]);
    }
  }, [emails, onSelectMail, selectedMailId]);
  return (
    <div className='flex flex-1 flex-col overflow-hidden'>
      <div className='bg-background flex gap-4 border-b p-2'>
        {/* Mail action buttons */}
        <div className='bg-background flex items-center justify-between'>
          <Button variant='ghost' size='icon' className='h-8 w-8'>
            <RefreshCcw size={16} />
          </Button>
        </div>
        {/* Search bar */}
        <div className='bg-background flex items-center rounded-md border px-2 py-1'>
          <Search size={18} className='text-muted-foreground mr-2' />
          <Input
            placeholder='Search'
            className='bg-background border-0 px-0 py-0 text-sm focus-visible:ring-0'
          />
        </div>
      </div>

      {/* Email list */}
      <div className='flex h-full flex-1 flex-col gap-2 overflow-auto p-2'>
        {emails.map((email) => (
          <MailItem
            mail={email}
            key={email.id}
            onSelectMail={onSelectMail}
            selectedMailId={selectedMailId}
          />
        ))}
      </div>
    </div>
  );
}
