> ## Documentation Index
> Fetch the complete documentation index at: https://docs.browserbase.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Agentic Autofill

> Use 1Password Agentic Autofill to approve and fill logins in a Browserbase session.

Connect a user's 1Password account, get their approval in the desktop app, and fill logins in a Browserbase session. The 1Password extension fills and submits forms without returning credential values to your application.

## Prerequisites

* A [Browserbase account](https://www.browserbase.com/sign-up), API key, and project ID.
* Node.js and an application backend with a production HTTPS OAuth callback.
* Two separate 1Password accounts on `1password.com`:

| Account | Purpose |
| - | - |
| **Business** | Register your application's OAuth client. Choose Business rather than Teams. |
| **Individual or Families, US region** | Connect as the end user and approve logins from a personal vault. |

Save test logins in **Personal** for Individual accounts or **Private** for Families. Business accounts don't get the user consent screen, and 1Password doesn't offer shared-vault logins.

## Register a production OAuth client

An owner, administrator, or member of the Security group must create the client in your company's Business account.

**1. Open OAuth Application**

Open **Integrations > OAuth Application** in your Business account.

If the option is missing, ask your 1Password contact to enable it using an owner or administrator's email address.

**2. Add your application's name and icon**

Enter the display name and upload a PNG, JPEG, or GIF icon up to **1 MB**. Both appear on the consent screen and approval prompt.

You can't add an icon after creation. Register a new client if an existing client has no icon.

**3. Configure the OAuth client**

| Setting | Value |
| - | - |
| Redirect URL | Your production HTTPS callback, matching `redirect_uri` exactly. |
| Grant type | **Authorization code** |
| Scope | **Read credentials** |

1Password rejects localhost and custom URL schemes.

**4. Generate and store credentials**

Generate credentials and save the **client ID** and **client secret** in your backend secret store. 1Password shows the secret once.

Keep the Business account active: the approval prompt looks up your client's name and icon there.

## Connect a user

Implement the [authorization code flow with PKCE](https://www.1password.dev/agentic-autofill/partners/connect) behind your application's **Connect 1Password** button.

**1. Start authorization**

Send the user to [1Password's authorization endpoint](https://my.1password.com/oauth/authorize) with these scopes, separated by a space:

* `brokered-credentials:request-access`
* `brokered-credentials:read`

Generate a fresh, unpredictable `state` and PKCE verifier for each attempt. Use `code_challenge_method=S256` and keep the verifier on your backend.

For testing, use a private browser window and sign in to the personal account.

**2. Capture the callback**

Validate `state`, then read the callback values:

| Value | Location |
| - | - |
| `code` | Query string |
| `state` | Query string |
| `integration_key` | URL fragment, on first consent |

Read the fragment in browser code and securely persist the key through your authenticated backend. Then clear the fragment with `history.replaceState`.

**Store the key before exchanging the code.** Browsers don't send fragments to your server automatically, and 1Password delivers the key only once per connection.

**3. Exchange the code**

On your backend, set the `OP_OAUTH_*` variables to your registered client credentials, callback values, and PKCE verifier. Exchange the code with **HTTP Basic authentication only**:

```bash cURL theme={null}
curl --request POST https://api.1password.com/v1/oauth/token \
  --user "${OP_OAUTH_CLIENT_ID}:${OP_OAUTH_CLIENT_SECRET}" \
  --data-urlencode 'grant_type=authorization_code' \
  --data-urlencode "code=${OP_OAUTH_CODE}" \
  --data-urlencode "redirect_uri=${OP_OAUTH_REDIRECT_URI}" \
  --data-urlencode "code_verifier=${OP_OAUTH_CODE_VERIFIER}"
```

Keep the client secret on your backend. Don't also send `client_id` in the form body.

**4. Store and refresh tokens**

Store the tokens and integration key together, bound to the same user and connection.

| Value | Handling |
| - | - |
| Access token | Expires after **15 minutes**. Refresh before it expires. |
| Refresh token | Rotates on every use. Replace it atomically and serialize refreshes per user. |
| Integration key | Retain the existing key when a reconnect omits `integration_key`. |

Refresh at the same token endpoint using `grant_type=refresh_token`, the current `refresh_token`, and both scopes.

> [accordion] Reconnects and missing integration keys
>
> A reconnect can omit `integration_key` while the connection is active. Keep your stored key, verify it belongs to the same user and account, and never overwrite it with an empty value.
>
> If the key is lost, revoke the connection and connect again. See [Store keys and tokens](https://www.1password.dev/agentic-autofill/partners/keys-and-tokens).

## Upload the 1Password extension

Upload the extension once, then reuse its Browserbase upload ID for new sessions.

**1. Install dependencies**

```bash theme={null}
npm install @browserbasehq/sdk playwright-core
```

**2. Package and upload the extension**

Create a ZIP with `manifest.json` at the root, following [Browser extensions](https://docs.browserbase.com/platform/browser/core-features/browser-extensions.md).

Set `BROWSERBASE_API_KEY` in your environment and save this as `upload-extension.mjs`:

```javascript Node.js: upload-extension.mjs theme={null}
import fs from "node:fs";
import { Browserbase } from "@browserbasehq/sdk";

const bb = new Browserbase({ apiKey: process.env.BROWSERBASE_API_KEY });
const extension = await bb.extensions.create({
  file: fs.createReadStream("1password-extension.zip"),
});
console.log(extension.id);
```

Run the script to print the upload ID:

```bash theme={null}
node upload-extension.mjs
```

**3. Configure your backend**

| Environment variable | Value |
| - | - |
| `BROWSERBASE_API_KEY` | Your Browserbase API key. |
| `BROWSERBASE_PROJECT_ID` | Your Browserbase project ID. |
| `BROWSERBASE_EXTENSION_ID` | The upload ID printed by the script. |

The example discovers the 1Password service worker from its manifest. No separate Chrome extension ID is needed.

> [accordion] Network allowlist
>
> If your browser uses an outbound allowlist, permit these hosts:
>
> * `api.1password.com`
> * `crl.1passwordservices.com`
> * `my.1password.com`
>
> Also allow the [1Password telemetry hosts](https://www.1password.dev/agentic-autofill/partners/fill#allow-network-access).

## Request, approve, and fill a login

The example creates a Browserbase session, calls the extension over CDP, and verifies the website's destination after filling. Calls run in the **extension service worker**, where `globalThis.api` is available.

### Configure the sign-in function

Save the complete example below as `agentic-autofill.mjs`. Call its `signIn` function from your backend with these arguments:

| Argument | Purpose |
| - | - |
| `getAccessToken` | Backend function that returns a current token, refreshing when necessary. Called before each 1Password operation. |
| `integrationKey` | The same user's integration key, loaded from your secret store. |
| `loginUrl` | HTTPS page containing the login form. |
| `successUrl` | Expected HTTPS destination after sign-in. |
| `showApproval` | UI hook that displays the opaque `appLink` to the authenticated user and resolves when they open it. |

Keep the client secret and refresh token on your backend. Deliver approval links through your authenticated application, outside model context and logs.

> [accordion] Try the public demo login
>
> Save the public login shown on [this test website](https://the-internet.herokuapp.com/login) in your personal vault, then use:
>
> | Argument | Value |
> | - | - |
> | `loginUrl` | `https://the-internet.herokuapp.com/login` |
> | `successUrl` | `https://the-internet.herokuapp.com/secure` |

### Follow the approval flow

**1. Request the logins**

Describe the task and the websites it needs. Each access request supports **one to five logins**.

1Password returns an access request, entry IDs, and an approval link. See [Create an access request](https://www.1password.dev/agentic-autofill/partners/access-requests) for field limits.

**2. Get the user's approval**

Open the approval link on the computer running the 1Password desktop app, signed in to the connected personal account. The prompt closes after **two minutes**.

Start checking status when the user opens the link. Use one checker per request and stop on every final state.

**3. Fill and verify the login**

Match the granted login by `entryId`, then pass its reference unchanged to `fillCredential`.

The example checks the destination's origin and path against `successUrl` after the fill returns. Add further task actions after verification, before cleanup.

> [accordion] Approval polling schedule
>
> | Time since the user opened the link | Check interval |
> | - | - |
> | First 5 seconds | Wait. |
> | 5–30 seconds | Every 2 seconds. |
> | 30–60 seconds | Every 5 seconds. |
> | 1–2 minutes | Every 10 seconds. |
> | After 2 minutes | Stop and wait for the user. |
>
> On `rateLimitExceeded`, wait at least one minute before checking again.
>
> If the request remains pending, wait for the user to say they've approved, then check once more. Create a new request only if it is still pending. Keep the request ID and entry IDs to support this continuation.
>
> Users can skip requested entries or add other logins, so match grants by `entryId` rather than array position. See [Get the user's approval](https://www.1password.dev/agentic-autofill/partners/approval).

> [accordion] Complete Node.js example: agentic-autofill.mjs
>
> ```javascript Node.js: agentic-autofill.mjs theme={null}
> import { Browserbase } from "@browserbasehq/sdk";
> import { chromium } from "playwright-core";
>
> const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
>
> function unwrap(response) {
>   if (!response.success) {
>     throw Object.assign(new Error(response.error.code), {
>       code: response.error.code,
>     });
>   }
>   return response.result;
> }
>
> async function findOnePasswordWorker(context) {
>   const deadline = Date.now() + 30_000;
>   while (Date.now() < deadline) {
>     for (const worker of context.serviceWorkers()) {
>       if (!worker.url().startsWith("chrome-extension://")) continue;
>       try {
>         const isOnePassword = await worker.evaluate(
>           () => chrome.runtime.getManifest().short_name === "1Password",
>         );
>         if (isOnePassword) return worker;
>       } catch {
>         // A starting service worker may be replaced. Check again.
>       }
>     }
>     await sleep(500);
>   }
>   throw new Error("1Password extension service worker not found");
> }
>
> async function waitForDecision(checkStatus) {
>   const openedAt = Date.now();
>   while (true) {
>     const elapsed = Date.now() - openedAt;
>     if (elapsed >= 120_000) return null;
>     const delay =
>       elapsed < 5_000
>         ? 5_000 - elapsed
>         : elapsed < 30_000
>           ? 2_000
>           : elapsed < 60_000
>             ? 5_000
>             : 10_000;
>     await sleep(delay);
>     if (Date.now() - openedAt >= 120_000) return null;
>     try {
>       const status = await checkStatus();
>       if (status.state !== "pending") return status;
>     } catch (error) {
>       if (error.code === "rateLimitExceeded") {
>         await sleep(60_000);
>       } else if (error.code !== "timeout" && error.code !== "networkError") {
>         throw error;
>       }
>     }
>   }
> }
>
> export async function signIn({
>   getAccessToken,
>   integrationKey,
>   loginUrl,
>   successUrl,
>   showApproval,
> }) {
>   const expected = new URL(successUrl);
>   if (
>     new URL(loginUrl).protocol !== "https:" ||
>     expected.protocol !== "https:"
>   ) {
>     throw new Error("Use HTTPS login and success URLs");
>   }
>   const bb = new Browserbase({ apiKey: process.env.BROWSERBASE_API_KEY });
>   const projectId = process.env.BROWSERBASE_PROJECT_ID;
>   const session = await bb.sessions.create({
>     projectId,
>     extensionId: process.env.BROWSERBASE_EXTENSION_ID,
>     timeout: 600,
>     browserSettings: { recordSession: false, logSession: false },
>   });
>   let browser;
>
>   try {
>     browser = await chromium.connectOverCDP(session.connectUrl);
>     const context = browser.contexts()[0];
>     if (!context) throw new Error("Browserbase browser context not found");
>     const worker = await findOnePasswordWorker(context);
>
>     await worker.evaluate(async () => {
>       const initialization = globalThis.api?.initialization?.v1;
>       if (!initialization?.whenSettled) {
>         throw new Error("1Password initialization API is unavailable");
>       }
>       let timer;
>       try {
>         const state = await Promise.race([
>           initialization.whenSettled(),
>           new Promise((_, reject) => {
>             timer = setTimeout(
>               () => reject(new Error("1Password initialization timed out")),
>               20_000,
>             );
>           }),
>         ]);
>         if (state !== "ready") {
>           throw new Error("1Password extension initialization failed");
>         }
>       } finally {
>         clearTimeout(timer);
>       }
>       const api = globalThis.api;
>       const methods = [
>         "createAccessRequest",
>         "getAccessRequestStatus",
>         "fillCredential",
>       ];
>       if (
>         typeof api.agenticMode?.v1?.enable !== "function" ||
>         !methods.every(
>           (method) => typeof api.agenticAutofill?.v1?.[method] === "function",
>         )
>       ) {
>         throw new Error("1Password Agentic Autofill API is unavailable");
>       }
>       const enabled = await api.agenticMode.v1.enable();
>       if (!enabled.success) throw new Error(enabled.error.code);
>     });
>
>     // Runs only in your backend; secrets are passed as evaluation arguments.
>     const callAutofill = async (method, parameters) =>
>       unwrap(
>         await worker.evaluate(
>           ({ method, ...args }) =>
>             globalThis.api.agenticAutofill.v1[method](args),
>           {
>             ...parameters,
>             method,
>             accessToken: await getAccessToken(),
>             integrationKey,
>           },
>         ),
>       );
>
>     const page = await context.newPage();
>     await page.goto(loginUrl, {
>       waitUntil: "domcontentloaded",
>       timeout: 30_000,
>     });
>     const created = await callAutofill("createAccessRequest", {
>       requests: {
>         version: 2,
>         goal: "Test a website sign-in",
>         entries: [
>           {
>             type: "login",
>             parameters: { website: loginUrl },
>             reason: "Sign in to verify the Browserbase integration",
>           },
>         ],
>       },
>     });
>
>     // Your UI hook resolves when the user opens the approval link.
>     await showApproval(created.appLink);
>
>     // Keep the CDP connection open and use one checker per request.
>     const status = await waitForDecision(() =>
>       callAutofill("getAccessRequestStatus", {
>         accessRequestUUID: created.accessRequest.id,
>       }),
>     );
>
>     if (!status) throw new Error("Approval still pending; wait for the user");
>     if (status.state !== "resolved") {
>       throw new Error(`Access request ended: ${status.state}`);
>     }
>     const entry = created.accessRequest.entries[0];
>     const grant = status.resolved.find(({ entryId }) => entryId === entry.id);
>     if (!grant) throw new Error("No login granted for the requested entry");
>
>     const tabUrl = page.url();
>     const tabId = await worker.evaluate(async (url) => {
>       const tabs = (await chrome.tabs.query({})).filter(
>         (tab) => tab.url === url,
>       );
>       if (tabs.length !== 1 || typeof tabs[0].id !== "number") {
>         throw new Error("Cannot identify login tab");
>       }
>       return tabs[0].id;
>     }, tabUrl);
>
>     // Pause all agent page reads and screenshots until this call returns.
>     const filled = await callAutofill("fillCredential", {
>       resourcePath: grant.reference,
>       tabId,
>     });
>
>     if (filled.status !== "fill_submitted") {
>       throw new Error("Unexpected fill status");
>     }
>     // Verify navigation only after the extension has finished the fill.
>     await page.waitForURL(
>       (url) =>
>         url.origin === expected.origin && url.pathname === expected.pathname,
>       { waitUntil: "domcontentloaded", timeout: 15_000 },
>     );
>     console.log(filled.status);
>     console.log("Website login verified");
>     return { status: filled.status, websiteLoginVerified: true };
>   } finally {
>     try {
>       await browser?.close();
>     } finally {
>       await bb.sessions.update(session.id, {
>         projectId,
>         status: "REQUEST_RELEASE",
>       });
>     }
>   }
> }
> ```

## Expected output

After approval, a successful fill, and navigation to `successUrl`:

```text theme={null}
fill_submitted
Website login verified
```

* **`fill_submitted`**: The extension filled and submitted the form, then removed the filled values before returning.
* **`Website login verified`**: The destination's origin and path match `successUrl`. The example throws if the page isn't reached within **15 seconds**.

Choose a destination available only after sign-in. If the website stays on the same URL, replace the destination check with a site-specific signed-in indicator after the fill returns.

> [accordion] Multi-page sign-in
>
> Fill the same granted reference on each username, password, or one-time-password page before verifying the final destination. Pause page reads during every fill.

## Troubleshooting

| Symptom or code | What to check |
| - | - |
| No consent screen | Use an Individual or Families account in the US region, separate from the Business account holding the client. |
| No approval prompt | Open the link on the computer running 1Password. Confirm the Business account holding the client is active. |
| No logins offered | Save the Login item in the user's Personal or Private vault with the requested website. |
| Service worker not found or API missing | Check the uploaded extension and access to `my.1password.com`. Wait for initialization. |
| `agenticModeNotEnabled` | Enable Agentic Mode for the tab or whole browser and check the response. |
| `fillFailed` | Refresh the token, check the grant's connection, and navigate to the login form. |
| `autosubmitFailed` | Report the website and error code to your 1Password contact. The extension clears the values it filled. |
| `rateLimitExceeded` | Wait at least a minute. Use one checker per request and follow the approval schedule. |

See the [extension API](https://www.1password.dev/agentic-autofill/partners/extension-api) and [troubleshooting reference](https://www.1password.dev/agentic-autofill/partners/troubleshooting). Share error codes without tokens, keys, or approval links.

## Zero data retention (ZDR)

The example disables session recording and logging when it creates the Browserbase session:

| Browser setting | Value | Effect |
| - | - | - |
| `recordSession` | `false` | Browserbase does not persist session recordings. |
| `logSession` | `false` | Browserbase does not persist session logs. |

Read the [ZDR guide](https://docs.browserbase.com/account/enterprise/zero-data-retention.md) for the full scope. Downloads, uploads, contexts, and extensions are separate artifacts; use [Bring Your Own Storage](https://docs.browserbase.com/account/enterprise/byos-setup-guide.md) to store them in your own AWS account.

Configure retention for your application's logs and model provider separately.

## Related guides

> [card] [Browser extensions](https://docs.browserbase.com/platform/browser/core-features/browser-extensions.md)
>
> Upload and run extensions in Browserbase sessions.

> [card] [Website authentication](https://docs.browserbase.com/platform/identity/authentication.md)
>
> Manage sign-in flows and reuse authenticated browser state.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.