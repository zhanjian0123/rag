"use client";

import Sidebar from "@/components/Sidebar";
import DashboardHeader from "@/components/DashboardHeader";
import StatsCards from "@/components/StatsCards";
import QuickActions from "@/components/QuickActions";
import SystemStatus from "@/components/SystemStatus";

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Sidebar />

      {/* Main content area - centered */}
      <main className="ml-64 min-h-screen">
        <div className="max-w-6xl mx-auto px-6 py-10">
          <DashboardHeader />

          <div className="space-y-6">
            {/* Statistics Section */}
            <StatsCards />

            {/* Quick Actions Section */}
            <QuickActions />

            {/* System Status Section */}
            <SystemStatus />
          </div>
        </div>
      </main>
    </div>
  );
}
