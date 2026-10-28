
import {
  BrowserRouter,
  Routes,
  Route,
  useLocation,
  useNavigate,
} from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Overview from "./pages/Overview";
import Traces from "./pages/Traces";
import ServiceMap from "./pages/ServiceMap";
import "./App.css";
import Logs from "./pages/Logs";
import Metrics from "./pages/Metrics";
import RootCause from "./pages/RootCause";
import Alerts from "./pages/Alerts";
import WorkspaceSettings from "./pages/WorkspaceSettings";

const pageInfo: Record<string, { title: string; subtitle: string }> = {
  "/": {
    title: "Observability",
    subtitle: "Your distributed systems, all in one place.",
  },
  "/traces": {
    title: "Trace Explorer",
    subtitle: "Investigate requests across your distributed services.",
  },
  "/service-map": {
    title: "Service Map",
    subtitle: "Explore service relationships and dependencies.",
  },
  "/logs": {
    title: "Log Explorer",
    subtitle: "Search and investigate application logs.",
  },
  "/metrics": {
    title: "Metrics",
    subtitle: "Track performance and system-level indicators.",
  },
  "/root-cause": {
    title: "Root Cause Analysis",
    subtitle: "Investigate service failures and diagnostic findings.",
  },
  "/alerts": {
    title: "Alert Center",
    subtitle: "Review active alerts and their lifecycle.",
  },
  "/settings": {
    title: "Settings",
    subtitle: "Configure your observability workspace.",
  },
};

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="placeholder-panel">
      <div className="placeholder-icon">✦</div>
      <h2>{title}</h2>
      <p>This section will be implemented in its upcoming frontend phase.</p>
      <span>Backend integration will be added as the page is developed.</span>
    </div>
  );
}

function AppLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const currentPath = location.pathname;
  const info = pageInfo[currentPath] ?? pageInfo["/"];

  return (
    <div className="app-shell">
      <Sidebar activePath={currentPath} onNavigate={navigate} />

      <main className="main-content">
        <Topbar title={info.title} subtitle={info.subtitle} />

        <div className="page-content">
          <Routes>
            <Route path="/" element={<Overview />} />

            <Route path="/traces" element={<Traces />} />

            <Route path="/service-map" element={<ServiceMap />} />

            <Route path="/logs" element={<Logs />} />

            <Route path="/metrics" element={<Metrics />} />

            <Route path="/root-cause" element={<RootCause />} />

            <Route path="/alerts" element={<Alerts />} />

            <Route
              path="/settings"
              element={<WorkspaceSettings />}
            />

            <Route
              path="*"
              element={<PlaceholderPage title="Page not found" />}
            />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppLayout />
    </BrowserRouter>
  );
}
