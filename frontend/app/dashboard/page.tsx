"use client";

import DashboardLayout from "@/components/DashboardLayout";
import DashboardHeader from "@/components/DashboardHeader";
import StatsCards from "@/components/StatsCards";
import QuickActions from "@/components/QuickActions";
import SystemStatus from "@/components/SystemStatus";

export default function DashboardPage() {
  return (
    <DashboardLayout>
      <DashboardHeader />

      <div className="space-y-6">
        {/* Statistics Section */}
        <StatsCards />

        {/* Quick Actions Section */}
        <QuickActions />

        {/* System Status Section */}
        <SystemStatus />
      </div>
    </DashboardLayout>
  );
}
