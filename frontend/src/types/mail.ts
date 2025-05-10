export interface MailSender {
  name: string;
  email: string;
}

export interface MailItem {
  id: string;
  sender: MailSender;
  subject: string;
  isRead: boolean;
  date: Date;
  content?: string;
}
