"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";

const navItems = [
  { href: "/", label: "首页", icon: "🏠" },
  { href: "/urls/add", label: "添加 URL", icon: "➕" },
  { href: "/urls/list", label: "URL 管理", icon: "📋" },
  { href: "/collections", label: "集合", icon: "📁" },
  { href: "/knowledge/build", label: "知识库", icon: "🔨" },
  { href: "/chat", label: "问答", icon: "💬" },
  { href: "/settings", label: "设置", icon: "⚙️" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <>
      {/* 移动端遮罩层 */}
      {mobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* 侧边栏 */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-full w-64 bg-white border-r border-slate-200
          transform transition-transform duration-200 ease-in-out
          lg:translate-x-0 lg:static lg:h-screen
          ${mobileMenuOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Logo 区域 */}
        <div className="h-14 flex items-center px-4 border-b border-slate-100">
          <Link href="/" className="flex items-center space-x-2.5 group">
            <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-blue-600 rounded-md flex items-center justify-center shadow-sm">
              <span className="text-sm">📚</span>
            </div>
            <span className="text-sm font-semibold text-slate-900">Web RAG</span>
          </Link>
        </div>

        {/* 导航菜单 */}
        <nav className="p-3 space-y-0.5">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + "/");
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileMenuOpen(false)}
                className={`
                  flex items-center space-x-2.5 px-2.5 py-2 rounded-md text-sm font-medium
                  transition-all duration-150
                  ${
                    isActive
                      ? "bg-slate-100 text-slate-900"
                      : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                  }
                `}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* 底部信息 */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-100">
          <div className="flex items-center space-x-2 text-xs text-slate-500">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>系统运行正常</span>
          </div>
        </div>
      </aside>

      {/* 移动端顶部栏 */}
      <header className="lg:hidden fixed top-0 left-0 right-0 h-14 bg-white border-b border-slate-200 z-30 flex items-center justify-between px-4">
        <button
          onClick={() => setMobileMenuOpen(true)}
          className="p-2 -ml-2 text-slate-600 hover:bg-slate-100 rounded-md"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <Link href="/" className="flex items-center space-x-2">
          <div className="w-7 h-7 bg-gradient-to-br from-blue-500 to-blue-600 rounded-md flex items-center justify-center">
            <span className="text-sm">📚</span>
          </div>
          <span className="text-sm font-semibold text-slate-900">Web RAG</span>
        </Link>
        <div className="w-9"></div>
      </header>
    </>
  );
}
