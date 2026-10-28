
import { useCallback, useEffect, useMemo, useState } from "react";
import api from "../services/api";

type AlertStatus = "firing" | "acknowledged" | "resolved";
type AlertSeverity = "info" | "warning" | "critical";

interface AlertItem {
  id: number;
  alert_key: string;
  alert_name: string;
  service_name: string;
  metric_name: string;
  observed_value: number;
  threshold_value: number;
  severity: AlertSeverity;
  status: AlertStatus;
  description: string | null;
  attributes: Record<string, unknown> | null;
  fired_at: string;
  acknowledged_at: string | null;
  resolved_at: string | null;
  created_at: string;
}

interface AlertsResponse {
  total: number;
  limit: number;
  offset: number;
  items: AlertItem[];
}

const statusColors: Record<AlertStatus, string> = {
  firing: "#dc2626",
  acknowledged: "#d97706",
  resolved: "#15803d",
};

const severityColors: Record<AlertSeverity, string> = {
  info: "#2563eb",
  warning: "#d97706",
  critical: "#dc2626",
};

const cardStyle: React.CSSProperties = {
  background: "var(--card-bg, #ffffff)",
  border: "1px solid var(--border-color, #e5e7eb)",
  borderRadius: 12,
  padding: 18,
};

const mutedStyle: React.CSSProperties = {
  color: "var(--muted-text, #64748b)",
  fontSize: 13,
};

const buttonStyle: React.CSSProperties = {
  border: "1px solid var(--border-color, #d1d5db)",
  borderRadius: 7,
  padding: "8px 12px",
  cursor: "pointer",
  fontSize: 13,
  fontWeight: 600,
  background: "var(--card-bg, #ffffff)",
  color: "var(--text-color, #111827)",
};

function formatDate(value: string | null): string {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString();
}

function formatValue(value: number): string {
  return Number.isFinite(value) ? String(value) : "—";
}

function Badge({
  label,
  color,
}: {
  label: string;
  color: string;
}) {
  return (
    <span
      style={{
        display: "inline-block",
        color,
        background: `${color}15`,
        border: `1px solid ${color}40`,
        borderRadius: 20,
        padding: "4px 9px",
        fontSize: 11,
        fontWeight: 700,
        textTransform: "uppercase",
        whiteSpace: "nowrap",
      }}
    >
      {label}
    </span>
  );
}

export default function Alerts() {
  const [items, setItems] = useState<AlertItem[]>([]);
  const [total, setTotal] = useState(0);
  const [statusFilter, setStatusFilter] = useState("");
  const [severityFilter, setSeverityFilter] = useState("");
  const [serviceFilter, setServiceFilter] = useState("");
  const [selectedAlert, setSelectedAlert] = useState<AlertItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const params: Record<string, string | number> = {
        limit: 200,
        offset: 0,
      };

      if (statusFilter) params.status = statusFilter;
      if (severityFilter) params.severity = severityFilter;

      const response = await api.get<AlertsResponse>("/alerts", { params });
      const result = response.data;

      const receivedItems = Array.isArray(result.items) ? result.items : [];

      setItems(receivedItems);
      setTotal(result.total ?? receivedItems.length);

      setSelectedAlert((current) =>
        current
          ? receivedItems.find((item) => item.id === current.id) ?? null
          : null,
      );
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : "Unable to load alerts.";

      setError(message);
      setItems([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [statusFilter, severityFilter]);

  useEffect(() => {
    void loadAlerts();
  }, [loadAlerts, refreshKey]);

  const visibleItems = useMemo(() => {
    const service = serviceFilter.trim().toLowerCase();

    if (!service) return items;

    return items.filter((item) =>
      item.service_name.toLowerCase().includes(service),
    );
  }, [items, serviceFilter]);

  const counts = useMemo(
    () => ({
      firing: items.filter((item) => item.status === "firing").length,
      acknowledged: items.filter((item) => item.status === "acknowledged").length,
      resolved: items.filter((item) => item.status === "resolved").length,
      critical: items.filter((item) => item.severity === "critical").length,
    }),
    [items],
  );

  async function changeStatus(
    alert: AlertItem,
    action: "acknowledge" | "resolve",
  ) {
    setBusyId(alert.id);
    setError("");
    setNotice("");

    try {
      const response = await api.post(
        `/alerts/${alert.id}/${action}`,
      );

      setNotice(
        response.data?.message ??
          `Alert ${action === "acknowledge" ? "acknowledged" : "resolved"}.`,
      );

      setRefreshKey((current) => current + 1);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : `Unable to ${action} alert.`;

      setError(message);
    } finally {
      setBusyId(null);
    }
  }

  const activeCount = counts.firing + counts.acknowledged;

  return (
    <div style={{ display: "grid", gap: 20, color: "var(--text-color, #111827)" }}>
      <section
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 12,
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: 24 }}>Alerts Dashboard</h2>
          <p style={{ ...mutedStyle, marginBottom: 0 }}>
            Monitor, acknowledge, and resolve alerts from your telemetry backend.
          </p>
        </div>

        <button
          style={buttonStyle}
          onClick={() => setRefreshKey((current) => current + 1)}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "↻ Refresh"}
        </button>
      </section>

      {error && (
        <div
          role="alert"
          style={{
            ...cardStyle,
            borderColor: "#fca5a5",
            color: "#b91c1c",
          }}
        >
          <strong>Request failed</strong>
          <p style={{ marginBottom: 0 }}>{error}</p>
          <p style={{ ...mutedStyle, marginBottom: 0 }}>
            Check that the backend is running and the API base URL is correct.
          </p>
        </div>
      )}

      {notice && (
        <div
          role="status"
          style={{
            ...cardStyle,
            borderColor: "#86efac",
            color: "#166534",
          }}
        >
          {notice}
        </div>
      )}

      <section
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(155px, 1fr))",
          gap: 14,
        }}
      >
        {[
          { label: "Loaded Alerts", value: items.length, color: "#2563eb" },
          { label: "Active Alerts", value: activeCount, color: "#dc2626" },
          { label: "Firing", value: counts.firing, color: "#dc2626" },
          { label: "Acknowledged", value: counts.acknowledged, color: "#d97706" },
          { label: "Critical", value: counts.critical, color: "#991b1b" },
        ].map((metric) => (
          <div key={metric.label} style={cardStyle}>
            <div style={mutedStyle}>{metric.label}</div>
            <div
              style={{
                fontSize: 28,
                fontWeight: 750,
                color: metric.color,
                marginTop: 8,
              }}
            >
              {loading ? "…" : metric.value}
            </div>
          </div>
        ))}
      </section>

      <section style={{ ...cardStyle, display: "grid", gap: 14 }}>
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            flexWrap: "wrap",
            alignItems: "center",
            gap: 10,
          }}
        >
          <h3 style={{ margin: 0 }}>Alert Records</h3>
          <span style={mutedStyle}>
            {loading ? "Loading…" : `${visibleItems.length} shown · ${total} matching API records`}
          </span>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
          }}
        >
          <label style={{ display: "grid", gap: 5, fontSize: 12 }}>
            Status
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
              style={{ ...buttonStyle, minWidth: 150 }}
            >
              <option value="">All statuses</option>
              <option value="firing">Firing</option>
              <option value="acknowledged">Acknowledged</option>
              <option value="resolved">Resolved</option>
            </select>
          </label>

          <label style={{ display: "grid", gap: 5, fontSize: 12 }}>
            Severity
            <select
              value={severityFilter}
              onChange={(event) => setSeverityFilter(event.target.value)}
              style={{ ...buttonStyle, minWidth: 150 }}
            >
              <option value="">All severities</option>
              <option value="critical">Critical</option>
              <option value="warning">Warning</option>
              <option value="info">Info</option>
            </select>
          </label>

          <label style={{ display: "grid", gap: 5, fontSize: 12 }}>
            Service name
            <input
              value={serviceFilter}
              onChange={(event) => setServiceFilter(event.target.value)}
              placeholder="Search service..."
              style={{ ...buttonStyle, minWidth: 180 }}
            />
          </label>
        </div>

        {loading ? (
          <div style={{ padding: 28, textAlign: "center", ...mutedStyle }}>
            Loading alerts from the backend…
          </div>
        ) : visibleItems.length === 0 ? (
          <div
            style={{
              padding: 32,
              textAlign: "center",
              border: "1px dashed var(--border-color, #cbd5e1)",
              borderRadius: 10,
            }}
          >
            <div style={{ fontSize: 20, marginBottom: 8 }}>No matching alerts</div>
            <p style={{ ...mutedStyle, margin: 0 }}>
              {error
                ? "Alerts could not be loaded. Resolve the request error and retry."
                : "The backend returned no alerts for these filters. No sample records have been added."}
            </p>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                textAlign: "left",
                fontSize: 13,
              }}
            >
              <thead>
                <tr style={{ background: "var(--table-header-bg, #f8fafc)" }}>
                  {[
                    "Alert",
                    "Service",
                    "Observed / Threshold",
                    "Severity",
                    "Status",
                    "Fired At",
                    "Actions",
                  ].map((heading) => (
                    <th
                      key={heading}
                      style={{
                        padding: "12px 10px",
                        borderBottom: "1px solid var(--border-color, #e5e7eb)",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {visibleItems.map((alert) => (
                  <tr key={alert.id}>
                    <td style={{ padding: 10, borderBottom: "1px solid var(--border-color, #e5e7eb)" }}>
                      <button
                        onClick={() => setSelectedAlert(alert)}
                        style={{
                          border: 0,
                          background: "transparent",
                          color: "var(--link-color, #2563eb)",
                          cursor: "pointer",
                          padding: 0,
                          textAlign: "left",
                          fontWeight: 700,
                        }}
                      >
                        {alert.alert_name}
                      </button>
                      <div style={mutedStyle}>ID: {alert.id}</div>
                    </td>
                    <td style={{ padding: 10, borderBottom: "1px solid var(--border-color, #e5e7eb)" }}>
                      <div>{alert.service_name}</div>
                      <div style={mutedStyle}>{alert.metric_name}</div>
                    </td>
                    <td style={{ padding: 10, borderBottom: "1px solid var(--border-color, #e5e7eb)", whiteSpace: "nowrap" }}>
                      {formatValue(alert.observed_value)} / {formatValue(alert.threshold_value)}
                    </td>
                    <td style={{ padding: 10, borderBottom: "1px solid var(--border-color, #e5e7eb)" }}>
                      <Badge label={alert.severity} color={severityColors[alert.severity] ?? "#64748b"} />
                    </td>
                    <td style={{ padding: 10, borderBottom: "1px solid var(--border-color, #e5e7eb)" }}>
                      <Badge label={alert.status} color={statusColors[alert.status] ?? "#64748b"} />
                    </td>
                    <td style={{ padding: 10, borderBottom: "1px solid var(--border-color, #e5e7eb)", whiteSpace: "nowrap" }}>
                      {formatDate(alert.fired_at)}
                    </td>
                    <td style={{ padding: 10, borderBottom: "1px solid var(--border-color, #e5e7eb)" }}>
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                        {alert.status === "firing" && (
                          <button
                            style={buttonStyle}
                            disabled={busyId === alert.id}
                            onClick={() => void changeStatus(alert, "acknowledge")}
                          >
                            {busyId === alert.id ? "Working…" : "Acknowledge"}
                          </button>
                        )}
                        {(alert.status === "firing" || alert.status === "acknowledged") && (
                          <button
                            style={{ ...buttonStyle, color: "#15803d" }}
                            disabled={busyId === alert.id}
                            onClick={() => void changeStatus(alert, "resolve")}
                          >
                            Resolve
                          </button>
                        )}
                        <button
                          style={buttonStyle}
                          onClick={() => setSelectedAlert(alert)}
                        >
                          Details
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {selectedAlert && (
        <section style={{ ...cardStyle, display: "grid", gap: 14 }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 12,
            }}
          >
            <h3 style={{ margin: 0 }}>Alert Details — #{selectedAlert.id}</h3>
            <button style={buttonStyle} onClick={() => setSelectedAlert(null)}>
              Close
            </button>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
              gap: 14,
            }}
          >
            {[
              ["Alert name", selectedAlert.alert_name],
              ["Alert key", selectedAlert.alert_key],
              ["Service", selectedAlert.service_name],
              ["Metric", selectedAlert.metric_name],
              ["Observed value", formatValue(selectedAlert.observed_value)],
              ["Threshold value", formatValue(selectedAlert.threshold_value)],
              ["Fired at", formatDate(selectedAlert.fired_at)],
              ["Acknowledged at", formatDate(selectedAlert.acknowledged_at)],
              ["Resolved at", formatDate(selectedAlert.resolved_at)],
              ["Created at", formatDate(selectedAlert.created_at)],
            ].map(([label, value]) => (
              <div key={label}>
                <div style={mutedStyle}>{label}</div>
                <div style={{ fontWeight: 600, overflowWrap: "anywhere" }}>
                  {value || "—"}
                </div>
              </div>
            ))}
          </div>

          <div>
            <div style={mutedStyle}>Description</div>
            <p style={{ marginTop: 5 }}>
              {selectedAlert.description || "No description provided by the backend."}
            </p>
          </div>

          <div>
            <div style={mutedStyle}>Attributes</div>
            <pre
              style={{
                padding: 12,
                borderRadius: 8,
                overflowX: "auto",
                background: "var(--code-bg, #f8fafc)",
                fontSize: 12,
              }}
            >
              {JSON.stringify(selectedAlert.attributes ?? {}, null, 2)}
            </pre>
          </div>
        </section>
      )}
    </div>
  );
}
