'use client';

import { useState } from 'react';
import Sidebar from './sidebar';
import { Mail } from '@/types/mail';
import MailList from './mail-list';
import MailView from './mail-view';
import { cn } from '@/lib/utils';

export default function MailClientLayout() {
  const [selectedMail, setSelectedMail] = useState<Mail | null>(null);

  return (
    <div className='flex flex-1 overflow-hidden'>
      {/* Sidebar */}
      <Sidebar />

      {/* Mail List */}
      <div
        className={cn(
          `bg-background flex w-80 flex-col overflow-hidden border-r`,
          !selectedMail && 'hidden md:block'
        )}
      >
        <div className='bg-background flex items-center justify-between border-b p-2'>
          <div className='text-lg font-semibold'>Inbox</div>
        </div>
        <MailList
          onSelectMail={setSelectedMail}
          selectedMailId={selectedMail?.id}
        />
      </div>

      {/* Mail View */}
      <div className='bg-background flex-1 overflow-hidden'>
        {selectedMail ? (
          <MailView mail={selectedMail} onBack={() => setSelectedMail(null)} />
        ) : (
          <div className='text-muted-foreground flex h-full items-center justify-center'>
            Select an email to view
          </div>
        )}
      </div>
    </div>
  );
}
