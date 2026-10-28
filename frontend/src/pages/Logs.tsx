
import { useCallback, useEffect, useState } from "react";
import api from "../services/api";

interface LogRecord {
  id: number;
  event_id: string;
  service_name: string;
  message: string;
  severity: string;
  timestamp: string;
  trace_id: string | null;
  attributes: Record<string, unknown> | null;
}

interface LogResponse {
  total: number;
  limit: number;
  offset: number;
  items: LogRecord[];
}

const pageStyle = {
  color: "#e2e8f0",
  fontFamily: "Arial, sans-serif",
} as const;

const inputStyle = {
  width: "100%",
  boxSizing: "border-box" as const,
  padding: "10px 12px",
  border: "1px solid #334155",
  borderRadius: "7px",
  background: "#0f172a",
  color: "#e2e8f0",
};

const buttonStyle = {
  padding: "10px 16px",
  border: "1px solid #475569",
  borderRadius: "7px",
  background: "#1e293b",
  color: "#f8fafc",
  cursor: "pointer",
};

export default function Logs() {
  const [logs, setLogs] = useState<LogRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [serviceName, setServiceName] = useState("");
  const [severity, setSeverity] = useState("");
  const [traceId, setTraceId] = useState("");
  const [appliedFilters, setAppliedFilters] = useState({
    service_name: "",
    severity: "",
    trace_id: "",
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const limit = 10;

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get<LogResponse>("/logs", {
        params: {
          limit,
          offset,
          ...(appliedFilters.service_name
            ? { service_name: appliedFilters.service_name }
            : {}),
          ...(appliedFilters.severity
            ? { severity: appliedFilters.severity }
            : {}),
          ...(appliedFilters.trace_id
            ? { trace_id: appliedFilters.trace_id }
            : {}),
        },
      });

      setLogs(response.data.items);
      setTotal(response.data.total);
    } catch (err: unknown) {
      setLogs([]);
      setTotal(0);

      if (typeof err === "object" && err !== null && "message" in err) {
        setError(String(err.message));
      } else {
        setError("Unable to load logs. Check whether the backend is running.");
      }
    } finally {
      setLoading(false);
    }
  }, [offset, appliedFilters]);

  useEffect(() => {
    void fetchLogs();
  }, [fetchLogs]);

  function applyFilters() {
    setOffset(0);
    setAppliedFilters({
      service_name: serviceName.trim(),
      severity,
      trace_id: traceId.trim(),
    });
  }

  function clearFilters() {
    setServiceName("");
    setSeverity("");
    setTraceId("");
    setOffset(0);
    setAppliedFilters({
      service_name: "",
      severity: "",
      trace_id: "",
    });
  }

  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.max(1, Math.ceil(total / limit));

  return (
    <div style={pageStyle}>
      <div style={{ marginBottom: 24 }}>
        <h2 style={{ margin: "0 0 8px", fontSize: 25 }}>
          Log Explorer
        </h2>
        <p style={{ margin: 0, color: "#94a3b8" }}>
          Search application logs and investigate service events.
        </p>
      </div>

      <section
        style={{
          padding: 20,
          marginBottom: 22,
          border: "1px solid #334155",
          borderRadius: 12,
          background: "#111827",
        }}
      >
        <h3 style={{ marginTop: 0 }}>Filter logs</h3>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: 16,
          }}
        >
          <label>
            <span style={{ display: "block", marginBottom: 8 }}>
              Service name
            </span>
            <input
              style={inputStyle}
              value={serviceName}
              onChange={(event) => setServiceName(event.target.value)}
              placeholder="e.g. order-service"
            />
          </label>

          <label>
            <span style={{ display: "block", marginBottom: 8 }}>
              Severity
            </span>
            <select
              style={inputStyle}
              value={severity}
              onChange={(event) => setSeverity(event.target.value)}
            >
              <option value="">All severities</option>
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </label>

          <label>
            <span style={{ display: "block", marginBottom: 8 }}>
              Trace ID
            </span>
            <input
              style={inputStyle}
              value={traceId}
              onChange={(event) => setTraceId(event.target.value)}
              placeholder="Enter trace ID"
            />
          </label>
        </div>

        <div style={{ display: "flex", gap: 10, marginTop: 18 }}>
          <button style={buttonStyle} onClick={applyFilters}>
            Search logs
          </button>
          <button style={buttonStyle} onClick={clearFilters}>
            Clear filters
          </button>
        </div>
      </section>

      <section
        style={{
          border: "1px solid #334155",
          borderRadius: 12,
          overflow: "hidden",
          background: "#111827",
        }}
      >
        <div
          style={{
            padding: 18,
            borderBottom: "1px solid #334155",
            display: "flex",
            justifyContent: "space-between",
            gap: 12,
            flexWrap: "wrap",
          }}
        >
          <strong>Log records</strong>
          <span style={{ color: "#94a3b8" }}>
            {total} record{total === 1 ? "" : "s"} found
          </span>
        </div>

        {loading ? (
          <p style={{ padding: 24 }}>Loading logs from the backend...</p>
        ) : error ? (
          <div style={{ padding: 24, color: "#fca5a5" }}>
            <p>Could not load logs.</p>
            <p>{error}</p>
            <button style={buttonStyle} onClick={() => void fetchLogs()}>
              Retry
            </button>
          </div>
        ) : logs.length === 0 ? (
          <div style={{ padding: 32, textAlign: "center" }}>
            <h3>No logs found</h3>
            <p style={{ color: "#94a3b8" }}>
              There are no stored logs matching these filters. Try clearing
              the filters or ingesting log records through the backend.
            </p>
          </div>
        ) : (
          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                textAlign: "left",
                minWidth: 800,
              }}
            >
              <thead>
                <tr style={{ background: "#1e293b" }}>
                  {[
                    "Timestamp",
                    "Service",
                    "Severity",
                    "Message",
                    "Trace ID",
                  ].map((heading) => (
                    <th
                      key={heading}
                      style={{
                        padding: 14,
                        borderBottom: "1px solid #334155",
                        color: "#cbd5e1",
                        fontSize: 13,
                      }}
                    >
                      {heading}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map((log) => (
                  <tr key={log.id}>
                    <td
                      style={{
                        padding: 14,
                        borderBottom: "1px solid #263449",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td
                      style={{
                        padding: 14,
                        borderBottom: "1px solid #263449",
                      }}
                    >
                      {log.service_name}
                    </td>
                    <td
                      style={{
                        padding: 14,
                        borderBottom: "1px solid #263449",
                      }}
                    >
                      <span
                        style={{
                          display: "inline-block",
                          padding: "4px 8px",
                          borderRadius: 5,
                          background:
                            log.severity.toUpperCase() === "ERROR" ||
                            log.severity.toUpperCase() === "CRITICAL"
                              ? "#7f1d1d"
                              : log.severity.toUpperCase() === "WARNING" ||
                                  log.severity.toUpperCase() === "WARN"
                                ? "#78350f"
                                : "#164e63",
                        }}
                      >
                        {log.severity}
                      </span>
                    </td>
                    <td
                      style={{
                        padding: 14,
                        borderBottom: "1px solid #263449",
                        maxWidth: 420,
                        overflowWrap: "anywhere",
                      }}
                    >
                      {log.message}
                    </td>
                    <td
                      style={{
                        padding: 14,
                        borderBottom: "1px solid #263449",
                        overflowWrap: "anywhere",
                      }}
                    >
                      {log.trace_id || "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {!loading && !error && total > 0 && (
          <div
            style={{
              padding: 16,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: 12,
              borderTop: "1px solid #334155",
            }}
          >
            <span style={{ color: "#94a3b8" }}>
              Page {currentPage} of {totalPages}
            </span>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                style={buttonStyle}
                disabled={offset === 0}
                onClick={() => setOffset(Math.max(0, offset - limit))}
              >
                Previous
              </button>
              <button
                style={buttonStyle}
                disabled={offset + limit >= total}
                onClick={() => setOffset(offset + limit)}
              >
                Next
              </button>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
