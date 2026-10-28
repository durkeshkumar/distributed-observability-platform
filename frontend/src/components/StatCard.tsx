
import type { ReactNode } from "react";

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  description: string;
  icon: ReactNode;
  tone: "blue" | "green" | "orange" | "purple";
  positive?: boolean;
}

export default function StatCard({
  title,
  value,
  change,
  description,
  icon,
  tone,
  positive = true,
}: StatCardProps) {
  return (
    <article className="stat-card">
      <div className="stat-card-top">
        <span className="stat-title">{title}</span>
        <span className={`stat-icon ${tone}`}>{icon}</span>
      </div>

      <div className="stat-value">{value}</div>

      <div className="stat-bottom">
        <span className={`stat-change ${positive ? "positive" : "negative"}`}>
          {change}
        </span>
        <span className="stat-description">{description}</span>
      </div>
    </article>
  );
}
