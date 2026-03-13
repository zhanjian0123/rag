"use client";

import { useEffect, useState } from "react";

interface StatsData {
  total_urls: number;
  processed_urls: number;
  vector_documents: number;
  bm25_documents: number;
}

export default function SystemStatus() {
  const [stats, setStats] = useState<StatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/knowledge/stats")
      .then((res) => res.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
      });
  }, []);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
        <span className="text-sm font-medium text-slate-700">系统状态：运行中</span>
      </div>
      {loading ? (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="text-center">
              <div className="h-6 bg-slate-100 rounded w-12 mx-auto mb-1 animate-pulse"></div>
              <div className="h-3 bg-slate-100 rounded w-16 mx-auto animate-pulse"></div>
            </div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-lg font-semibold text-slate-800">{stats?.total_urls || 0}</p>
            <p className="text-xs text-slate-500 mt-0.5">URL</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-semibold text-slate-800">{stats?.processed_urls || 0}</p>
            <p className="text-xs text-slate-500 mt-0.5">已处理</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-semibold text-slate-800">{stats?.vector_documents || 0}</p>
            <p className="text-xs text-slate-500 mt-0.5">向量</p>
          </div>
          <div className="text-center">
            <p className="text-lg font-semibold text-slate-800">{stats?.bm25_documents || 0}</p>
            <p className="text-xs text-slate-500 mt-0.5">索引</p>
          </div>
        </div>
      )}
    </div>
  );
}
