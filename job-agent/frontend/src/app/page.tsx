"use client";

import { useEffect, useState } from "react";
import StatsBar from "@/components/StatsBar";
// MED-05: Removed unused ApplicationCard import
import StatusBadge from "@/components/StatusBadge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Stats {
  total_applications: number;
  outreach_sent: number;
  applied_direct: number;
  interviews_scheduled: number;
  rejected: number;
  no_reply: number;
  response_rate: number;
  avg_match_score: number;
  applications_this_week: number;
}

interface Application {
  id: number;
  status: string;
  match_score: number | null;
  created_at: string | null;
  job_title: string | null;
  job_company: string | null;
  job_location: string | null;
  is_remote: boolean | null;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }

    const headers = { Authorization: `Bearer ${token}` };

    Promise.all([
      fetch(`${API_URL}/dashboard/stats`, { headers }).then((r) => {
        // MED-02: Redirect to login on auth errors instead of silently failing
        if (r.status === 401) { window.location.href = "/login"; return null; }
        return r.json();
      }),
      fetch(`${API_URL}/applications?limit=10`, { headers }).then((r) => {
        if (r.status === 401) { window.location.href = "/login"; return null; }
        return r.json();
      }),
    ])
      .then(([statsData, appsData]) => {
        if (!statsData || !appsData) return; // redirect already triggered
        setStats(statsData);
        setApplications(Array.isArray(appsData) ? appsData : []);
      })
      .catch(() => { window.location.href = "/login"; })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-surface-200 bg-clip-text text-transparent">
          Dashboard
        </h1>
        <p className="text-surface-200 mt-1">
          Your job application pipeline at a glance
        </p>
      </div>

      {stats && <StatsBar stats={stats} />}

      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Applications</h2>
          <a href="/applications" className="btn-secondary text-xs">
            View All →
          </a>
        </div>
        <div className="glass-card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left px-6 py-4 text-xs font-semibold text-surface-200 uppercase tracking-wider">
                    Company
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-surface-200 uppercase tracking-wider">
                    Role
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-surface-200 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-surface-200 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="text-left px-6 py-4 text-xs font-semibold text-surface-200 uppercase tracking-wider">
                    Date
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {applications.map((app) => (
                  <tr
                    key={app.id}
                    className="hover:bg-white/[0.03] transition-colors"
                  >
                    <td className="px-6 py-4 font-medium">
                      {app.job_company || "—"}
                    </td>
                    <td className="px-6 py-4 text-surface-200">
                      {app.job_title || "—"}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={app.status} />
                    </td>
                    <td className="px-6 py-4">
                      {app.match_score !== null ? (
                        <span
                          className={`font-semibold ${
                            app.match_score >= 80
                              ? "text-emerald-400"
                              : app.match_score >= 60
                              ? "text-amber-400"
                              : "text-red-400"
                          }`}
                        >
                          {app.match_score}%
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-6 py-4 text-surface-200">
                      {app.created_at
                        ? new Date(app.created_at).toLocaleDateString()
                        : "—"}
                    </td>
                  </tr>
                ))}
                {applications.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-6 py-12 text-center text-surface-200"
                    >
                      No applications yet. Go to{" "}
                      <a
                        href="/jobs"
                        className="text-primary-400 hover:underline"
                      >
                        Jobs
                      </a>{" "}
                      to start discovering opportunities.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
