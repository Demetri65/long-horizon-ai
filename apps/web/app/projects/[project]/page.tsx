'use client';

import { useParams } from 'next/navigation';
import { projects } from '@/lib/projects';
import ChatPage from '@/components/chat-page/chat-page';

export default function ProjectPage() {
  const { project } = useParams<{ project: string }>();

  // Find the project in the database
  const goal = projects.find((p) => p.project === project);
  if (!project) {
    return <div className="p-4">Project not found</div>;
  }
  return <ChatPage project={goal} />;
}