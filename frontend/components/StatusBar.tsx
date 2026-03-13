"use client";

import { useState, useEffect } from "react";

interface StatsData {
  total_urls: number;
  processed_urls: number;
  vector_documents: number;
  bm25_documents: number;
}

export default function StatusBar() {
  const [stats, setStats] = useState<StatsData>({
    total_urls: 0,
    processed_urls: 0,
    vector_documents: 0,
    bm25_documents: 0,
  });
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
    <footer className="hidden lg:flex items-center justify-between h-10 px-4 bg-white border-t border-slate-200 text-xs text-slate-500">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5">
          <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
          <span>就绪</span>
        </div>
        <div className="w-px h-3 bg-slate-200"></div>
        <div className="flex items-center space-x-1">
          <span className="text-slate-400">URL:</span>
          {loading ? (
            <span className="w-8 h-4 bg-slate-100 rounded animate-pulse"></span>
          ) : (
            <span className="font-medium text-slate-700">{stats.total_urls}</span>
          )}
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-slate-400">已处理:</span>
          {loading ? (
            <span className="w-8 h-4 bg-slate-100 rounded animate-pulse"></span>
          ) : (
            <span className="font-medium text-slate-700">{stats.processed_urls}</span>
          )}
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-slate-400">向量:</span>
          {loading ? (
            <span className="w-8 h-4 bg-slate-100 rounded animate-pulse"></span>
          ) : (
            <span className="font-medium text-slate-700">{stats.vector_documents}</span>
          )}
        </div>
        <div className="flex items-center space-x-1">
          <span className="text-slate-400">索引:</span>
          {loading ? (
            <span className="w-8 h-4 bg-slate-100 rounded animate-pulse"></span>
          ) : (
            <span className="font-medium text-slate-700">{stats.bm25_documents}</span>
          )}
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <span className="text-slate-400">Web RAG v1.0.0</span>
        <a
          href="/docs"
          className="text-slate-400 hover:text-slate-600 transition-colors"
          target="_blank"
          rel="noopener noreferrer"
        >
          文档
        </a>
      </div>
    </footer>
  );
}
