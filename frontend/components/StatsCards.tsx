"use client";

import { useEffect, useState } from "react";

interface StatsData {
  total_urls: number;
  processed_urls: number;
  vector_documents: number;
  bm25_documents: number;
}

interface StatCardProps {
  label: string;
  value: number;
}

function StatCard({ label, value }: StatCardProps) {
  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md transition">
      <div>
        <p className="text-sm text-slate-500 mb-1">{label}</p>
        <p className="text-2xl font-semibold text-slate-800">{value.toLocaleString()}</p>
      </div>
    </div>
  );
}

export default function StatsCards() {
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

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white border border-slate-200 rounded-2xl p-6 animate-pulse"
          >
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <div className="h-3 bg-slate-100 rounded w-20"></div>
                <div className="h-7 bg-slate-100 rounded w-12"></div>
              </div>
              <div className="h-10 w-10 bg-slate-100 rounded-xl"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-10">
      <StatCard
        label="总 URL 数"
        value={stats?.total_urls || 0}
      />
      <StatCard
        label="已处理 URL"
        value={stats?.processed_urls || 0}
      />
      <StatCard
        label="向量文档"
        value={stats?.vector_documents || 0}
      />
      <StatCard
        label="索引文档"
        value={stats?.bm25_documents || 0}
      />
    </div>
  );
}
