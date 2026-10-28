
import {
  NorthEastRounded,
  ArrowDownwardRounded,
  AccountTreeRounded,
  SpeedRounded,
  ErrorOutlineRounded,
  NotificationsActiveRounded,
  MoreHorizRounded,
  CheckCircleRounded,
  WarningAmberRounded,
  TrendingUpRounded,
} from "@mui/icons-material";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
} from "recharts";
import StatCard from "../components/StatCard";

const requestData = [
  { time: "00:00", requests: 2100, errors: 90 },
  { time: "04:00", requests: 1700, errors: 55 },
  { time: "08:00", requests: 3600, errors: 130 },
  { time: "12:00", requests: 5200, errors: 180 },
  { time: "16:00", requests: 4300, errors: 110 },
  { time: "20:00", requests: 6100, errors: 220 },
  { time: "23:59", requests: 4800, errors: 145 },
];

const serviceData = [
  { name: "API Gateway", latency: 125 },
  { name: "Order Service", latency: 184 },
  { name: "Payment", latency: 246 },
  { name: "Inventory", latency: 158 },
  { name: "Auth Service", latency: 92 },
];

const recentEvents = [
  {
    service: "payment-service",
    event: "Elevated response latency detected",
    time: "2 min ago",
    severity: "Critical",
  },
  {
    service: "order-service",
    event: "Error rate crossed warning threshold",
    time: "8 min ago",
    severity: "Warning",
  },
  {
    service: "api-gateway",
    event: "New deployment detected",
    time: "16 min ago",
    severity: "Info",
  },
];

export default function Overview() {
  return (
    <div className="overview">
      <div className="demo-notice">
        <span className="demo-notice-dot" />
        Demo data — live backend integration is the next step
      </div>

      <section className="welcome-row">
        <div>
          <h2>System overview</h2>
          <p>Monitor service health, performance, and distributed requests.</p>
        </div>
        <button
          className="refresh-button"
          type="button"
          onClick={() => window.location.reload()}
        >
          <TrendingUpRounded fontSize="small" />
          Dashboard overview
        </button>
      </section>

      <section className="stats-grid">
        <StatCard
          title="Total Requests"
          value="128.4K"
          change="+12.8%"
          description="vs. previous period"
          icon={<AccountTreeRounded />}
          tone="blue"
        />
        <StatCard
          title="Error Rate"
          value="2.41%"
          change="-0.6%"
          description="vs. previous period"
          icon={<ErrorOutlineRounded />}
          tone="orange"
          positive
        />
        <StatCard
          title="Avg. Latency"
          value="184 ms"
          change="+8.2%"
          description="vs. previous period"
          icon={<SpeedRounded />}
          tone="purple"
          positive={false}
        />
        <StatCard
          title="Active Alerts"
          value="07"
          change="3 critical"
          description="requiring attention"
          icon={<NotificationsActiveRounded />}
          tone="green"
          positive={false}
        />
      </section>

      <section className="charts-grid">
        <article className="panel traffic-panel">
          <div className="panel-header">
            <div>
              <h3>Request traffic</h3>
              <p>Incoming requests and errors over time</p>
            </div>
            <button className="more-button" type="button" aria-label="More traffic options">
              <MoreHorizRounded />
            </button>
          </div>

          <div className="chart-legend">
            <span><i className="legend-dot requests-dot" /> Requests</span>
            <span><i className="legend-dot errors-dot" /> Errors</span>
          </div>

          <div className="chart-container traffic-chart">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={requestData} margin={{ top: 10, right: 8, left: -15, bottom: 0 }}>
                <defs>
                  <linearGradient id="requestsGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#6478ed" stopOpacity={0.24} />
                    <stop offset="95%" stopColor="#6478ed" stopOpacity={0.01} />
                  </linearGradient>
                  <linearGradient id="errorsGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#f59e69" stopOpacity={0.20} />
                    <stop offset="95%" stopColor="#f59e69" stopOpacity={0.01} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#edf0f6" strokeDasharray="4 4" vertical={false} />
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: "#9299aa", fontSize: 11 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: "#9299aa", fontSize: 11 }} />
                <Tooltip />
                <Area type="monotone" dataKey="requests" name="Requests" stroke="#6478ed" strokeWidth={2.5} fill="url(#requestsGradient)" />
                <Area type="monotone" dataKey="errors" name="Errors" stroke="#f59e69" strokeWidth={2} fill="url(#errorsGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          <div className="chart-footnote">
            <span><NorthEastRounded fontSize="small" /> Traffic trend across the selected period</span>
            <span>Sample series</span>
          </div>
        </article>

        <article className="panel latency-panel">
          <div className="panel-header">
            <div>
              <h3>Service latency</h3>
              <p>Average response time by service</p>
            </div>
            <button className="more-button" type="button" aria-label="More latency options">
              <MoreHorizRounded />
            </button>
          </div>

          <div className="latency-summary">
            <div>
              <span className="small-label">Overall average</span>
              <strong>184 <small>ms</small></strong>
            </div>
            <span className="latency-trend"><ArrowDownwardRounded fontSize="small" /> 4.3%</span>
          </div>

          <div className="chart-container latency-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={serviceData} layout="vertical" margin={{ top: 2, right: 18, left: 12, bottom: 2 }}>
                <CartesianGrid stroke="#edf0f6" strokeDasharray="4 4" horizontal={false} />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: "#9299aa", fontSize: 10 }} />
                <YAxis type="category" dataKey="name" width={94} axisLine={false} tickLine={false} tick={{ fill: "#646d80", fontSize: 10 }} />
                <Tooltip formatter={(value) => [`${value} ms`, "Latency"]} />
                <Bar dataKey="latency" fill="#7888ef" radius={[0, 5, 5, 0]} barSize={13} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="panel-footnote">
            <span>Target latency</span>
            <strong>Below 200 ms</strong>
          </div>
        </article>
      </section>

      <section className="bottom-grid">
        <article className="panel services-panel">
          <div className="panel-header">
            <div>
              <h3>Service health</h3>
              <p>Current state of your services</p>
            </div>
            <button className="text-action" type="button">View services <NorthEastRounded fontSize="small" /></button>
          </div>

          <div className="service-row">
            <div className="service-symbol gateway-symbol">AG</div>
            <div className="service-details">
              <strong>API Gateway</strong>
              <span>api-gateway</span>
            </div>
            <div className="service-metric"><strong>125 ms</strong><span>Latency</span></div>
            <span className="health-pill healthy"><CheckCircleRounded /> Healthy</span>
          </div>

          <div className="service-row">
            <div className="service-symbol order-symbol">OR</div>
            <div className="service-details">
              <strong>Order Service</strong>
              <span>order-service</span>
            </div>
            <div className="service-metric"><strong>184 ms</strong><span>Latency</span></div>
            <span className="health-pill healthy"><CheckCircleRounded /> Healthy</span>
          </div>

          <div className="service-row">
            <div className="service-symbol payment-symbol">PY</div>
            <div className="service-details">
              <strong>Payment Service</strong>
              <span>payment-service</span>
            </div>
            <div className="service-metric"><strong>486 ms</strong><span>Latency</span></div>
            <span className="health-pill degraded"><WarningAmberRounded /> Degraded</span>
          </div>

          <div className="service-row">
            <div className="service-symbol inventory-symbol">IN</div>
            <div className="service-details">
              <strong>Inventory Service</strong>
              <span>inventory-service</span>
            </div>
            <div className="service-metric"><strong>158 ms</strong><span>Latency</span></div>
            <span className="health-pill healthy"><CheckCircleRounded /> Healthy</span>
          </div>
        </article>

        <article className="panel events-panel">
          <div className="panel-header">
            <div>
              <h3>Recent events</h3>
              <p>Latest system activity</p>
            </div>
            <button className="more-button" type="button" aria-label="More event options">
              <MoreHorizRounded />
            </button>
          </div>

          <div className="events-list">
            {recentEvents.map((event) => (
              <div className="event-row" key={`${event.service}-${event.time}`}>
                <div className={`event-severity-icon ${event.severity.toLowerCase()}`}>
                  {event.severity === "Critical" ? (
                    <ErrorOutlineRounded />
                  ) : event.severity === "Warning" ? (
                    <WarningAmberRounded />
                  ) : (
                    <CheckCircleRounded />
                  )}
                </div>
                <div className="event-content">
                  <strong>{event.event}</strong>
                  <span>{event.service} · {event.time}</span>
                </div>
                <span className={`severity-label ${event.severity.toLowerCase()}`}>
                  {event.severity}
                </span>
              </div>
            ))}
          </div>

          <button className="all-events-button" type="button">
            View all events <NorthEastRounded fontSize="small" />
          </button>
        </article>
      </section>

      <footer className="dashboard-footer">
        <span>Observa Platform</span>
        <span>Dashboard preview · Demo values are not live telemetry</span>
      </footer>
    </div>
  );
}
