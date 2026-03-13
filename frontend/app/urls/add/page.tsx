"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/Card";

export default function AddUrlPage() {
  const router = useRouter();
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/urls/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "添加失败");
      }

      router.push("/urls/list");
    } catch (err) {
      setError(err instanceof Error ? err.message : "添加失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl space-y-4">
        <div>
          <h1 className="text-lg font-semibold text-slate-900">添加 URL</h1>
          <p className="text-sm text-slate-500 mt-0.5">将网页内容提取并添加到知识库</p>
        </div>

        <Card hover={false}>
          <CardHeader>
            <div>
              <CardTitle>输入网页 URL</CardTitle>
              <CardDescription>支持任意公开网页，包括新闻、博客、论坛等</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="pt-4">
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2.5 rounded-md text-sm">
                  ⚠️ {error}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">
                  网页地址
                </label>
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com/article"
                  className="input"
                  required
                />
                <p className="text-xs text-slate-500 mt-1.5">
                  💡 输入完整的 URL 地址，包括 https:// 或 http://
                </p>
              </div>

              <button type="submit" disabled={loading} className="btn btn-primary w-full">
                {loading ? (
                  <span>提取中...</span>
                ) : (
                  <span>➕ 添加到知识库</span>
                )}
              </button>
            </form>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50/50 border-yellow-100" hover={false}>
          <CardContent className="py-3">
            <div className="flex items-start space-x-3">
              <div className="w-6 h-6 bg-yellow-100 rounded-md flex items-center justify-center flex-shrink-0">
                <span className="text-sm">💡</span>
              </div>
              <div>
                <h4 className="text-sm font-medium text-slate-900 mb-1">使用提示</h4>
                <ul className="text-xs text-slate-600 space-y-0.5">
                  <li>• 支持新闻文章、博客、技术文档等多种网页类型</li>
                  <li>• 系统会自动提取网页正文内容，忽略广告和导航</li>
                  <li>• 添加后可在"URL 管理"页面查看和管理</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
