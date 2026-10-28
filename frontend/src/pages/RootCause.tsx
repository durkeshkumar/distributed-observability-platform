
import { useState } from "react";
import api from "../services/api";

interface RootCauseIssue {
  type: string;
  score: number;
  message: string;
  span_id: string | null;
  log_id: number | null;
  severity: string | null;
  metric_name: string | null;
  observed_value: number | null;
  threshold: number | null;
}

interface RankedServiceDiagnosis {
  service_name: string;
  score: number;
  issue_count: number;
  issues: RootCauseIssue[];
}

interface RootCauseReport {
  trace_id: string;
  most_suspected_service: string | null;
  total_issues: number;
  ranked_services: RankedServiceDiagnosis[];
  analysis_status: string;
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
  background: "#2563eb",
  color: "#ffffff",
  cursor: "pointer",
} as const;

function displayStatus(status: string) {
  return status.replaceAll("_", " ");
}

function formatValue(value: number | null) {
  return value === null ? "N/A" : value.toLocaleString();
}

export default function RootCause() {
  const [traceId, setTraceId] = useState("phase6-trace-002");
  const [report, setReport] = useState<RootCauseReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeTrace(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const requestedTraceId = traceId.trim();

    if (!requestedTraceId) {
      setError("Please enter a trace ID.");
      setReport(null);
      return;
    }

    setLoading(true);
    setError("");
    setReport(null);

    try {
      const response = await api.get<RootCauseReport>(
        `/root-cause/${encodeURIComponent(requestedTraceId)}`
      );

      setReport(response.data);
    } catch (err: unknown) {
      console.error("Root cause analysis request failed:", err);

      if (
        typeof err === "object" &&
        err !== null &&
        "response" in err
      ) {
        const response = (
          err as {
            response?: {
              status?: number;
              data?: { detail?: string };
            };
          }
        ).response;

        if (response?.status === 404) {
          setError(
            response.data?.detail ??
              `Trace "${requestedTraceId}" was not found.`
          );
        } else if (response?.status === 400) {
          setError(
            response.data?.detail ??
              "The backend could not process this trace ID."
          );
        } else {
          setError(
            response?.data?.detail ??
              "Unable to analyze this trace. Check the backend and try again."
          );
        }
      } else {
        setError(
          "Cannot connect to the backend. Check that the API server is running."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        display: "grid",
        gap: 20,
        color: "#e2e8f0",
        fontFamily: "Arial, sans-serif",
      }}
    >
      <section>
        <h2 style={{ margin: "0 0 8px", fontSize: 25 }}>
          Root Cause Analysis
        </h2>

        <p style={{ margin: 0, color: "#94a3b8" }}>
          Investigate trace spans, logs, and metrics to identify services
          with potential issues.
        </p>
      </section>

      <section style={panelStyle}>
        <h3 style={{ marginTop: 0 }}>Analyze a trace</h3>

        <form
          onSubmit={analyzeTrace}
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 12,
            alignItems: "end",
          }}
        >
          <label
            style={{
              display: "grid",
              gap: 8,
              flex: "1 1 280px",
              color: "#cbd5e1",
            }}
          >
            Trace ID

            <input
              value={traceId}
              onChange={(event) => setTraceId(event.target.value)}
              placeholder="Enter an existing trace ID"
              maxLength={100}
              required
              style={{
                boxSizing: "border-box",
                width: "100%",
                padding: 12,
                border: "1px solid #475569",
                borderRadius: 7,
                background: "#0f172a",
                color: "#f8fafc",
              }}
            />
          </label>

          <button
            type="submit"
            disabled={loading}
            style={{
              ...buttonStyle,
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Analyzing..." : "Analyze trace"}
          </button>
        </form>

        <p
          style={{
            marginBottom: 0,
            color: "#94a3b8",
            fontSize: 12,
          }}
        >
          Test trace: phase6-trace-002
        </p>
      </section>

      {error && (
        <section
          role="alert"
          style={{
            ...panelStyle,
            borderColor: "#b91c1c",
            color: "#fca5a5",
          }}
        >
          <strong>Analysis could not be completed</strong>
          <p style={{ marginBottom: 0 }}>{error}</p>
        </section>
      )}

      {report && (
        <>
          <section
            style={{
              ...panelStyle,
              borderColor:
                report.analysis_status === "NO_ISSUES_DETECTED"
                  ? "#16a34a"
                  : "#b45309",
            }}
          >
            <p style={{ margin: "0 0 8px", color: "#94a3b8" }}>
              Analysis status
            </p>

            <h3 style={{ margin: "0 0 16px" }}>
              {displayStatus(report.analysis_status)}
            </h3>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
                gap: 16,
              }}
            >
              <div>
                <p style={{ color: "#94a3b8", margin: "0 0 8px" }}>
                  Trace ID
                </p>
                <strong style={{ overflowWrap: "anywhere" }}>
                  {report.trace_id}
                </strong>
              </div>

              <div>
                <p style={{ color: "#94a3b8", margin: "0 0 8px" }}>
                  Total issues
                </p>
                <strong style={{ fontSize: 24 }}>
                  {report.total_issues}
                </strong>
              </div>

              <div>
                <p style={{ color: "#94a3b8", margin: "0 0 8px" }}>
                  Most suspected service
                </p>
                <strong>
                  {report.most_suspected_service ?? "None identified"}
                </strong>
              </div>

              <div>
                <p style={{ color: "#94a3b8", margin: "0 0 8px" }}>
                  Services with findings
                </p>
                <strong style={{ fontSize: 24 }}>
                  {report.ranked_services.length}
                </strong>
              </div>
            </div>

            {report.analysis_status === "NO_ISSUES_DETECTED" && (
              <p style={{ marginBottom: 0, color: "#86efac" }}>
                The backend did not detect any issues for this trace.
              </p>
            )}

            {report.analysis_status === "POTENTIAL_ISSUES_FOUND" && (
              <p style={{ marginBottom: 0, color: "#fcd34d" }}>
                Potential issues were detected by the backend's diagnostic
                rules. These findings are evidence to investigate, not
                confirmed causes.
              </p>
            )}
          </section>

          <section style={panelStyle}>
            <h3 style={{ marginTop: 0 }}>Ranked service diagnoses</h3>

            {report.ranked_services.length === 0 ? (
              <p style={{ color: "#94a3b8", marginBottom: 0 }}>
                No services were ranked because the API returned no findings.
                Try another existing trace ID to inspect other results.
              </p>
            ) : (
              <div style={{ display: "grid", gap: 16 }}>
                {report.ranked_services.map((service, index) => (
                  <article
                    key={service.service_name}
                    style={{
                      padding: 16,
                      border: "1px solid #334155",
                      borderRadius: 9,
                      background: "#0f172a",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        flexWrap: "wrap",
                        justifyContent: "space-between",
                        gap: 12,
                      }}
                    >
                      <div>
                        <p
                          style={{
                            margin: "0 0 6px",
                            color: "#94a3b8",
                            fontSize: 12,
                          }}
                        >
                          Rank #{index + 1}
                        </p>

                        <h4 style={{ margin: 0, fontSize: 18 }}>
                          {service.service_name}
                        </h4>
                      </div>

                      <div>
                        <strong>Score: {service.score}</strong>
                        <p
                          style={{
                            margin: "5px 0 0",
                            color: "#94a3b8",
                            fontSize: 12,
                          }}
                        >
                          {service.issue_count} issue(s)
                        </p>
                      </div>
                    </div>

                    {service.issues.length > 0 && (
                      <div
                        style={{
                          display: "grid",
                          gap: 12,
                          marginTop: 16,
                        }}
                      >
                        {service.issues.map((issue, issueIndex) => (
                          <div
                            key={`${issue.type}-${issueIndex}`}
                            style={{
                              padding: 12,
                              borderLeft: "3px solid #f59e0b",
                              background: "#1e293b",
                              borderRadius: "0 7px 7px 0",
                            }}
                          >
                            <strong>
                              {displayStatus(issue.type)}
                            </strong>

                            <p style={{ margin: "8px 0" }}>
                              {issue.message}
                            </p>

                            <div
                              style={{
                                display: "flex",
                                flexWrap: "wrap",
                                gap: 12,
                                color: "#94a3b8",
                                fontSize: 12,
                              }}
                            >
                              <span>Score: {issue.score}</span>

                              {issue.severity && (
                                <span>Severity: {issue.severity}</span>
                              )}

                              {issue.span_id && (
                                <span>Span: {issue.span_id}</span>
                              )}

                              {issue.log_id !== null && (
                                <span>Log ID: {issue.log_id}</span>
                              )}

                              {issue.metric_name && (
                                <span>Metric: {issue.metric_name}</span>
                              )}

                              {issue.observed_value !== null && (
                                <span>
                                  Observed: {formatValue(issue.observed_value)}
                                </span>
                              )}

                              {issue.threshold !== null && (
                                <span>
                                  Threshold: {formatValue(issue.threshold)}
                                </span>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
}
