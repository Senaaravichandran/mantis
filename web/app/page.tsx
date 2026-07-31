"use client";

import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { analyticsAPI, alertsAPI } from "@/lib/api-client";
import { useMantisStore } from "@/lib/store";
import { useEffect, useState, useRef } from "react";
import { formatDateTime, getSeverityColor } from "@/lib/utils";
import Link from "next/link";

function useCountUp(target: number, duration = 1200) {
  const [count, setCount] = useState(0);
  const prevTarget = useRef(0);

  useEffect(() => {
    if (target === prevTarget.current) return;
    prevTarget.current = target;
    const start = 0;
    const startTime = performance.now();
    const animate = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setCount(Math.round(start + (target - start) * eased));
      if (progress < 1) requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  }, [target, duration]);

  return count;
}

export default function DashboardPage() {
  const setAlertCount = useMantisStore((s) => s.setAlertCount);

  const { data: dashboard } = useQuery({
    queryKey: ["dashboard"],
    queryFn: () => analyticsAPI.dashboard(),
  });

  const { data: recentAlerts } = useQuery({
    queryKey: ["alerts", "recent"],
    queryFn: () => alertsAPI.list({ page_size: "5", resolved: "false" }),
  });

  useEffect(() => {
    if (dashboard?.stats?.active_alerts !== undefined) {
      setAlertCount(dashboard.stats.active_alerts);
    }
  }, [dashboard, setAlertCount]);

  const stats = dashboard?.stats || {};
  const riskDist = dashboard?.risk_distribution || {};

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="animate-fade-in-up">
        <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-sm text-gray-500 mt-1">Real-time overview of your infrastructure health</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4 stagger-children">
        <KPICard
          title="Total Assets"
          value={stats.total_assets || 0}
          subtitle="infrastructure assets monitored"
          icon={<AssetIcon />}
          color="blue"
          href="/assets"
        />
        <KPICard
          title="Active Alerts"
          value={stats.active_alerts || 0}
          subtitle="unresolved alerts"
          icon={<AlertIcon />}
          color="amber"
          href="/alerts"
          pulse={stats.active_alerts > 0}
        />
        <KPICard
          title="Pending Work Orders"
          value={stats.pending_work_orders || 0}
          subtitle="awaiting approval"
          icon={<WorkOrderIcon />}
          color="purple"
          href="/workorders"
        />
        <KPICard
          title="Avg Health Score"
          value={stats.avg_health_score || 0}
          subtitle="across all assets"
          icon={<HealthIcon />}
          color="green"
          isScore
        />
      </div>

      {/* Risk Distribution + Recent Alerts */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2 stagger-children" style={{ animationDelay: "300ms" }}>
        {/* Risk Distribution */}
        <Card className="overflow-hidden">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Risk Distribution</CardTitle>
              <Link href="/assets" className="text-xs text-mantis-600 hover:text-mantis-700 font-medium transition-colors">
                View all →
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <AnimatedRiskBar label="Low" count={riskDist.low || 0} total={stats.total_assets || 1} color="bg-emerald-500" textColor="text-emerald-700" delay={0} />
              <AnimatedRiskBar label="Medium" count={riskDist.medium || 0} total={stats.total_assets || 1} color="bg-amber-500" textColor="text-amber-700" delay={100} />
              <AnimatedRiskBar label="High" count={riskDist.high || 0} total={stats.total_assets || 1} color="bg-red-500" textColor="text-red-700" delay={200} />
              <AnimatedRiskBar label="Critical" count={riskDist.critical || 0} total={stats.total_assets || 1} color="bg-red-700" textColor="text-red-800" delay={300} />
            </div>
            {/* Summary bar */}
            <div className="mt-5 flex h-3 rounded-full overflow-hidden bg-gray-100">
              {[
                { key: "low", count: riskDist.low || 0, color: "bg-emerald-500" },
                { key: "medium", count: riskDist.medium || 0, color: "bg-amber-500" },
                { key: "high", count: riskDist.high || 0, color: "bg-red-500" },
                { key: "critical", count: riskDist.critical || 0, color: "bg-red-700" },
              ].map((seg) => (
                <div
                  key={seg.key}
                  className={`${seg.color} animate-bar-grow transition-all duration-700`}
                  style={{ width: `${(seg.count / (stats.total_assets || 1)) * 100}%` }}
                  title={`${seg.key}: ${seg.count}`}
                />
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Alerts */}
        <Card className="overflow-hidden">
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Alerts</CardTitle>
              <Link href="/alerts" className="text-xs text-mantis-600 hover:text-mantis-700 font-medium transition-colors">
                View all →
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {recentAlerts?.items?.map((alert: any, i: number) => (
                <Link
                  key={alert.id}
                  href={`/alerts/${alert.id}`}
                  className="flex items-start gap-3 rounded-lg border border-transparent p-3 hover:bg-gray-50 hover:border-gray-200 transition-all duration-200 group"
                  style={{ animationDelay: `${i * 80}ms` }}
                >
                  <div className="relative mt-0.5">
                    <Badge className={getSeverityColor(alert.severity)}>{alert.severity}</Badge>
                    {alert.severity === "critical" && (
                      <span className="absolute -top-1 -right-1 h-2.5 w-2.5 rounded-full bg-red-500 animate-pulse" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate group-hover:text-mantis-700 transition-colors">{alert.title}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{formatDateTime(alert.detected_at)}</p>
                  </div>
                  <svg className="w-4 h-4 text-gray-300 group-hover:text-mantis-500 transition-all group-hover:translate-x-0.5 mt-1 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Link>
              )) || <p className="text-sm text-gray-500 py-4 text-center">No recent alerts</p>}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Assets by Type + Quick Stats */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card className="lg:col-span-2 overflow-hidden">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Assets by Type</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4 stagger-children">
              {dashboard?.asset_type_counts?.map((item: any) => (
                <Link
                  key={item.asset_type}
                  href={`/assets?type=${item.asset_type}`}
                  className="group rounded-xl border border-gray-100 bg-gradient-to-br from-white to-gray-50/50 p-4 text-center hover:border-mantis-200 hover:shadow-md transition-all duration-300 hover:-translate-y-0.5"
                >
                  <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-lg bg-mantis-50 text-mantis-600 group-hover:bg-mantis-100 transition-colors">
                    {getAssetTypeIcon(item.asset_type)}
                  </div>
                  <p className="text-2xl font-bold text-gray-900 group-hover:text-mantis-700 transition-colors">{item.count}</p>
                  <p className="text-xs text-gray-500 capitalize mt-0.5">{item.asset_type.replace("_", " ")}</p>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card className="overflow-hidden">
          <CardHeader className="pb-3">
            <CardTitle className="text-base">System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <StatusRow label="API Service" status="online" />
              <StatusRow label="Agent Pipeline" status="online" />
              <StatusRow label="Kafka Streaming" status="online" />
              <StatusRow label="ML Anomaly Detection" status="online" />
              <StatusRow label="Ollama LLM" status="online" />
              <StatusRow label="Vector Database" status="online" />
            </div>
            <div className="mt-4 pt-3 border-t border-gray-100">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs text-gray-500">All systems operational</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function KPICard({
  title, value, subtitle, icon, color, href, pulse, isScore,
}: {
  title: string; value: number; subtitle: string;
  icon: React.ReactNode; color: string; href?: string;
  pulse?: boolean; isScore?: boolean;
}) {
  const animatedValue = useCountUp(value);

  const colorClasses: Record<string, { bg: string; border: string; iconBg: string; text: string }> = {
    blue:   { bg: "from-blue-50 to-white",   border: "border-blue-100",   iconBg: "bg-blue-100 text-blue-600",   text: "text-blue-700" },
    amber:  { bg: "from-amber-50 to-white",  border: "border-amber-100",  iconBg: "bg-amber-100 text-amber-600",  text: "text-amber-700" },
    purple: { bg: "from-purple-50 to-white",  border: "border-purple-100", iconBg: "bg-purple-100 text-purple-600", text: "text-purple-700" },
    green:  { bg: "from-emerald-50 to-white", border: "border-emerald-100",iconBg: "bg-emerald-100 text-emerald-600", text: "text-emerald-700" },
  };
  const c = colorClasses[color] || colorClasses.blue;

  const content = (
    <Card className={`bg-gradient-to-br ${c.bg} ${c.border} overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1 ${href ? "cursor-pointer" : ""} group`}>
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-500">{title}</p>
            <div className="flex items-baseline gap-1 mt-1.5">
              <p className={`text-3xl font-bold tabular-nums ${pulse ? "text-amber-600" : "text-gray-900"}`}>
                {animatedValue}
              </p>
              {isScore && <span className="text-lg text-gray-400">/100</span>}
            </div>
            <p className="text-xs text-gray-400 mt-1.5">{subtitle}</p>
          </div>
          <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${c.iconBg} transition-transform duration-300 group-hover:scale-110`}>
            {icon}
          </div>
        </div>
        {pulse && (
          <div className="mt-3 flex items-center gap-1.5">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-amber-500" />
            </span>
            <span className="text-xs text-amber-600 font-medium">Requires attention</span>
          </div>
        )}
        {href && (
          <div className="mt-3 flex items-center gap-1 text-xs font-medium text-gray-400 group-hover:text-mantis-600 transition-colors">
            <span>View details</span>
            <svg className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </div>
        )}
      </CardContent>
    </Card>
  );

  if (href) return <Link href={href}>{content}</Link>;
  return content;
}

function AnimatedRiskBar({
  label, count, total, color, textColor, delay,
}: {
  label: string; count: number; total: number; color: string; textColor: string; delay: number;
}) {
  const pct = Math.round((count / total) * 100);
  return (
    <div className="flex items-center gap-3 animate-fade-in-up" style={{ animationDelay: `${delay}ms` }}>
      <span className={`w-16 text-sm font-medium ${textColor}`}>{label}</span>
      <div className="flex-1 h-3 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full ${color} animate-bar-grow transition-all`}
          style={{ width: `${pct}%`, animationDelay: `${delay + 200}ms` }}
        />
      </div>
      <span className="w-10 text-right text-sm font-bold tabular-nums">{count}</span>
    </div>
  );
}

function StatusRow({ label, status }: { label: string; status: string }) {
  return (
    <div className="flex items-center justify-between py-1">
      <span className="text-sm text-gray-600">{label}</span>
      <div className="flex items-center gap-1.5">
        <div className={`h-1.5 w-1.5 rounded-full ${status === "online" ? "bg-emerald-500" : "bg-red-500"}`} />
        <span className={`text-xs font-medium ${status === "online" ? "text-emerald-600" : "text-red-600"}`}>
          {status === "online" ? "Online" : "Offline"}
        </span>
      </div>
    </div>
  );
}

function getAssetTypeIcon(type: string) {
  const icons: Record<string, React.ReactNode> = {
    bridge: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M3 17h18M5 17V9m14 8V9M9 17V5h6v12" /></svg>,
    water_main: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M12 3v18m-4-4c0 2.2 1.8 4 4 4s4-1.8 4-4c0-2.2-4-6-4-6s-4 3.8-4 6z" /></svg>,
    road: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 3L5 21M15 3l4 18M12 6v2m0 4v2m0 4v2" /></svg>,
    tunnel: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M4 20h16M6 20V10a6 6 0 0112 0v10" /></svg>,
    pump_station: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" /><path strokeLinecap="round" d="M12 1v4m0 14v4m-9-9h4m14 0h-4" /></svg>,
    culvert: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><ellipse cx="12" cy="12" rx="8" ry="4" /><path d="M4 12v4c0 2.2 3.6 4 8 4s8-1.8 8-4v-4" /></svg>,
    retention_basin: <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" d="M3 17c2-2 4 2 6 0s4 2 6 0 4 2 6 0M3 13c2-2 4 2 6 0s4 2 6 0 4 2 6 0M5 21V17M19 21V17" /></svg>,
  };
  return icons[type] || <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><rect x="4" y="4" width="16" height="16" rx="2" /></svg>;
}

function AssetIcon() {
  return <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" /></svg>;
}
function AlertIcon() {
  return <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 005.454-1.31A8.967 8.967 0 0118 9.75v-.7V9A6 6 0 006 9v.75a8.967 8.967 0 01-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 01-5.714 0m5.714 0a3 3 0 11-5.714 0" /></svg>;
}
function WorkOrderIcon() {
  return <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15a2.25 2.25 0 012.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V19.5a2.25 2.25 0 002.25 2.25h.75" /></svg>;
}
function HealthIcon() {
  return <svg className="w-5 h-5" fill="none" stroke="currentColor" strokeWidth={1.5} viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" /></svg>;
}
