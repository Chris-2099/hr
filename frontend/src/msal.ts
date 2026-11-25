// MSAL.js wiring for "Sign in with Microsoft" - dormant until the backend's
// AUTH_MODE is "entra" or "hybrid" (see api.ts fetchAuthConfig() / Login.tsx).
// Safe to import even with no real Entra app registration yet: msalInstance
// is only ever used if the Login page's button is enabled, which only
// happens once AUTH_MODE says so.
import { PublicClientApplication, type Configuration } from "@azure/msal-browser";

const tenantId = import.meta.env.VITE_ENTRA_TENANT_ID ?? "";
const clientId = import.meta.env.VITE_ENTRA_CLIENT_ID ?? "";

const msalConfig: Configuration = {
  auth: {
    clientId: clientId || "00000000-0000-0000-0000-000000000000",
    authority: `https://login.microsoftonline.com/${tenantId || "common"}`,
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "sessionStorage",
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);

const LOGIN_SCOPES = ["openid", "profile", "email"];

export async function signInWithMicrosoft() {
  const result = await msalInstance.loginPopup({ scopes: LOGIN_SCOPES });
  return result;
}
