"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/Card";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    openai_api_key: "",
    openai_model: "gpt-3.5-turbo",
    dashscope_api_key: "",
    dashscope_model: "qwen-turbo",
    llm_provider: "openai",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch("/api/settings")
      .then((res) => res.json())
      .then((data) => setSettings(data))
      .catch(() => {});
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(settings),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error("保存失败", err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
          <span>⚙️</span>
          <span>系统设置</span>
        </h1>
        <p className="text-gray-500 mt-1">配置模型提供者和 API 密钥</p>
      </div>

      <Card className="animate-slide-up shadow-lg">
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <span className="text-lg">⚙️</span>
            </div>
            <div>
              <CardTitle>LLM 提供商</CardTitle>
              <p className="text-sm text-gray-500 mt-0.5">选择您要使用的语言模型</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              选择提供商
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setSettings({ ...settings, llm_provider: "openai" })}
                className={`p-4 border-2 rounded-xl transition-all duration-200 ${
                  settings.llm_provider === "openai"
                    ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
                    : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                }`}
              >
                <div className="text-2xl mb-1">🤖</div>
                <div className="font-medium">OpenAI</div>
                <div className="text-xs text-gray-500">GPT-3.5 / GPT-4</div>
              </button>
              <button
                type="button"
                onClick={() => setSettings({ ...settings, llm_provider: "dashscope" })}
                className={`p-4 border-2 rounded-xl transition-all duration-200 ${
                  settings.llm_provider === "dashscope"
                    ? "border-blue-500 bg-blue-50 ring-2 ring-blue-200"
                    : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                }`}
              >
                <div className="text-2xl mb-1">☁️</div>
                <div className="font-medium">DashScope</div>
                <div className="text-xs text-gray-500">通义千问系列</div>
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {settings.llm_provider === "openai" && (
        <Card className="animate-slide-up shadow-lg">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <span className="text-lg">🔑</span>
              </div>
              <div>
                <CardTitle>OpenAI 设置</CardTitle>
                <p className="text-sm text-gray-500 mt-0.5">配置 OpenAI API</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={settings.openai_api_key}
                onChange={(e) =>
                  setSettings({ ...settings, openai_api_key: e.target.value })
                }
                className="input"
                placeholder="sk-..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                模型
              </label>
              <select
                value={settings.openai_model}
                onChange={(e) =>
                  setSettings({ ...settings, openai_model: e.target.value })
                }
                className="input"
              >
                <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
                <option value="gpt-4">gpt-4</option>
                <option value="gpt-4-turbo">gpt-4-turbo</option>
              </select>
            </div>
          </CardContent>
        </Card>
      )}

      {settings.llm_provider === "dashscope" && (
        <Card className="animate-slide-up shadow-lg">
          <CardHeader>
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                <span className="text-lg">🔑</span>
              </div>
              <div>
                <CardTitle>DashScope 设置</CardTitle>
                <p className="text-sm text-gray-500 mt-0.5">配置阿里云通义千问 API</p>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={settings.dashscope_api_key}
                onChange={(e) =>
                  setSettings({ ...settings, dashscope_api_key: e.target.value })
                }
                className="input"
                placeholder="sk-..."
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                模型
              </label>
              <select
                value={settings.dashscope_model}
                onChange={(e) =>
                  setSettings({ ...settings, dashscope_model: e.target.value })
                }
                className="input"
              >
                <option value="qwen-turbo">qwen-turbo (快速)</option>
                <option value="qwen-plus">qwen-plus (增强)</option>
                <option value="qwen-max">qwen-max (最强)</option>
              </select>
            </div>
          </CardContent>
        </Card>
      )}

      <button
        onClick={handleSave}
        disabled={saving}
        className="btn btn-primary w-full flex items-center justify-center space-x-2 py-3"
      >
        {saving ? (
          <>
            <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <span>保存中...</span>
          </>
        ) : saved ? (
          <>
            <span>✅</span>
            <span>已保存</span>
          </>
        ) : (
          <>
            <span>💾</span>
            <span>保存设置</span>
          </>
        )}
      </button>
    </div>
  );
}
