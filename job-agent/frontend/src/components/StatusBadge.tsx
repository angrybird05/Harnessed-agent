interface StatusBadgeProps {
  status: string;
}

const STATUS_STYLES: Record<string, string> = {
  pending: "bg-gray-500/10 text-gray-400 border-gray-500/20",
  outreach_sent: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  applied: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  interview_scheduled: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  request_for_info: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  rejected: "bg-red-500/10 text-red-400 border-red-500/20",
  no_reply: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  selected: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  withdrawn: "bg-gray-500/10 text-gray-500 border-gray-500/20",
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const style =
    STATUS_STYLES[status] ||
    "bg-gray-500/10 text-gray-400 border-gray-500/20";

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 rounded-lg text-[11px] font-semibold uppercase tracking-wide border ${style}`}
    >
      {status.replace(/_/g, " ")}
    </span>
  );
}
