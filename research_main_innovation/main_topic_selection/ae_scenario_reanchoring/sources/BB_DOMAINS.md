> ## Documentation Index
> Fetch the complete documentation index at: https://docs.browserbase.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Allowed Domains

> Restrict session navigation to an allowlist of domains

Allowed domains let you restrict which websites a session can navigate to. If you pass one or more domains, Browserbase blocks top-level page navigations to any domain not on the list. This keeps automated sessions focused and prevents unintended navigation.

> [!NOTE]
>
> This feature is experimental and its behavior may change in future releases.

## Restricting navigation

Use the `allowedDomains` field in `browserSettings` when creating a session to specify which domains are permitted. Below are examples in both Node.js and Python SDKs.

> [tab] Node.js
>
> ```typescript Node.js theme={null}
> import Browserbase from "@browserbasehq/sdk";
>
> const bb = new Browserbase({ apiKey: process.env.BROWSERBASE_API_KEY! });
>
> async function createSession() {
>   const session = await bb.sessions.create({
>     browserSettings: {
>       allowedDomains: ["example.com", "docs.example.com"],
>     },
>   });
>   console.log(`Session URL: https://browserbase.com/sessions/${session.id}`);
>   return session;
> }
>
> const session = createSession();
> ```

> [tab] Python
>
> ```python Python theme={null}
> from browserbase import Browserbase
> import os
>
> bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])
>
>
> def createSession():
>     session = bb.sessions.create(
>         browser_settings={
>             "allowedDomains": [
>                 "example.com",
>                 "docs.example.com",
>             ],
>         }
>     )
>     print(f"Session URL: https://browserbase.com/sessions/{session.id}")
>     return session
>
>
> session = createSession()
> ```

> [!NOTE]
>
> **Limitations:**
>
> * **Subdomain matching:** Adding `example.com` also permits `www.example.com`, `a.b.example.com`, and any other subdomain. You do not need to list subdomains separately.
> * **Top-frame navigation only:** Browserbase checks top-frame navigations. It does not block iframe/subframe loads or in-page resource requests (images, scripts, XHR, etc.).
> * **HTTP(S) domains only:** Browserbase does not apply the allowlist to navigations to `about:blank`, `chrome://`, `file://`, and similar URLs.

For a full list of session options and configuration fields, check out the [API reference for creating a session](https://docs.browserbase.com/reference/api/create-a-session.md).

## Related guides

> [card] [IP allowlisting](https://docs.browserbase.com/platform/browser/security/ip-allowlisting.md)
>
> Configure network access for your browser workflows.

> [card] [Security](https://docs.browserbase.com/account/enterprise/security.md)
>
> Review Browserbase security practices.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.