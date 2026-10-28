
import { useEffect, useState } from "react";
import api from "../services/api";

type WorkspaceSettingsData = {
  id?: number;
  workspace_name: string;
  description: string;
  environment: "development" | "staging" | "production";
  timezone: string;
  refresh_interval: number;
  notification_preferences: {
    email?: boolean;
    alerts?: boolean;
    [key: string]: boolean | undefined;
  };
};

const initialSettings: WorkspaceSettingsData = {
  workspace_name: "Observability Workspace",
  description: "Monitor services, telemetry, and application health.",
  environment: "development",
  timezone: "Asia/Kolkata",
  refresh_interval: 30,
  notification_preferences: {
    email: false,
    alerts: false,
  },
};

const inputStyle: React.CSSProperties = {
  width: "100%",
  padding: "10px 12px",
  border: "1px solid #d1d5db",
  borderRadius: "8px",
  fontSize: "14px",
  boxSizing: "border-box",
  background: "white",
  color: "#111827",
};

const labelStyle: React.CSSProperties = {
  display: "block",
  marginBottom: "7px",
  fontSize: "14px",
  fontWeight: 600,
  color: "#374151",
};

export default function WorkspaceSettings() {
  const [settings, setSettings] =
    useState<WorkspaceSettingsData>(initialSettings);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<
    "success" | "error" | ""
  >("");

  useEffect(() => {
    let active = true;

    async function loadSettings() {
      try {
        const response = await api.get<WorkspaceSettingsData>("/settings");

        if (active) {
          setSettings({
            ...response.data,
            description: response.data.description ?? "",
            notification_preferences:
              response.data.notification_preferences ?? {},
          });
        }
      } catch (error) {
        console.error("Failed to load workspace settings:", error);

        if (active) {
          setMessage(
            "Could not load settings from the server. Please check that the backend is running and try again.",
          );
          setMessageType("error");
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadSettings();

    return () => {
      active = false;
    };
  }, []);

  function updateField<K extends keyof WorkspaceSettingsData>(
    field: K,
    value: WorkspaceSettingsData[K],
  ) {
    setSettings((previous) => ({
      ...previous,
      [field]: value,
    }));
    setMessage("");
    setMessageType("");
  }

  function updateNotification(
    field: "email" | "alerts",
    checked: boolean,
  ) {
    setSettings((previous) => ({
      ...previous,
      notification_preferences: {
        ...previous.notification_preferences,
        [field]: checked,
      },
    }));
    setMessage("");
    setMessageType("");
  }

  async function handleSave(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setSaving(true);
    setMessage("");
    setMessageType("");

    try {
      const payload = {
        workspace_name: settings.workspace_name.trim(),
        description: settings.description.trim() || null,
        environment: settings.environment,
        timezone: settings.timezone,
        refresh_interval: settings.refresh_interval,
        notification_preferences: settings.notification_preferences,
      };

      const response = await api.put<WorkspaceSettingsData>(
        "/settings",
        payload,
      );

      setSettings({
        ...response.data,
        description: response.data.description ?? "",
        notification_preferences:
          response.data.notification_preferences ?? {},
      });

      setMessage("Workspace settings saved successfully.");
      setMessageType("success");
    } catch (error: any) {
      console.error("Failed to save workspace settings:", error);

      const detail = error?.response?.data?.detail;
      const errorMessage = Array.isArray(detail)
        ? detail.map((item: { msg?: string }) => item.msg ?? "Invalid input").join(", ")
        : typeof detail === "string"
          ? detail
          : "Could not save settings. Please check your backend connection and try again.";

      setMessage(errorMessage);
      setMessageType("error");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div style={{ padding: 32, color: "#6b7280" }}>
        Loading workspace settings...
      </div>
    );
  }

  return (
    <div
      style={{
        maxWidth: 900,
        margin: "0 auto",
        padding: "28px",
        color: "#111827",
      }}
    >
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 28, margin: "0 0 8px" }}>
          Workspace Settings
        </h1>
        <p style={{ margin: 0, color: "#6b7280", lineHeight: 1.6 }}>
          Configure your observability workspace and monitoring preferences.
        </p>
      </div>

      {message && (
        <div
          role="status"
          style={{
            padding: "12px 16px",
            borderRadius: 8,
            marginBottom: 20,
            background: messageType === "success" ? "#ecfdf5" : "#fef2f2",
            color: messageType === "success" ? "#065f46" : "#991b1b",
            border:
              messageType === "success"
                ? "1px solid #a7f3d0"
                : "1px solid #fecaca",
          }}
        >
          {message}
        </div>
      )}

      <form onSubmit={handleSave}>
        <section
          style={{
            padding: 24,
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            marginBottom: 20,
            background: "#ffffff",
          }}
        >
          <h2 style={{ fontSize: 18, margin: "0 0 22px" }}>
            General Settings
          </h2>

          <div style={{ marginBottom: 20 }}>
            <label htmlFor="workspace-name" style={labelStyle}>
              Workspace Name
            </label>
            <input
              id="workspace-name"
              style={inputStyle}
              value={settings.workspace_name}
              onChange={(event) =>
                updateField("workspace_name", event.target.value)
              }
              required
              minLength={1}
              maxLength={100}
            />
          </div>

          <div style={{ marginBottom: 20 }}>
            <label htmlFor="workspace-description" style={labelStyle}>
              Description
            </label>
            <textarea
              id="workspace-description"
              style={{ ...inputStyle, minHeight: 90, resize: "vertical" }}
              value={settings.description}
              onChange={(event) =>
                updateField("description", event.target.value)
              }
              maxLength={500}
              rows={3}
            />
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 20,
            }}
          >
            <div>
              <label htmlFor="environment" style={labelStyle}>
                Environment
              </label>
              <select
                id="environment"
                style={inputStyle}
                value={settings.environment}
                onChange={(event) =>
                  updateField(
                    "environment",
                    event.target.value as WorkspaceSettingsData["environment"],
                  )
                }
              >
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="production">Production</option>
              </select>
            </div>

            <div>
              <label htmlFor="timezone" style={labelStyle}>
                Timezone
              </label>
              <select
                id="timezone"
                style={inputStyle}
                value={settings.timezone}
                onChange={(event) =>
                  updateField("timezone", event.target.value)
                }
              >
                <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                <option value="UTC">UTC</option>
                <option value="America/New_York">
                  America/New_York
                </option>
                <option value="Europe/London">Europe/London</option>
              </select>
            </div>

            <div>
              <label htmlFor="refresh-interval" style={labelStyle}>
                Refresh Interval
              </label>
              <select
                id="refresh-interval"
                style={inputStyle}
                value={String(settings.refresh_interval)}
                onChange={(event) =>
                  updateField("refresh_interval", Number(event.target.value))
                }
              >
                <option value="15">15 seconds</option>
                <option value="30">30 seconds</option>
                <option value="60">60 seconds</option>
                <option value="300">5 minutes</option>
              </select>
            </div>
          </div>
        </section>

        <section
          style={{
            padding: 24,
            border: "1px solid #e5e7eb",
            borderRadius: 12,
            marginBottom: 24,
            background: "#ffffff",
          }}
        >
          <h2 style={{ fontSize: 18, margin: "0 0 8px" }}>
            Notification Preferences
          </h2>
          <p
            style={{
              fontSize: 14,
              color: "#6b7280",
              margin: "0 0 20px",
            }}
          >
            Save your preferred notification options for this workspace.
          </p>

          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              marginBottom: 16,
              cursor: "pointer",
            }}
          >
            <input
              type="checkbox"
              checked={settings.notification_preferences.email ?? false}
              onChange={(event) =>
                updateNotification("email", event.target.checked)
              }
            />
            <span>Email notifications</span>
          </label>

          <label
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              cursor: "pointer",
            }}
          >
            <input
              type="checkbox"
              checked={settings.notification_preferences.alerts ?? false}
              onChange={(event) =>
                updateNotification("alerts", event.target.checked)
              }
            />
            <span>Alert notifications</span>
          </label>
        </section>

        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <button
            type="submit"
            disabled={saving}
            style={{
              padding: "11px 22px",
              border: "none",
              borderRadius: 8,
              background: saving ? "#9ca3af" : "#2563eb",
              color: "#ffffff",
              fontSize: 14,
              fontWeight: 600,
              cursor: saving ? "not-allowed" : "pointer",
            }}
          >
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </div>
      </form>
    </div>
  );
}
