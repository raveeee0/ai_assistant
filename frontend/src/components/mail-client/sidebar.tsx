'use client';

import { Button } from '@/components/ui/button';
import {
  Inbox,
  Send,
  Archive,
  Trash2,
  Star,
  AlertCircle,
  PenSquare,
  ChevronDown,
  Users
} from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface NavItemProps {
  icon: React.ReactNode;
  label: string;
  isActive?: boolean;
  count?: number;
}

function NavItem({ icon, label, isActive, count }: NavItemProps) {
  return (
    <Button
      variant={isActive ? 'secondary' : 'ghost'}
      className={cn(
        'w-full justify-start gap-2 px-2',
        isActive ? 'font-medium' : 'font-normal'
      )}
    >
      {icon}
      <span className='flex-1 text-left'>{label}</span>
      {count !== undefined && (
        <span className='text-muted-foreground ml-auto text-xs'>{count}</span>
      )}
    </Button>
  );
}

export default function Sidebar() {
  return (
    <div className='bg-background flex h-full w-64 flex-col border-r'>
      {/* Navigation items */}
      <ScrollArea className='flex-1'>
        <div className='space-y-1 px-2 py-2'>
          <NavItem
            icon={<Inbox size={18} />}
            label='Inbox'
            isActive={true}
            count={128}
          />
          <NavItem icon={<Archive size={18} />} label='Drafts' count={9} />
          <NavItem icon={<Send size={18} />} label='Sent' />
          <NavItem icon={<Trash2 size={18} />} label='Junk' count={23} />
          <NavItem icon={<Trash2 size={18} />} label='Trash' />
          <NavItem icon={<Archive size={18} />} label='Archive' />
        </div>

        <div className='mt-6 px-4 py-2'>
          <div className='text-muted-foreground mb-2 flex items-center justify-between text-sm font-medium'>
            <span>Labels</span>
            <ChevronDown size={16} />
          </div>
          <div className='space-y-1'>
            <NavItem
              icon={<span className='h-2 w-2 rounded-full bg-red-500' />}
              label='Important'
            />
            <NavItem
              icon={<span className='h-2 w-2 rounded-full bg-green-500' />}
              label='Work'
            />
            <NavItem
              icon={<span className='h-2 w-2 rounded-full bg-blue-500' />}
              label='Personal'
            />
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
