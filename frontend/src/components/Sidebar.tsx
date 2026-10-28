
import {
  DashboardRounded,
  AccountTreeRounded,
  HubRounded,
  ArticleRounded,
  ShowChartRounded,
  TroubleshootRounded,
  NotificationsActiveRounded,
  SettingsRounded,
  InsightsRounded,
} from "@mui/icons-material";

const navigation = [
  { label: "Overview", icon: DashboardRounded, path: "/" },
  { label: "Traces", icon: AccountTreeRounded, path: "/traces" },
  { label: "Service Map", icon: HubRounded, path: "/service-map" },
  { label: "Logs", icon: ArticleRounded, path: "/logs" },
  { label: "Metrics", icon: ShowChartRounded, path: "/metrics" },
  { label: "Root Cause Analysis", icon: TroubleshootRounded, path: "/root-cause" },
  { label: "Alerts", icon: NotificationsActiveRounded, path: "/alerts" },
];

interface SidebarProps {
  activePath: string;
  onNavigate: (path: string) => void;
}

export default function Sidebar({ activePath, onNavigate }: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">
          <InsightsRounded />
        </div>
        <div>
          <div className="brand-name">Observa</div>
          <div className="brand-caption">OBSERVABILITY PLATFORM</div>
        </div>
      </div>

      <div className="workspace-label">WORKSPACE</div>

      <nav className="sidebar-nav">
        {navigation.map(({ label, icon: Icon, path }) => (
          <button
            key={path}
            type="button"
            className={`nav-item ${activePath === path ? "active" : ""}`}
            onClick={() => onNavigate(path)}
          >
            <Icon fontSize="small" />
            <span>{label}</span>
            {label === "Alerts" && <span className="nav-dot" />}
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="environment-card">
          <span className="environment-indicator" />
          <div>
            <div className="environment-title">Development</div>
            <div className="environment-subtitle">Local environment</div>
          </div>
        </div>

        <button
          type="button"
          className={`nav-item ${activePath === "/settings" ? "active" : ""}`}
          onClick={() => onNavigate("/settings")}
        >
          <SettingsRounded fontSize="small" />
          <span>Settings</span>
        </button>

        <div className="sidebar-footer">Distributed Systems · v1.0</div>
      </div>
    </aside>
  );
}
