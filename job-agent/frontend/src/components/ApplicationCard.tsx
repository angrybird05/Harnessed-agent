import StatusBadge from "./StatusBadge";

interface ApplicationCardProps {
  application: {
    id: number;
    status: string;
    match_score: number | null;
    created_at: string | null;
    job_title: string | null;
    job_company: string | null;
    job_location: string | null;
    is_remote: boolean | null;
    followup_count: number;
  };
  onWithdraw?: (id: number) => void;
}

export default function ApplicationCard({
  application,
  onWithdraw,
}: ApplicationCardProps) {
  const canWithdraw =
    application.status !== "withdrawn" &&
    application.status !== "selected" &&
    application.status !== "rejected";

  return (
    <div className="glass-card-hover p-5 flex flex-col gap-3">
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white truncate">
            {application.job_title || "Unknown Role"}
          </h3>
          <p className="text-sm text-surface-200">
            {application.job_company || "Unknown Company"}
          </p>
        </div>
        <StatusBadge status={application.status} />
      </div>

      <div className="flex items-center gap-3 text-xs text-surface-200">
        {application.job_location && (
          <span>📍 {application.job_location}</span>
        )}
        {application.is_remote && (
          <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-semibold">
            REMOTE
          </span>
        )}
      </div>

      <div className="flex items-center justify-between text-xs">
        {application.match_score !== null && (
          <div className="flex items-center gap-2">
            <span className="text-surface-200">Match:</span>
            <span
              className={`font-bold ${
                application.match_score >= 80
                  ? "text-emerald-400"
                  : application.match_score >= 60
                  ? "text-amber-400"
                  : "text-red-400"
              }`}
            >
              {application.match_score}%
            </span>
          </div>
        )}
        {application.followup_count > 0 && (
          <span className="text-surface-200">
            Follow-ups: {application.followup_count}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between mt-auto pt-2 border-t border-white/5">
        <span className="text-[11px] text-surface-200">
          {application.created_at
            ? new Date(application.created_at).toLocaleDateString()
            : "—"}
        </span>
        {canWithdraw && onWithdraw && (
          <button
            onClick={() => onWithdraw(application.id)}
            className="btn-danger text-xs"
          >
            Withdraw
          </button>
        )}
      </div>
    </div>
  );
}
