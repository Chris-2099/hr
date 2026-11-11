import { PublicClientApplication, type AccountInfo, type Configuration } from "@azure/msal-browser";

/**
 * "Embed for your organization" (user-owns-data) auth: each viewer signs
 * into Microsoft themselves, and Power BI enforces whatever permissions
 * their own account already has - no service principal involved. Requires
 * the Entra app registration (ENTRA_TENANT_ID/ENTRA_CLIENT_ID on the
 * backend) to have:
 *   1. A "Single-page application" platform/redirect URI added for this
 *      app's origin (in addition to whatever platform the rest of the
 *      app's own SSO login uses).
 *   2. The Power BI Service API's delegated permission "Report.Read.All"
 *      (or broader) granted, with admin consent.
 * Neither of those is code - they're Azure AD portal configuration.
 */
export const POWERBI_SCOPES = ["https://analysis.windows.net/powerbi/api/Report.Read.All"];

let msalInstance: PublicClientApplication | null = null;
let initPromise: Promise<PublicClientApplication> | null = null;

export function getMsalInstance(tenantId: string, clientId: string): Promise<PublicClientApplication> {
  if (msalInstance) return Promise.resolve(msalInstance);
  if (!initPromise) {
    const config: Configuration = {
      auth: {
        clientId,
        authority: `https://login.microsoftonline.com/${tenantId}`,
        redirectUri: window.location.origin,
      },
      cache: { cacheLocation: "sessionStorage" },
    };
    const instance = new PublicClientApplication(config);
    initPromise = instance.initialize().then(async () => {
      await instance.handleRedirectPromise();
      msalInstance = instance;
      return instance;
    });
  }
  return initPromise;
}

export async function acquirePowerBIToken(tenantId: string, clientId: string): Promise<string> {
  const instance = await getMsalInstance(tenantId, clientId);
  let account: AccountInfo | undefined = instance.getAllAccounts()[0];
  if (!account) {
    const result = await instance.loginPopup({ scopes: POWERBI_SCOPES });
    account = result.account ?? undefined;
  }
  try {
    const result = await instance.acquireTokenSilent({ scopes: POWERBI_SCOPES, account });
    return result.accessToken;
  } catch {
    const result = await instance.acquireTokenPopup({ scopes: POWERBI_SCOPES, account });
    return result.accessToken;
  }
}
