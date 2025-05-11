export interface MailSender {
  name: string;
  email: string;
}

export interface MailItem {
  id: string;
  originalMessageId: string;
  threadId: string;
  sender: MailSender;
  subject: string;
  snippet: string;
  date: Date;
  content?: string;
}
