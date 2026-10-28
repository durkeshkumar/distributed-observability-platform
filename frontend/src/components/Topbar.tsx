
import {
  SearchRounded,
  NotificationsNoneRounded,
  KeyboardArrowDownRounded,
  AccessTimeRounded,
} from "@mui/icons-material";

interface TopbarProps {
  title: string;
  subtitle: string;
}

export default function Topbar({ title, subtitle }: TopbarProps) {
  return (
    <header className="topbar">
      <div className="topbar-heading">
        <div className="breadcrumb">Workspace <span>/</span> Observability</div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>

      <div className="topbar-actions">
        <div className="time-range">
          <AccessTimeRounded fontSize="small" />
          <span>Last 24 hours</span>
          <KeyboardArrowDownRounded fontSize="small" />
        </div>

        <button type="button" className="icon-button" aria-label="Search">
          <SearchRounded />
        </button>

        <button
          type="button"
          className="icon-button notification-button"
          aria-label="Notifications"
        >
          <NotificationsNoneRounded />
          <span />
        </button>

        <div className="avatar">DK</div>
      </div>
    </header>
  );
}
