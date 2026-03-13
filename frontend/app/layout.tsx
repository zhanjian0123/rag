import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import StatusBar from "@/components/StatusBar";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Web RAG 知识库系统",
  description: "基于通用网页内容提取的知识库系统",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </head>
      <body className={`${inter.className} antialiased bg-slate-50`}>
        <div className="flex min-h-screen">
          {/* 左侧侧边栏 */}
          <Sidebar />

          {/* 主内容区域 */}
          <div className="flex-1 flex flex-col">
            {/* 主内容 */}
            <main className="flex-1 pt-14 lg:pt-0 lg:pl-64">
              <div className="p-4 sm:p-6 lg:p-8">
                {children}
              </div>
            </main>

            {/* 底部状态栏 */}
            <StatusBar />
          </div>
        </div>
      </body>
    </html>
  );
}
