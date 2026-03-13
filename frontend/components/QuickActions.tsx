"use client";

import Link from "next/link";

interface ActionCard {
  href: string;
  title: string;
  description: string;
  icon: React.ReactNode;
}

export default function QuickActions() {
  const actions: ActionCard[] = [
    {
      href: "/urls/add",
      title: "Add URL",
      description: "Add a webpage to your knowledge base",
      icon: (
        <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 4v16m8-8H4" />
        </svg>
      ),
    },
    {
      href: "/urls/list",
      title: "Manage URLs",
      description: "View and manage all submitted URLs",
      icon: (
        <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
        </svg>
      ),
    },
    {
      href: "/knowledge/build",
      title: "Build Knowledge Base",
      description: "Process URLs and generate embeddings",
      icon: (
        <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
        </svg>
      ),
    },
    {
      href: "/chat",
      title: "Ask Questions",
      description: "Chat with your knowledge base",
      icon: (
        <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-10">
      {actions.map((action) => (
        <Link
          key={action.title}
          href={action.href}
          className="bg-white border border-slate-200 rounded-2xl p-6 cursor-pointer hover:shadow-md hover:-translate-y-0.5 transition"
        >
          <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center text-slate-700 mb-3">
            {action.icon}
          </div>
          <h3 className="font-medium text-slate-800 mb-1">{action.title}</h3>
          <p className="text-sm text-slate-500">{action.description}</p>
        </Link>
      ))}
    </div>
  );
}
