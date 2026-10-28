
import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Chip,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
} from "@mui/material";
import RefreshRounded from "@mui/icons-material/RefreshRounded";
import SearchRounded from "@mui/icons-material/SearchRounded";
import api from "../services/api";

interface Trace {
  trace_id?: string;
  id?: string;
  service_name?: string;
  service?: string;
  operation_name?: string;
  operation?: string;
  status?: string;
  duration_ms?: number;
  duration?: number;
  timestamp?: string;
  start_time?: string;
}

export default function Traces() {
  const [traces, setTraces] = useState<Trace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  async function loadTraces() {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("/traces");
      const data = response.data;

      const records: Trace[] = Array.isArray(data)
        ? data
        : Array.isArray(data?.traces)
          ? data.traces
          : Array.isArray(data?.items)
            ? data.items
            : [];

      setTraces(records);
    } catch (err) {
      console.error("Failed to load traces:", err);
      setError(
        "Unable to load traces. Check that the backend is running and GET /traces is available."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadTraces();
  }, []);

  const filteredTraces = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return traces;
    }

    return traces.filter((trace) =>
      [
        trace.trace_id,
        trace.id,
        trace.service_name,
        trace.service,
        trace.operation_name,
        trace.operation,
        trace.status,
      ].some((value) =>
        String(value ?? "").toLowerCase().includes(query)
      )
    );
  }, [traces, search]);

  return (
    <Box>
      <Box className="page-heading">
        <Box>
          <h2 className="page-title">Trace Explorer</h2>
          <p className="page-subtitle">
            Investigate requests across your distributed services.
          </p>
        </Box>

        <button
          type="button"
          className="refresh-button"
          onClick={() => void loadTraces()}
          disabled={loading}
        >
          <RefreshRounded fontSize="small" />
          Refresh
        </button>
      </Box>

      <Paper className="trace-panel" elevation={0}>
        <Box className="trace-toolbar">
          <TextField
            size="small"
            fullWidth
            placeholder="Search trace ID, service, operation or status..."
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            slotProps={{
              input: {
                startAdornment: (
                  <SearchRounded
                    sx={{ mr: 1, color: "#8b95a7" }}
                  />
                ),
              },
            }}
          />

          <Chip
            label={`${filteredTraces.length} traces`}
            variant="outlined"
          />
        </Box>

        {error && (
          <Alert severity="error" sx={{ m: 2 }}>
            {error}
          </Alert>
        )}

        {loading ? (
          <Box className="loading-state">
            <CircularProgress size={28} />
            <p>Loading traces...</p>
          </Box>
        ) : (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Trace ID</TableCell>
                  <TableCell>Service</TableCell>
                  <TableCell>Operation</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Duration</TableCell>
                  <TableCell>Timestamp</TableCell>
                </TableRow>
              </TableHead>

              <TableBody>
                {filteredTraces.map((trace, index) => {
                  const traceId =
                    trace.trace_id ?? trace.id ?? `trace-${index}`;

                  const status = trace.status ?? "Unknown";
                  const duration =
                    trace.duration_ms ?? trace.duration;

                  const timestamp =
                    trace.timestamp ?? trace.start_time;

                  return (
                    <TableRow key={traceId} hover>
                      <TableCell>
                        <span className="trace-id">{traceId}</span>
                      </TableCell>

                      <TableCell>
                        {trace.service_name ?? trace.service ?? "—"}
                      </TableCell>

                      <TableCell>
                        {trace.operation_name ?? trace.operation ?? "—"}
                      </TableCell>

                      <TableCell>
                        <Chip
                          size="small"
                          label={status}
                          color={
                            /error|fail/i.test(status)
                              ? "error"
                              : /ok|success|complete/i.test(status)
                                ? "success"
                                : "default"
                          }
                        />
                      </TableCell>

                      <TableCell align="right">
                        {duration == null ? "—" : `${duration} ms`}
                      </TableCell>

                      <TableCell>
                        {timestamp
                          ? new Date(timestamp).toLocaleString()
                          : "—"}
                      </TableCell>
                    </TableRow>
                  );
                })}

                {!error && filteredTraces.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={6}>
                      <Box className="empty-state">
                        <p><strong>No traces found</strong></p>
                        <p>
                          {search
                            ? "Try a different search term."
                            : "No trace records were returned by the backend yet."}
                        </p>
                      </Box>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}
      </Paper>
    </Box>
  );
}
