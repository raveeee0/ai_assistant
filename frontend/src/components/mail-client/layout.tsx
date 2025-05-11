'use client';

import { useEffect, useState } from 'react';
import Sidebar from './sidebar';
import { MailItem } from '@/types/mail';
import MailList from './mail-list';
import MailView from './mail-view';
import { cn } from '@/lib/utils';
import { Request } from '@/types/utils';
import { set } from 'date-fns';

export default function MailClientLayout() {
  const [mails, setMails] = useState<MailItem[]>([]);
  const [isLoadingMails, setIsLoadingMails] = useState<boolean>(true); // Added loading state
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
    setIsLoadingMails(true); // Set loading to true when starting to fetch

    fetch('http://127.0.0.1:8000/unread-mails')
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Failed to fetch mails');
      })
      .then((data) => {
        const formattedMails = data.messages.map(
          (mail: {
            message_id: string;
            original_message_id: string;
            thread_id: string;
            senderName: string;
            senderEmail: string;
            subject: string;
            snippet: string;
            date: string | number | Date;
            text: string;
          }) => ({
            id: mail.message_id,
            originalMessageId: mail.original_message_id,
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
      })
      .catch((error) => {
        console.error('Failed to fetch mails:', error);
      })
      .finally(() => {
        setIsLoadingMails(false); // Set loading to false when done
      });
  };

  useEffect(() => {
    if (selectedMail) {
      // Reset summary and draft when a new mail is selected
      setSummary({ isLoading: true, result: null, error: false });
      setDraft({ isLoading: true, result: null, error: false });

      const summarySocket = new WebSocket(
        `ws://localhost:8000/summary/${selectedMail.id}/ws`
      );

      summarySocket.onmessage = (event) => {
        setSummary((old) => ({
          isLoading: true,
          result: (old.result || '') + event.data,
          error: false
        }));
      };

      summarySocket.onclose = () => {
        setSummary((old) => ({
          isLoading: false,
          result: old.result,
          error: false
        }));
      };
      summarySocket.onerror = (error) => {
        console.error('WebSocket error:', error);
        setSummary({
          isLoading: false,
          result: 'Error loading summary.',
          error: true
        });
      };

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
          isLoading={isLoadingMails}
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
        ) : isLoadingMails ? (
          <div className='text-muted-foreground flex h-full items-center justify-center'>
            Loading emails...
          </div>
        ) : (
          <div className='text-muted-foreground flex h-full items-center justify-center'>
            {mails.length > 0 ? 'Select an email to view' : 'No emails found'}
          </div>
        )}
      </div>
    </div>
  );
}
