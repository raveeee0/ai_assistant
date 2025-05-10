'use client';

import { useEffect, useState } from 'react';
import Sidebar from './sidebar';
import { MailItem } from '@/types/mail';
import MailList from './mail-list';
import MailView from './mail-view';
import { cn } from '@/lib/utils';

export default function MailClientLayout() {
  const [selectedMail, setSelectedMail] = useState<MailItem | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [draft, setDraft] = useState<string | null>(null);

  useEffect(() => {
    if (selectedMail) {
      // Call the API to get the summary and draft
      fetch(`http://localhost:3000/api/mail/${selectedMail.id}/summary`).then(
        (response) => {
          if (response.ok) {
            response.json().then((data) => {
              setSummary(data.summary);
            });
          } else {
            console.error('Failed to fetch summary');
          }
        }
      );

      fetch(`http://localhost:3000/api/mail/${selectedMail.id}/draft`).then(
        (response) => {
          if (response.ok) {
            response.json().then((data) => {
              setDraft(data.draft);
            });
          } else {
            console.error('Failed to fetch draft');
          }
        }
      );
    }

    return () => {};
  }, [selectedMail]);

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
