"use client";

import { useEffect, useState } from "react";
import JobCard from "@/components/JobCard";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Job {
  id: number;
  title: string;
  company: string | null;
  location: string | null;
  job_url: string | null;
  is_remote: boolean;
  salary_min: number | null;
  salary_max: number | null;
  seniority_level: string | null;
  source: string | null;
  fetched_at: string | null;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [discovering, setDiscovering] = useState(false);
  const [discoverMessage, setDiscoverMessage] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }

    fetch(`${API_URL}/jobs?limit=40`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.json())
      .then((data) => setJobs(Array.isArray(data) ? data : []))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleDiscover = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) return;

    setDiscovering(true);
    setDiscoverMessage("");

    try {
      const res = await fetch(`${API_URL}/jobs/discover`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setDiscoverMessage(data.message || "Discovery task started!");
    } catch (err) {
      setDiscoverMessage("Failed to start discovery task.");
      console.error(err);
    } finally {
      setDiscovering(false);
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
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-white to-surface-200 bg-clip-text text-transparent">
            Job Listings
          </h1>
          <p className="text-surface-200 mt-1">
            Discover and browse matching opportunities
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <button
            onClick={handleDiscover}
            disabled={discovering}
            className="btn-primary disabled:opacity-50"
          >
            {discovering ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Discovering...
              </span>
            ) : (
              "🔍 Discover Jobs"
            )}
          </button>
          {discoverMessage && (
            <p className="text-xs text-primary-300">{discoverMessage}</p>
          )}
        </div>
      </div>

      {jobs.length === 0 ? (
        <div className="glass-card p-12 text-center">
          <div className="text-4xl mb-4">🔎</div>
          <h3 className="text-lg font-semibold mb-2">No jobs found yet</h3>
          <p className="text-surface-200 text-sm mb-4">
            Click &quot;Discover Jobs&quot; to start finding opportunities that
            match your profile.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {jobs.map((job) => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      )}
    </div>
  );
}
