"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "仪表盘" },
  { href: "/urls/add", label: "添加 URL" },
  { href: "/urls/list", label: "URL 管理" },
  { href: "/collections", label: "集合" },
  { href: "/knowledge/build", label: "知识库" },
  { href: "/chat", label: "智能问答" },
  { href: "/settings", label: "系统设置" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-slate-200 flex flex-col">
      {/* Logo */}
      <div className="h-14 flex items-center px-4 border-b border-slate-100">
        <Link href="/dashboard" className="text-sm font-semibold text-slate-800">
          Web RAG 知识库
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-0.5 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`
                block px-2.5 py-2 rounded-md text-sm font-medium
                transition-colors duration-150
                ${
                  isActive
                    ? "bg-slate-100 text-slate-900"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                }
              `}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Status indicator */}
      <div className="p-4 border-t border-slate-100">
        <div className="flex items-center space-x-2 text-xs text-slate-500">
          <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
          <span>系统运行中</span>
        </div>
      </div>
    </aside>
  );
}
