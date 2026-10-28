import { useCallback, useEffect, useState } from "react";
import {
  Alert,
  Box,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  Divider,
  Stack,
  Typography,
} from "@mui/material";
import AccountTreeIcon from "@mui/icons-material/AccountTree";
import api from "../services/api";

interface ServiceNode {
  id: string;
  name: string;
  span_count: number;
  avg_duration_ms: number | null;
  error_count: number;
}

interface ServiceEdge {
  source: string;
  target: string;
  calls: number;
}

interface ServiceMapResponse {
  nodes: ServiceNode[];
  edges: ServiceEdge[];
  summary: {
    service_count: number;
    dependency_count: number;
    span_count: number;
  };
}

export default function ServiceMap() {
  const [data, setData] = useState<ServiceMapResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadServiceMap = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get<ServiceMapResponse>("/service-map");
      setData(response.data);
    } catch (err) {
      console.error("Failed to load service map:", err);
      setError(
        "Unable to load the Service Map. Check that the backend is running and try again.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadServiceMap();
  }, [loadServiceMap]);

  if (loading) {
    return (
      <Box
        sx={{
          minHeight: 280,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          gap: 2,
        }}
      >
        <CircularProgress />
        <Typography color="text.secondary">
          Loading service map from backend...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Stack spacing={2}>
        <Alert severity="error">{error}</Alert>
        <Box>
          <Chip
            label="Retry"
            clickable
            color="primary"
            onClick={() => void loadServiceMap()}
          />
        </Box>
      </Stack>
    );
  }

  if (!data) {
    return <Alert severity="warning">No Service Map response received.</Alert>;
  }

  return (
    <Stack spacing={3}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        sx={{
          justifyContent: "space-between",
          alignItems: { xs: "flex-start", sm: "center" },
          gap: 2,
        }}
      >
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Service Dependency Map
          </Typography>
          <Typography color="text.secondary" sx={{ mt: 0.5 }}>
            Services and relationships derived from stored trace spans.
          </Typography>
        </Box>

        <Chip
          label="Refresh"
          clickable
          color="primary"
          variant="outlined"
          onClick={() => void loadServiceMap()}
        />
      </Stack>

      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: {
            xs: "1fr",
            sm: "repeat(3, minmax(0, 1fr))",
          },
          gap: 2,
        }}
      >
        <Card variant="outlined">
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Services
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              {data.summary.service_count}
            </Typography>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Dependencies
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              {data.summary.dependency_count}
            </Typography>
          </CardContent>
        </Card>

        <Card variant="outlined">
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              Stored Spans
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>
              {data.summary.span_count}
            </Typography>
          </CardContent>
        </Card>
      </Box>

      <Card variant="outlined">
        <CardContent>
          <Stack
            direction="row"
            sx={{ alignItems: "center", gap: 1, mb: 2 }}
          >
            <AccountTreeIcon color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 700 }}>
              Observed Services
            </Typography>
          </Stack>

          {data.nodes.length === 0 ? (
            <Alert severity="info">
              No services have been found in the stored trace data yet.
              Ingest trace spans to populate this map.
            </Alert>
          ) : (
            <Stack spacing={2}>
              {data.nodes.map((service) => (
                <Box
                  key={service.id}
                  sx={{
                    border: "1px solid",
                    borderColor: "divider",
                    borderRadius: 2,
                    p: 2,
                  }}
                >
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    sx={{
                      justifyContent: "space-between",
                      alignItems: { xs: "flex-start", sm: "center" },
                      gap: 1,
                    }}
                  >
                    <Box>
                      <Typography sx={{ fontWeight: 700 }}>
                        {service.name}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {service.span_count}{" "}
                        {service.span_count === 1 ? "span" : "spans"}
                        {" · "}
                        Average duration:{" "}
                        {service.avg_duration_ms == null
                          ? "N/A"
                          : `${service.avg_duration_ms} ms`}
                      </Typography>
                    </Box>

                    <Chip
                      label={`${service.error_count} errors`}
                      color={service.error_count > 0 ? "error" : "success"}
                      size="small"
                      variant="outlined"
                    />
                  </Stack>
                </Box>
              ))}
            </Stack>
          )}
        </CardContent>
      </Card>

      <Card variant="outlined">
        <CardContent>
          <Typography
            variant="h6"
            sx={{ fontWeight: 700, mb: 2 }}
          >
            Cross-Service Dependencies
          </Typography>

          {data.edges.length === 0 ? (
            <Alert severity="info">
              No cross-service dependencies are recorded yet. A dependency
              appears when a child span references a parent span from a
              different service in the same trace. No connections are
              fabricated.
            </Alert>
          ) : (
            <Stack spacing={2}>
              {data.edges.map((edge) => (
                <Box key={`${edge.source}-${edge.target}`}>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    sx={{
                      alignItems: { xs: "flex-start", sm: "center" },
                      gap: 1.5,
                    }}
                  >
                    <Chip label={edge.source} variant="outlined" />
                    <Typography color="text.secondary">→</Typography>
                    <Chip
                      label={edge.target}
                      color="primary"
                      variant="outlined"
                    />
                    <Typography variant="body2" color="text.secondary">
                      {edge.calls} {edge.calls === 1 ? "call" : "calls"}
                    </Typography>
                  </Stack>
                  <Divider sx={{ mt: 2 }} />
                </Box>
              ))}
            </Stack>
          )}
        </CardContent>
      </Card>
    </Stack>
  );
}
