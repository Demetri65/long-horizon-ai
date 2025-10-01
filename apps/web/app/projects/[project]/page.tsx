'use client';

import { useParams } from 'next/navigation';
import { SIDEBAR_ITEMS_DATA } from '@/components/sidebar/sidebar-items';
import { Chat } from '@/components/chat';

export default function ProjectPage() {
  const { project } = useParams<{ project: string }>();

  const goal = SIDEBAR_ITEMS_DATA.find((p) => p.title.toLowerCase() === project.toLowerCase());
  if (!goal) {
    return <div className="p-4">Project not found</div>;
  }
  return <Chat project={goal} />;
}