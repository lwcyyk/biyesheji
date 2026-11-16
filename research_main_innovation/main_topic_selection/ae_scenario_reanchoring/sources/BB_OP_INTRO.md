> ## Documentation Index
> Fetch the complete documentation index at: https://docs.browserbase.com/llms.txt
> Use this file to discover all available pages before exploring further.

# Introduction

> Securely log into websites in a Browserbase session using 1Password.

> [!NOTE]
>
> To let users approve personal logins in the 1Password desktop app and fill them through the browser extension, see [Agentic Autofill](https://docs.browserbase.com/integrations/1password/agentic-autofill.md). The guide below uses a service account and the 1Password SDK to retrieve credentials in your application.

By the end of this guide, your **Browserbase** agent will use **1Password** to log into a website, without hardcoding credentials into your code.

You'll learn how to:

1. Set up a 1Password vault for your credentials
2. Create a 1Password Service Account for programmatic access
3. Use the 1Password SDK to retrieve credentials from your vault
4. Automate website logins in your Browserbase session

## When you'd use this

Use the 1Password integration when you need to:

* Automate logins without storing raw credentials in code or environment files.
* Give your agent access to credentials in a secure, auditable way.
* Rotate passwords in your vault without updating scripts.
* Share access across team members without exposing sensitive data.

This is ideal for:

* Testing logins on staging environments
* Monitoring tools that need to log into internal dashboards
* AI agents that manage or navigate multiple accounts

## Prerequisites

Before you start, make sure you have:

* [A Browserbase account](https://www.browserbase.com/sign-up)
* [A 1Password account](https://start.1password.com/)

> The quickstart guide will walk you through creating a Service Account and setting up your vault.

## Quickstart guides

> [card] [Follow the guide](https://docs.browserbase.com/integrations/1password/quickstart.md)
>
> Follow the step-by-step quickstart guide to use your 1Password Service Account to automate your first login.

> [card] [Agentic Autofill](https://docs.browserbase.com/integrations/1password/agentic-autofill.md)
>
> Let users approve personal logins in 1Password and fill them through the browser extension.


This documentation is built and hosted on [Mintlify](https://mintlify.com), a developer documentation platform.