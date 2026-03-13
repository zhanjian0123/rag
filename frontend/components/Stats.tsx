"use client";

import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/Card";

interface StatsData {
  total_urls: number;
  processed_urls: number;
  vector_documents: number;
  bm25_documents: number;
}

const statItems = [
  { key: "total_urls", label: "总 URL", icon: "🔗", color: "text-blue-600" },
  { key: "processed_urls", label: "已处理", icon: "✅", color: "text-green-600" },
  { key: "vector_documents", label: "向量文档", icon: "📊", color: "text-purple-600" },
  { key: "bm25_documents", label: "索引文档", icon: "📚", color: "text-orange-600" },
];

export default function Stats() {
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
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="py-4">
              <div className="h-3 bg-slate-100 rounded w-16 mb-2"></div>
              <div className="h-6 bg-slate-100 rounded w-12"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 animate-slide-up">
      {statItems.map((item) => (
        <Card key={item.key} className="card-hover">
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-500 mb-1.5">{item.label}</p>
                <p className="text-2xl font-semibold text-slate-900">
                  {stats?.[item.key as keyof StatsData] || 0}
                </p>
              </div>
              <div className={`w-9 h-9 bg-slate-50 rounded-md flex items-center justify-center`}>
                <span className="text-base">{item.icon}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
