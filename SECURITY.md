# Security policy

Please report vulnerabilities privately through GitHub: **Security tab > Report a vulnerability**.
Do not open a public issue. You will get a reply within a few days.

In scope: authentication, row-level security, Edge Functions, the GitHub Actions workflows and
anything that could expose another user's CV or stored AI key. Please do not test against other
people's accounts or send automated traffic at the live site.

Running your own copy: set `ALLOWED_ORIGIN` for the Edge Functions, use your own Supabase project and
secrets, use a fine-grained `GITHUB_PAT` limited to this repo (Actions: write), and protect `main`.
