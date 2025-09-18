'use client';

import { useParams } from 'next/navigation';
import ChatPage from '@/components/chat-page/chat-page';
import { SIDEBAR_ITEMS_DATA } from '@/components/sidebar/sidebar-items';

export default function ProjectPage() {
  const { project } = useParams<{ project: string }>();

  // Find the project in the database
  const goal = SIDEBAR_ITEMS_DATA.find((p) => p.title.toLowerCase() === project.toLowerCase());
  if (!goal) {
    return <div className="p-4">Project not found</div>;
  }
  return <ChatPage project={goal} />;
}