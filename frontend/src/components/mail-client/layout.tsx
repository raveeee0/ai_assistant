'use client';

import { useEffect, useState } from 'react';
import Sidebar from './sidebar';
import { MailItem } from '@/types/mail';
import MailList from './mail-list';
import MailView from './mail-view';
import { cn } from '@/lib/utils';
import { Request } from '@/types/utils';

export default function MailClientLayout() {
  const [mails, setMails] = useState<MailItem[]>([]);
  const [selectedMail, setSelectedMail] = useState<MailItem | null>(null);
  const [summary, setSummary] = useState<Request>({
    isLoading: false,
    result: null,
    error: false
  });
  const [draft, setDraft] = useState<Request>({
    isLoading: false,
    result: null,
    error: false
  });

  useEffect(() => {
    refreshMails();
  }, []);

  const refreshMails = () => {
    fetch('http://127.0.0.1:8000/unread-mails').then((response) => {
      if (response.ok) {
        response.json().then((data) => {
          console.log('Fetched mails:', data);
          // Convert API response data to MailItem format
          const formattedMails = data.messages.map(
            (mail: {
              message_id: any;
              thread_id: any;
              senderName: any;
              senderEmail: any;
              subject: any;
              snippet: any;
              date: string | number | Date;
              text: any;
            }) => ({
              id: mail.message_id,
              threadId: mail.thread_id,
              sender: {
                name: mail.senderName,
                email: mail.senderEmail
              },
              subject: mail.subject,
              snippet: mail.snippet,
              date: new Date(mail.date),
              content: mail.text
            })
          );
          setMails(formattedMails);
        });
      } else {
        console.error('Failed to fetch mails');
      }
    });
  };

  useEffect(() => {
    if (selectedMail) {
      // Reset summary and draft when a new mail is selected
      setSummary({ isLoading: true, result: null, error: false });
      setDraft({ isLoading: true, result: null, error: false });

      // Call the API to get the summary
      fetch(`http://localhost:3000/api/mail/${selectedMail.id}/summary`)
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          throw new Error('Failed to fetch summary');
        })
        .then((data) => {
          setSummary({ isLoading: false, result: data.summary, error: false });
        })
        .catch((error) => {
          console.error(error);
          setSummary({
            isLoading: false,
            result: 'Error loading summary.',
            error: true
          });
        });

      // Call the API to get the draft
      fetch(`http://localhost:3000/api/mail/${selectedMail.id}/draft`)
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          throw new Error('Failed to fetch draft');
        })
        .then((data) => {
          setDraft({ isLoading: false, result: data.draft, error: false });
        })
        .catch((error) => {
          console.error(error);
          setDraft({
            isLoading: false,
            result: 'Error loading draft.',
            error: true
          });
        });
    } else {
      // Clear summary and draft if no mail is selected
      setSummary({ isLoading: false, result: null, error: false });
      setDraft({ isLoading: false, result: null, error: false });
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
          mails={mails}
          refreshMails={refreshMails}
        />
      </div>

      {/* Mail View */}
      <div className='bg-background flex-1 overflow-hidden'>
        {selectedMail ? (
          <MailView
            mail={selectedMail}
            onBack={() => setSelectedMail(null)}
            summary={summary}
            draft={draft}
          />
        ) : (
          <div className='text-muted-foreground flex h-full items-center justify-center'>
            Select an email to view
          </div>
        )}
      </div>
    </div>
  );
}
