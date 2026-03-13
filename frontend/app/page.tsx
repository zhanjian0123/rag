import Link from "next/link";
import { Card, CardContent, CardTitle, CardDescription } from "@/components/Card";
import Stats from "@/components/Stats";

const features = [
  {
    href: "/urls/add",
    title: "添加 URL",
    description: "添加单个网页 URL 到知识库",
    icon: "➕",
    color: "text-blue-600",
    bgColor: "bg-blue-50",
  },
  {
    href: "/urls/list",
    title: "URL 管理",
    description: "查看和管理已添加的 URL",
    icon: "📋",
    color: "text-green-600",
    bgColor: "bg-green-50",
  },
  {
    href: "/knowledge/build",
    title: "构建知识库",
    description: "将 URL 内容向量化构建知识库",
    icon: "🔨",
    color: "text-purple-600",
    bgColor: "bg-purple-50",
  },
  {
    href: "/chat",
    title: "智能问答",
    description: "基于知识库进行智能问答",
    icon: "💬",
    color: "text-orange-600",
    bgColor: "bg-orange-50",
  },
];

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Hero Section */}
      <section className="py-8 animate-fade-in">
        <div className="inline-flex items-center justify-center w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg mb-4 shadow-sm">
          <span className="text-xl">📚</span>
        </div>
        <h1 className="text-3xl font-semibold text-slate-900 mb-2 tracking-tight">
          Web RAG 知识库系统
        </h1>
        <p className="text-base text-slate-600 max-w-2xl">
          基于通用网页内容提取技术，智能构建您的个人知识库
        </p>
      </section>

      {/* Stats */}
      <Stats />

      {/* Quick Actions */}
      <section className="animate-slide-up">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">
              快速开始
            </h2>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {features.map((feature, index) => (
            <Link
              key={feature.href}
              href={feature.href}
              style={{ animationDelay: `${index * 0.05}s` }}
              className="group"
            >
              <Card className="h-full group-hover:border-slate-300 group-hover:shadow-md transition-all duration-200">
                <CardContent className="p-4">
                  <div className={`inline-flex items-center justify-center w-9 h-9 ${feature.bgColor} rounded-md mb-3`}>
                    <span className={`text-lg ${feature.color}`}>{feature.icon}</span>
                  </div>
                  <CardTitle className="text-sm font-medium text-slate-900 group-hover:text-blue-600 transition-colors">
                    {feature.title}
                  </CardTitle>
                  <CardDescription className="mt-1 text-xs text-slate-500 line-clamp-2">
                    {feature.description}
                  </CardDescription>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="animate-slide-up" style={{ animationDelay: '0.15s' }}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-slate-900 uppercase tracking-wide">
            核心特性
          </h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <Card className="p-4 card-hover">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-50 rounded-md flex items-center justify-center flex-shrink-0">
                <span className="text-lg">🌐</span>
              </div>
              <div>
                <h3 className="text-sm font-medium text-slate-900 mb-1">多源统一</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  支持任意公开网页，包括新闻、博客、论坛等，一键提取内容
                </p>
              </div>
            </div>
          </Card>
          <Card className="p-4 card-hover">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-50 rounded-md flex items-center justify-center flex-shrink-0">
                <span className="text-lg">🔗</span>
              </div>
              <div>
                <h3 className="text-sm font-medium text-slate-900 mb-1">一键入库</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  输入 URL 即可自动提取内容、入库存储、向量化处理
                </p>
              </div>
            </div>
          </Card>
          <Card className="p-4 card-hover">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-purple-50 rounded-md flex items-center justify-center flex-shrink-0">
                <span className="text-lg">🤖</span>
              </div>
              <div>
                <h3 className="text-sm font-medium text-slate-900 mb-1">智能问答</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  基于内容理解进行智能问答，提供准确的答案和参考来源
                </p>
              </div>
            </div>
          </Card>
        </div>
      </section>
    </div>
  );
}
