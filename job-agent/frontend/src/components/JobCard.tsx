interface JobCardProps {
  job: {
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
  };
}

export default function JobCard({ job }: JobCardProps) {
  const formatSalary = (min: number | null, max: number | null) => {
    if (!min && !max) return null;
    const fmt = (n: number) =>
      `$${(n / 1000).toFixed(0)}k`;
    if (min && max) return `${fmt(min)} - ${fmt(max)}`;
    if (min) return `From ${fmt(min)}`;
    return `Up to ${fmt(max!)}`;
  };

  const salary = formatSalary(job.salary_min, job.salary_max);

  return (
    <div className="glass-card-hover p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white truncate" title={job.title}>
            {job.title}
          </h3>
          <p className="text-sm text-surface-200 truncate">
            {job.company || "Unknown Company"}
          </p>
        </div>
        {job.is_remote && (
          <span className="shrink-0 px-2 py-0.5 text-[10px] font-bold rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            REMOTE
          </span>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-2 text-xs text-surface-200">
        {job.location && (
          <span className="flex items-center gap-1">
            📍 {job.location}
          </span>
        )}
        {job.seniority_level && (
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 capitalize">
            {job.seniority_level}
          </span>
        )}
        {job.source && (
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/10 uppercase text-[10px]">
            {job.source}
          </span>
        )}
      </div>

      {salary && (
        <p className="text-sm font-medium text-primary-300">{salary}</p>
      )}

      <div className="flex items-center gap-2 mt-auto pt-2 border-t border-white/5">
        {job.job_url && (
          <a
            href={job.job_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-secondary text-xs flex-1 text-center"
          >
            View Job →
          </a>
        )}
      </div>
    </div>
  );
}
