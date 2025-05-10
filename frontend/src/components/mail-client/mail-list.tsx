'use client';

import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Search, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import MailItem from './mail-item';
import { MailItem as MailItemType } from '@/types/mail';

// Sample email data
const sampleEmails: MailItemType[] = [
  {
    id: '1',
    sender: {
      name: 'Daniel Johnson',
      email: 'danieljohnson@example.com'
    },
    subject: 'Feedback Request',
    snippet: 'Lorem ipsum dolor sit amet',
    date: new Date(2022, 9, 22, 9, 30, 0),
    content: `
# Feedback Request

Hello,

I'd like your feedback on the latest project deliverables. We've made significant progress on the following areas:

## Key Achievements
- Implemented the new user dashboard
- Fixed 15+ critical bugs
- Improved performance by 30%

Could you please review the changes by **Friday** and let me know your thoughts?

Thanks,
Daniel
        `
  },
  {
    id: '2',
    sender: {
      name: 'James Martin',
      email: 'james@example.com'
    },
    subject: 'Re: Conference Registration',
    snippet: 'Lorem ipsum dolor sit amet',
    date: new Date(2025, 4, 9, 15, 45),
    content: `
# Conference Registration Confirmed

I've completed the registration for the conference next month. The event promises to be a great networking opportunity.

## Event Details
- **Date:** June 15-17, 2025
- **Location:** Tech Convention Center
- **Registration ID:** CONF-2025-1234

Looking forward to attending with you!

Regards,
James
        `
  },
  {
    id: '3',
    sender: {
      name: 'Alex Johnson',
      email: 'alex@example.com'
    },
    subject: 'Vacation Plans',
    snippet: 'Lorem ipsum dolor sit amet',
    date: new Date(2025, 4, 8, 10, 15),
    content: `
# Summer Vacation Plans

Hey there!

I'm planning my vacation for next month. Would you like to join? I'm thinking about:

1. Beach retreat in Hawaii
2. Mountain hiking in Colorado
3. City exploring in New York

Let me know what you think!

Best,
Alex
        `
  },
  {
    id: '4',
    sender: {
      name: 'Tech Newsletter',
      email: 'news@tech.com'
    },
    subject: 'This Week in Tech',
    snippet: 'Lorem ipsum dolor sit amet',
    date: new Date(2025, 4, 7, 8, 0),
    content: `
# This Week in Tech

## AI Advancements
The latest breakthrough in machine learning has researchers excited about potential applications in healthcare.

## New Releases
- **XPhone 15** - Now with holographic display
- **DevBook Pro** - The ultimate laptop for developers

## Industry Trends
> "The future of tech is increasingly focused on sustainability" - Tech Analyst Jane Smith

[Read more on our website](https://example.com)
        `
  },
  {
    id: '5',
    sender: {
      name: 'Sarah Wilson',
      email: 'sarah@example.com'
    },
    subject: 'Project Proposal',
    snippet: 'Lorem ipsum dolor sit amet',
    date: new Date(2025, 4, 6, 14, 20),
    content: `
# Project Proposal: Q3 Initiative

Attached is the project proposal we discussed. Please review when you have a chance.

## Objectives
- Increase user engagement by 25%
- Reduce system downtime
- Launch new features by September

## Budget Requirements
| Item | Cost |
|------|------|
| Development | $120,000 |
| Testing | $45,000 |
| Marketing | $60,000 |

Please let me know if you need any clarification.

Sarah
        `
  },
  {
    id: '6',
    sender: {
      name: 'David Brown',
      email: 'david@example.com'
    },
    subject: 'Lunch Next Week?',
    snippet: 'Lorem ipsum dolor sit amet',
    date: new Date(2025, 4, 5, 11, 10),
    content: `
# Lunch Invitation

Hi there,

Would you be available for lunch next week? I'd love to catch up and hear what you've been working on.

I'm free on:
- Tuesday (12-2pm)
- Wednesday (1-3pm)
- Friday (anytime)

There's a new restaurant downtown I've been wanting to try!

Cheers,
David
        `
  },
  {
    id: '7',
    sender: {
      name: 'Marketing Team',
      email: 'marketing@company.com'
    },
    subject: 'New Campaign Launch',
    snippet: 'Lorem ipsum dolor sit amet',
    date: new Date(2025, 4, 4, 16, 30),
    content: `
# Marketing Campaign Launch

Team,

We're launching our new marketing campaign next Monday. Here's what you need to know:

## Campaign Details
- **Launch Date:** May 11, 2025
- **Target Audience:** Tech professionals, ages 25-45
- **Channels:** Social media, email, partner websites

### Key Messaging
* Focus on productivity benefits
* Emphasize new AI-powered features
* Highlight customer success stories

Please review the attached materials and be prepared for our final review meeting on Friday.

Marketing Team
        `
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
