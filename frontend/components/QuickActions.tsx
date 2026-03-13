"use client";

import Link from "next/link";

interface ActionCard {
  href: string;
  title: string;
  description: string;
}

export default function QuickActions() {
  const actions: ActionCard[] = [
    {
      href: "/urls/add",
      title: "添加 URL",
      description: "将网页添加到知识库",
    },
    {
      href: "/urls/list",
      title: "管理 URL",
      description: "查看和管理所有 URL",
    },
    {
      href: "/knowledge/build",
      title: "构建知识库",
      description: "处理 URL 并生成向量",
    },
    {
      href: "/chat",
      title: "智能问答",
      description: "与知识库对话",
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
          <h3 className="font-medium text-slate-800 mb-1">{action.title}</h3>
          <p className="text-sm text-slate-500">{action.description}</p>
        </Link>
      ))}
    </div>
  );
}
