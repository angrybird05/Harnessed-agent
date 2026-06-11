"use client";

import { useEffect, useState, useCallback } from "react";
import StatusBadge from "@/components/StatusBadge";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Application {
  id: number;
  user_id: number;
  job_id: number;
  status: string;
  match_score: number | null;
  created_at: string | null;
  applied_at: string | null;
  followup_count: number;
  job_title: string | null;
  job_company: string | null;
  job_location: string | null;
  job_url: string | null;
  is_remote: boolean | null;
}

const STATUS_OPTIONS = [
  "all",
  "pending",
  "outreach_sent",
  "applied",
  "interview_scheduled",
  "request_for_info",
  "rejected",
  "no_reply",
  "selected",
  "withdrawn",
];

export default function ApplicationsPage() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [withdrawingId, setWithdrawingId] = useState<number | null>(null);

  // MED-03: Wrap in useCallback so it can be correctly listed in useEffect deps
  const fetchApplications = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }

    const headers = { Authorization: `Bearer ${token}` };
    const params = new URLSearchParams();
    if (statusFilter !== "all") params.set("status", statusFilter);
    params.set("limit", "50");

    try {
      const res = await fetch(
        `${API_URL}/applications?${params.toString()}`,
        { headers }
      );
      // MED-02: Redirect to login on auth error
      if (res.status === 401) { window.location.href = "/login"; return; }
      const data = await res.json();
      setApplications(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    fetchApplications();
  }, [fetchApplications]);

  const handleWithdraw = async (applicationId: number) => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    setWithdrawingId(applicationId);
    try {
      await fetch(`${API_URL}/applications/${applicationId}/withdraw`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      await fetchApplications();
    } catch (err) {
      console.error(err);
    } finally {
      setWithdrawingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-surface-200 bg-clip-text text-transparent">
          Applications
        </h1>
        <p className="text-surface-200 mt-1">
          Track and manage your job applications
        </p>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-2 flex-wrap">
        {STATUS_OPTIONS.map((s) => (
          <button
            key={s}
            onClick={() => setStatusFilter(s)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 ${
              statusFilter === s
                ? "bg-primary-500/20 text-primary-300 border border-primary-500/30"
                : "bg-white/5 text-surface-200 border border-white/10 hover:bg-white/10"
            }`}
          >
            {s === "all" ? "All" : s.replace(/_/g, " ")}
          </button>
        ))}
      </div>

      {/* Table */}
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
                <th className="text-left px-6 py-4 text-xs font-semibold text-surface-200 uppercase tracking-wider">
                  Actions
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
                    <div className="flex items-center gap-2">
                      <span>{app.job_title || "—"}</span>
                      {app.is_remote && (
                        <span className="px-1.5 py-0.5 text-[10px] font-semibold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          REMOTE
                        </span>
                      )}
                    </div>
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
                  <td className="px-6 py-4">
                    {app.status !== "withdrawn" &&
                      app.status !== "selected" &&
                      app.status !== "rejected" && (
                        <button
                          onClick={() => handleWithdraw(app.id)}
                          disabled={withdrawingId === app.id}
                          className="btn-danger text-xs disabled:opacity-50"
                        >
                          {withdrawingId === app.id
                            ? "Withdrawing..."
                            : "Withdraw"}
                        </button>
                      )}
                  </td>
                </tr>
              ))}
              {applications.length === 0 && (
                <tr>
                  <td
                    colSpan={6}
                    className="px-6 py-12 text-center text-surface-200"
                  >
                    No applications found
                    {statusFilter !== "all" && " for this filter"}.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
