"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent } from "@/components/Card";

interface URLItem {
  id: number;
  url: string;
  title: string | null;
  site_name: string | null;
  is_processed: boolean;
  created_at: string;
}

export default function UrlListPage() {
  const [urls, setUrls] = useState<URLItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/urls/list")
      .then((res) => res.json())
      .then((data) => {
        setUrls(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("确定要删除这个 URL 吗？")) return;

    try {
      const res = await fetch(`/api/urls/${id}`, { method: "DELETE" });
      if (res.ok) {
        setUrls(urls.filter((u) => u.id !== id));
      }
    } catch (err) {
      console.error("删除失败", err);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
      <div className="max-w-4xl space-y-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="py-4">
              <div className="h-4 bg-slate-100 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-slate-100 rounded w-1/2"></div>
            </CardContent>
          </Card>
        ))}
      </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
    <div className="max-w-4xl space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-slate-900">URL 管理</h1>
          <p className="text-sm text-slate-500 mt-0.5">管理已添加到知识库的网页</p>
        </div>
        <Link href="/urls/add" className="btn btn-primary">
          <span>➕</span>
          <span className="ml-1.5">添加 URL</span>
        </Link>
      </div>

      {urls.length === 0 ? (
        <Card className="py-12" hover={false}>
          <CardContent className="text-center">
            <div className="w-12 h-12 mx-auto bg-slate-100 rounded-full flex items-center justify-center mb-3">
              <span className="text-xl">📭</span>
            </div>
            <p className="text-sm text-slate-500 mb-4">暂无 URL，请先添加</p>
            <Link href="/urls/add" className="btn btn-primary inline-block">
              立即添加
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {urls.map((item) => (
            <Card key={item.id} className="card-hover">
              <CardContent className="py-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm font-medium text-blue-600 hover:text-blue-700 hover:underline truncate block"
                    >
                      {item.title || item.url}
                    </a>
                    <div className="flex items-center flex-wrap gap-2 mt-1.5">
                      <span className="inline-flex items-center px-2 py-0.5 bg-slate-100 rounded text-xs text-slate-600">
                        {item.site_name || "未知站点"}
                      </span>
                      <span className={`inline-flex items-center gap-1 text-xs ${
                        item.is_processed ? "text-green-600" : "text-yellow-600"
                      }`}>
                        <span>{item.is_processed ? "✅" : "⏳"}</span>
                        <span>{item.is_processed ? "已处理" : "未处理"}</span>
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(item.id)}
                    className="btn btn-secondary text-red-600 hover:bg-red-50 flex-shrink-0"
                  >
                    🗑️ 删除
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
    </DashboardLayout>
  );
}
