"use client";

import { useState, useEffect } from "react";
import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";

interface Collection {
  id: number;
  name: string;
  description: string;
  url_count: number;
}

export default function CollectionListPage() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [collections, setCollections] = useState<Collection[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/knowledge/collections")
      .then((res) => res.json())
      .then((data) => {
        setCollections(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch("/api/knowledge/collections", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, description }),
      });
      if (res.ok) {
        const newCollection = await res.json();
        setCollections([...collections, { ...newCollection, url_count: 0 }]);
        setName("");
        setDescription("");
      }
    } catch (err) {
      console.error("创建失败", err);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
      <div className="max-w-4xl space-y-3">
        {[1, 2].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="py-6">
              <div className="h-4 bg-slate-100 rounded w-1/3 mb-2"></div>
              <div className="h-3 bg-slate-100 rounded w-2/3"></div>
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
      <div>
        <h1 className="text-lg font-semibold text-slate-900">集合管理</h1>
        <p className="text-sm text-slate-500 mt-0.5">创建和管理知识集合</p>
      </div>

      <Card hover={false}>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-50 rounded-md flex items-center justify-center">
              <span className="text-lg">📁</span>
            </div>
            <div>
              <CardTitle>创建新集合</CardTitle>
              <p className="text-xs text-slate-500 mt-0.5">为您的知识创建分组</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreate} className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                集合名称
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="input"
                placeholder="例如：技术文档、产品资讯"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                描述 <span className="text-slate-400 font-normal">(可选)</span>
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="input"
                rows={2}
                placeholder="描述这个集合的用途..."
              />
            </div>
            <button type="submit" className="btn btn-primary">
              ➕ 创建集合
            </button>
          </form>
        </CardContent>
      </Card>

      {collections.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {collections.map((col) => (
            <Card key={col.id} className="card-hover group cursor-pointer">
              <CardContent className="py-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-md flex items-center justify-center text-white shadow-sm">
                      📚
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-slate-900">{col.name}</h3>
                      <p className="text-xs text-slate-500 mt-0.5">{col.url_count} 个 URL</p>
                    </div>
                  </div>
                </div>
                {col.description && (
                  <p className="text-xs text-slate-600 mt-3 pt-3 border-t border-slate-100">
                    {col.description}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card hover={false}>
          <CardContent className="py-12 text-center">
            <div className="w-12 h-12 mx-auto bg-slate-100 rounded-full flex items-center justify-center mb-3">
              <span className="text-xl">📂</span>
            </div>
            <p className="text-sm text-slate-500">暂无集合</p>
          </CardContent>
        </Card>
      )}
    </div>
    </DashboardLayout>
  );
}
