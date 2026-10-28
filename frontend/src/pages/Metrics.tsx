
import { useCallback, useEffect, useState } from "react";
import api from "../services/api";

interface RequestCountSummary {
  service_name: string;
  request_count: number;
  start_time: string | null;
  end_time: string | null;
}

interface ErrorRateSummary {
  service_name: string;
  error_rate_percent: number;
  start_time: string | null;
  end_time: string | null;
}

interface LatencySummary {
  service_name: string;
  average_latency: number | null;
  unit: string;
  start_time: string | null;
  end_time: string | null;
}

interface GroupedMetric {
  service_name: string;
  metric_name: string;
  record_count: number;
  total_value: number;
  average_value: number;
}

interface GroupedMetricsResponse {
  items: GroupedMetric[];
}

const panelStyle = {
  padding: 20,
  border: "1px solid #334155",
  borderRadius: 12,
  background: "#111827",
  color: "#e2e8f0",
} as const;

const buttonStyle = {
  padding: "10px 16px",
  border: "1px solid #475569",
  borderRadius: 7,
  background: "#1e293b",
  color: "#f8fafc",
  cursor: "pointer",
} as const;

export default function Metrics() {
  const [requestCount, setRequestCount] =
    useState<RequestCountSummary | null>(null);

  const [errorRate, setErrorRate] =
    useState<ErrorRateSummary | null>(null);

  const [latency, setLatency] =
    useState<LatencySummary | null>(null);

  const [groupedMetrics, setGroupedMetrics] = useState<GroupedMetric[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadMetrics = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const service = "order-service";

      const [
        requestsResponse,
        errorsResponse,
        latencyResponse,
        groupedResponse,
      ] = await Promise.all([
        api.get<RequestCountSummary>("/metrics/summary/request-count", {
          params: { service_name: service },
        }),

        api.get<ErrorRateSummary>("/metrics/summary/error-rate", {
          params: { service_name: service },
        }),

        api.get<LatencySummary>("/metrics/summary/latency", {
          params: { service_name: service },
        }),

        api.get<GroupedMetricsResponse>("/metrics/summary/grouped", {
          params: { service_name: service },
        }),
      ]);

      setRequestCount(requestsResponse.data);
      setErrorRate(errorsResponse.data);
      setLatency(latencyResponse.data);
      setGroupedMetrics(groupedResponse.data.items);
    } catch (err) {
      console.error("Failed to load metrics:", err);

      setError(
        "Unable to load metrics. Check the backend and verify that the Metrics APIs accept the selected service name."
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadMetrics();
  }, [loadMetrics]);

  const serviceName =
    requestCount?.service_name ??
    errorRate?.service_name ??
    latency?.service_name ??
    groupedMetrics[0]?.service_name ??
    "order-service";

  const formatNumber = (value: number | null | undefined) =>
    value == null
      ? "N/A"
      : value.toLocaleString(undefined, {
          maximumFractionDigits: 2,
        });

  const maxValue = Math.max(
    1,
    ...groupedMetrics.map((metric) => Math.abs(metric.average_value))
  );

  return (
    <div
      style={{
        fontFamily: "Arial, sans-serif",
        color: "#e2e8f0",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 12,
          marginBottom: 24,
        }}
      >
        <div>
          <h2 style={{ margin: "0 0 8px", fontSize: 25 }}>
            Metrics Dashboard
          </h2>

          <p style={{ margin: 0, color: "#94a3b8" }}>
            Monitor request volume, errors, latency, and recorded metrics.
          </p>
        </div>

        <button
          style={{
            ...buttonStyle,
            opacity: loading ? 0.6 : 1,
          }}
          onClick={() => void loadMetrics()}
          disabled={loading}
        >
          {loading ? "Refreshing..." : "Refresh metrics"}
        </button>
      </div>

      {loading && (
        <div style={{ ...panelStyle, marginBottom: 20 }}>
          Loading metrics from the backend...
        </div>
      )}

      {!loading && error && (
        <div
          style={{
            ...panelStyle,
            marginBottom: 20,
            borderColor: "#b91c1c",
          }}
        >
          <p style={{ color: "#fca5a5" }}>{error}</p>

          <button
            style={buttonStyle}
            onClick={() => void loadMetrics()}
          >
            Try again
          </button>
        </div>
      )}

      {!loading && !error && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))",
              gap: 16,
              marginBottom: 22,
            }}
          >
            <MetricCard
              title="Request Count"
              value={formatNumber(requestCount?.request_count)}
              description="Total requests reported by the API"
            />

            <MetricCard
              title="Error Rate"
              value={
                errorRate
                  ? `${formatNumber(errorRate.error_rate_percent)}%`
                  : "N/A"
              }
              description="Reported percentage of errors"
            />

            <MetricCard
              title="Average Latency"
              value={
                latency?.average_latency == null
                  ? "N/A"
                  : `${formatNumber(latency.average_latency)} ${latency.unit}`
              }
              description="Average latency reported by the API"
            />

            <MetricCard
              title="Metric Types"
              value={formatNumber(
                new Set(
                  groupedMetrics.map((metric) => metric.metric_name)
                ).size
              )}
              description="Distinct recorded metric names"
            />
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
              gap: 20,
              marginBottom: 22,
            }}
          >
            <section style={panelStyle}>
              <h3 style={{ marginTop: 0 }}>Service overview</h3>

              <p style={{ color: "#94a3b8" }}>Service name</p>
              <strong style={{ fontSize: 20 }}>{serviceName}</strong>

              <div
                style={{
                  marginTop: 20,
                  paddingTop: 16,
                  borderTop: "1px solid #334155",
                }}
              >
                <p style={{ color: "#94a3b8" }}>Request count</p>
                <strong>
                  {formatNumber(requestCount?.request_count)}
                </strong>
              </div>

              <div style={{ marginTop: 16 }}>
                <p style={{ color: "#94a3b8" }}>Error rate</p>
                <strong>
                  {errorRate
                    ? `${formatNumber(errorRate.error_rate_percent)}%`
                    : "N/A"}
                </strong>
              </div>
            </section>

            <section style={panelStyle}>
              <h3 style={{ marginTop: 0 }}>Grouped metric averages</h3>

              {groupedMetrics.length === 0 ? (
                <p style={{ color: "#94a3b8" }}>
                  No grouped metric records were returned by the API.
                </p>
              ) : (
                <div style={{ display: "grid", gap: 18 }}>
                  {groupedMetrics.map((metric) => (
                    <div
                      key={`${metric.service_name}-${metric.metric_name}`}
                    >
                      <div
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: 12,
                          marginBottom: 8,
                        }}
                      >
                        <span style={{ overflowWrap: "anywhere" }}>
                          {metric.metric_name}
                        </span>

                        <strong>
                          {formatNumber(metric.average_value)}
                        </strong>
                      </div>

                      <div
                        style={{
                          height: 8,
                          background: "#263449",
                          borderRadius: 8,
                          overflow: "hidden",
                        }}
                      >
                        <div
                          style={{
                            height: "100%",
                            width: `${Math.min(
                              100,
                              (Math.abs(metric.average_value) / maxValue) *
                                100
                            )}%`,
                            background: "#38bdf8",
                            borderRadius: 8,
                          }}
                        />
                      </div>

                      <p
                        style={{
                          margin: "6px 0 0",
                          color: "#94a3b8",
                          fontSize: 12,
                        }}
                      >
                        {metric.service_name} · {metric.record_count} record(s)
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </section>
          </div>

          <section style={{ ...panelStyle, overflowX: "auto" }}>
            <h3 style={{ marginTop: 0 }}>Grouped metrics details</h3>

            {groupedMetrics.length === 0 ? (
              <p style={{ color: "#94a3b8" }}>No metrics to display.</p>
            ) : (
              <table
                style={{
                  width: "100%",
                  minWidth: 650,
                  borderCollapse: "collapse",
                  textAlign: "left",
                }}
              >
                <thead>
                  <tr style={{ background: "#1e293b" }}>
                    {[
                      "Service",
                      "Metric name",
                      "Records",
                      "Total value",
                      "Average value",
                    ].map((heading) => (
                      <th
                        key={heading}
                        style={{
                          padding: 12,
                          borderBottom: "1px solid #334155",
                        }}
                      >
                        {heading}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {groupedMetrics.map((metric) => (
                    <tr
                      key={`${metric.service_name}-${metric.metric_name}`}
                    >
                      {[
                        metric.service_name,
                        metric.metric_name,
                        formatNumber(metric.record_count),
                        formatNumber(metric.total_value),
                        formatNumber(metric.average_value),
                      ].map((value, index) => (
                        <td
                          key={index}
                          style={{
                            padding: 12,
                            borderBottom: "1px solid #263449",
                            overflowWrap: "anywhere",
                          }}
                        >
                          {value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </>
      )}
    </div>
  );
}

function MetricCard({
  title,
  value,
  description,
}: {
  title: string;
  value: string;
  description: string;
}) {
  return (
    <section
      style={{
        padding: 20,
        border: "1px solid #334155",
        borderRadius: 12,
        background: "#111827",
        color: "#e2e8f0",
      }}
    >
      <p style={{ margin: "0 0 14px", color: "#94a3b8" }}>
        {title}
      </p>

      <strong
        style={{
          display: "block",
          fontSize: 28,
          marginBottom: 10,
        }}
      >
        {value}
      </strong>

      <p style={{ margin: 0, fontSize: 12, color: "#94a3b8" }}>
        {description}
      </p>
    </section>
  );
}
