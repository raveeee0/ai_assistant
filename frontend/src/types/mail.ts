export interface MailSender {
  name: string;
  email: string;
}

export interface MailItem {
  id: string;
  sender: MailSender;
  subject: string;
  preview: string;
  isRead: boolean;
  isStarred: boolean;
  date: Date;
  labels?: string[];
}

export interface Mail extends MailItem {
  content?: string;
  attachments?: {
    name: string;
    size: string;
    type: string;
    url: string;
  }[];
  recipients?: {
    to: MailSender[];
    cc?: MailSender[];
    bcc?: MailSender[];
  };
}
