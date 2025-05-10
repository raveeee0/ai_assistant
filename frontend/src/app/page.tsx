import { Metadata } from 'next';
import MailClientLayout from '@/components/mail-client/layout';

export const metadata: Metadata = {
  title: 'Mail Client',
  description:
    'Modern mail client built with Next.js, Shadcn UI and Tailwind CSS'
};

export default async function Page() {
  return <MailClientLayout />;
}
