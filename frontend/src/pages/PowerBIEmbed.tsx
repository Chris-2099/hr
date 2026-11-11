import { useEffect, useState } from "react";
import { PowerBIEmbed } from "powerbi-client-react";
import { models } from "powerbi-client";
import { api, ApiError } from "../api";
import { acquirePowerBIToken } from "../msal";

interface PublicConfigResponse {
  tenant_id: string;
  client_id: string;
  workspace_id: string;
  report_id: string;
}

interface EmbedConfigResponse {
  report_id: string;
  embed_url: string;
  access_token: string;
  token_type: string;
}

function looksLikePlaceholder(value: string): boolean {
  return !value || value.toLowerCase().includes("placeholder");
}

/**
 * React-shell-with-embedded-Power-BI-pages pattern, "embed for your
 * organization" (user-owns-data): the viewer signs into Microsoft
 * themselves via MSAL.js (src/msal.ts), and their own delegated Azure AD
 * token - not a service-principal token - is what Power BI uses to decide
 * what this person can see. Flow:
 *   1. GET backend config (tenant/client/workspace/report ids - all public,
 *      no secrets).
 *   2. MSAL popup login -> the user's own Power BI-scoped access token.
 *   3. POST that token to our backend, which forwards it to Power BI's
 *      REST API to fetch this report's embedUrl (app/routers/integrations.py).
 *   4. Render via Microsoft's own powerbi-client-react SDK.
 *
 * Never rendered a real report yet: needs a Power BI Pro license per
 * viewer (or Premium/Fabric capacity on the workspace), the Entra app
 * registration's SPA platform + delegated Power BI permission actually
 * configured in Azure AD, and a report actually published to the
 * workspace from Power BI Desktop. See README.md.
 */
export default function PowerBIEmbedPage() {
  const [config, setConfig] = useState<EmbedConfigResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string>("Loading configuration…");

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const publicConfig = await api.get<PublicConfigResponse>("/api/integrations/powerbi/config");
        if (looksLikePlaceholder(publicConfig.tenant_id) || looksLikePlaceholder(publicConfig.client_id)) {
          setError(
            "Entra app registration isn't configured yet (ENTRA_TENANT_ID/ENTRA_CLIENT_ID are still placeholders)."
          );
          return;
        }
        if (looksLikePlaceholder(publicConfig.workspace_id) || looksLikePlaceholder(publicConfig.report_id)) {
          setError("No Power BI workspace/report configured yet (POWERBI_WORKSPACE_ID/POWERBI_REPORT_ID).");
          return;
        }

        setStatus("Signing in with Microsoft…");
        const userToken = await acquirePowerBIToken(publicConfig.tenant_id, publicConfig.client_id);
        if (cancelled) return;

        setStatus("Loading report…");
        const embed = await api.post<EmbedConfigResponse>("/api/integrations/powerbi/embed-config", {
          user_access_token: userToken,
        });
        if (!cancelled) setConfig(embed);
      } catch (e) {
        if (!cancelled) setError(e instanceof ApiError ? e.message : e instanceof Error ? e.message : "Failed to load the report");
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div>
      <div className="page-header">
        <h2>Power BI (Embedded)</h2>
        <p>
          A published Power BI report, rendered inline with your own Microsoft sign-in — the same data this app's
          own dashboards read, for teams that want to keep building in Power BI Desktop directly.
        </p>
      </div>

      {error && (
        <div className="card">
          <h3>Not available yet</h3>
          <p className="card-subtitle">{error}</p>
        </div>
      )}

      {config && (
        <div className="card">
          <PowerBIEmbed
            embedConfig={{
              type: "report",
              id: config.report_id,
              embedUrl: config.embed_url,
              accessToken: config.access_token,
              tokenType: config.token_type === "Aad" ? models.TokenType.Aad : models.TokenType.Embed,
              // View-only by design: this org's users view reports, they
              // don't author them (that still happens in Power BI Desktop
              // by whoever has Contributor+ on the workspace). This forces
              // the embedded UI itself into read-only mode - it does NOT
              // change what the signed-in user could still do if they
              // opened the report directly in app.powerbi.com; that's
              // governed by their actual workspace role, not this setting.
              permissions: models.Permissions.Read,
              viewMode: models.ViewMode.View,
              settings: {
                panes: { filters: { visible: false }, pageNavigation: { visible: true } },
              },
            }}
            cssClassName="powerbi-embed-frame"
          />
        </div>
      )}

      {!error && !config && <div className="loading">{status}</div>}
    </div>
  );
}
