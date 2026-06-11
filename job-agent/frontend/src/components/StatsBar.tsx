interface StatsBarProps {
  stats: {
    total_applications: number;
    outreach_sent: number;
    applied_direct: number;
    interviews_scheduled: number;
    rejected: number;
    no_reply: number;
    response_rate: number;
    avg_match_score: number;
    applications_this_week: number;
  };
}

const STAT_CARDS = [
  {
    key: "total_applications" as const,
    label: "Total Applications",
    icon: "📊",
    gradient: "from-primary-400/20 to-primary-600/10",
    textColor: "text-primary-300",
  },
  {
    key: "outreach_sent" as const,
    label: "Outreach Sent",
    icon: "📧",
    gradient: "from-blue-400/20 to-blue-600/10",
    textColor: "text-blue-300",
  },
  {
    key: "interviews_scheduled" as const,
    label: "Interviews",
    icon: "🎯",
    gradient: "from-emerald-400/20 to-emerald-600/10",
    textColor: "text-emerald-300",
  },
  {
    key: "response_rate" as const,
    label: "Response Rate",
    icon: "📈",
    gradient: "from-cyan-400/20 to-cyan-600/10",
    textColor: "text-cyan-300",
    suffix: "%",
  },
  {
    key: "avg_match_score" as const,
    label: "Avg Match Score",
    icon: "⭐",
    gradient: "from-amber-400/20 to-amber-600/10",
    textColor: "text-amber-300",
    suffix: "%",
  },
  {
    key: "applications_this_week" as const,
    label: "This Week",
    icon: "🚀",
    gradient: "from-purple-400/20 to-purple-600/10",
    textColor: "text-purple-300",
  },
];

export default function StatsBar({ stats }: StatsBarProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
      {STAT_CARDS.map((card) => (
        <div
          key={card.key}
          className={`stat-card bg-gradient-to-br ${card.gradient} border border-white/10`}
        >
          <div className="flex items-center gap-2">
            <span className="text-lg">{card.icon}</span>
            <span className="text-[11px] font-medium text-surface-200 uppercase tracking-wide">
              {card.label}
            </span>
          </div>
          <p className={`text-2xl font-bold ${card.textColor}`}>
            {stats[card.key]}
            {card.suffix || ""}
          </p>
        </div>
      ))}
    </div>
  );
}
