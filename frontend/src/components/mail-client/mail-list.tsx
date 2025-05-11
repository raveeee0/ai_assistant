'use client';

import React, { useState, useEffect } from 'react';
import { Input } from '@/components/ui/input';
import { Search, RefreshCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton'; // Import skeleton component
import MailItem from './mail-item';
import { MailItem as MailItemType } from '@/types/mail';

interface MailListProps {
  onSelectMail: (mail: any) => void;
  selectedMailId?: string;
  mails?: MailItemType[];
  refreshMails: () => void;
  isLoading?: boolean;
}

// Mail Skeleton component for loading state
const MailItemSkeleton = () => (
  <div className='border-accent flex items-start gap-2 rounded-md border p-3'>
    <div className='min-w-0 flex-1'>
      <div className='flex items-center justify-between'>
        <Skeleton className='h-4 w-24' />
        <Skeleton className='h-3 w-12' />
      </div>
      <Skeleton className='mt-2 h-4 w-full' />
      <Skeleton className='mt-2 h-3 w-3/4' />
    </div>
  </div>
);

export default function MailList({
  onSelectMail,
  selectedMailId,
  mails = [],
  refreshMails,
  isLoading = false
}: MailListProps) {
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
            disabled={isLoading}
          >
            <RefreshCcw size={16} className={isLoading ? 'animate-spin' : ''} />
          </Button>
        </div>
        {/* Search bar */}
        <div className='bg-background flex items-center rounded-md border px-2 py-1'>
          <Search size={18} className='text-muted-foreground mr-2' />
          <Input
            placeholder='Search'
            className='!bg-background border-0 px-0 py-0 text-sm focus-visible:ring-0'
            disabled={isLoading}
          />
        </div>
      </div>

      {/* Email list */}
      <div className='flex h-full flex-1 flex-col gap-2 overflow-auto p-2'>
        {isLoading ? (
          // Show skeleton items when loading
          Array.from({ length: 5 }).map((_, index) => (
            <MailItemSkeleton key={`skeleton-${index}`} />
          ))
        ) : mails.length > 0 ? (
          // Show actual mail items when available
          mails.map((email) => (
            <MailItem
              mail={email}
              key={email.id}
              onSelectMail={onSelectMail}
              selectedMailId={selectedMailId}
            />
          ))
        ) : (
          // Show empty state when no emails
          <div className='text-muted-foreground flex h-full items-center justify-center'>
            No emails found
          </div>
        )}
      </div>
    </div>
  );
}
