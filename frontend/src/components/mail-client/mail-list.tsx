'use client';

import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Search, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import MailItem from './mail-item';
import { MailItem as MailItemType } from '@/types/mail';

interface MailListProps {
  onSelectMail: (mail: any) => void;
  selectedMailId?: string;
  mails?: MailItemType[];
  refreshMails: () => void;
}

export default function MailList({
  onSelectMail,
  selectedMailId,
  mails = [],
  refreshMails
}: MailListProps) {
  // Auto-select first email on component mount
  useEffect(() => {
    if (mails.length > 0 && !selectedMailId) {
      onSelectMail(mails[0]);
    }
  }, [mails, onSelectMail, selectedMailId]);
  return (
    <div className='flex flex-1 flex-col overflow-hidden'>
      <div className='bg-background flex gap-4 border-b p-2'>
        {/* Mail action buttons */}
        <div className='bg-background flex items-center justify-between'>
          <Button
            variant='ghost'
            size='icon'
            className='h-8 w-8 cursor-pointer'
            onClick={() => refreshMails()}
          >
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
        {mails.map((email) => (
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
