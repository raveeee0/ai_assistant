'use client';

import { Button } from '@/components/ui/button';
import { ChevronDown } from 'lucide-react';
import { Avatar } from '@/components/ui/avatar';

interface HeaderProps {
  title: string;
}

export default function Header({ title }: HeaderProps) {
  return (
    <div className='bg-background flex h-12 items-center justify-between border-b px-4'>
      <div className='flex items-center'>
        <h1 className='text-lg font-semibold'>{title}</h1>
      </div>
      <div className='flex items-center gap-2'>
        <Avatar className='h-8 w-8'>
          <div className='bg-primary text-primary-foreground'>A</div>
        </Avatar>
        <Button variant='ghost' size='sm' className='gap-1'>
          Alicia Koch
          <ChevronDown size={14} />
        </Button>
      </div>
    </div>
  );
}
