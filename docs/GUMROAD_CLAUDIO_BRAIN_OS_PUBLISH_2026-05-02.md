# Gumroad Publish Evidence: Claudio OS / Brain OS v1

Date: 2026-05-02

## Scope

This evidence note covers only the Gumroad product `Claudio OS / Brain OS v1`.
It does not authorize broad Gumroad publishing, Cloudflare deploys, social posts,
private game publishing, or publication of the full Claudio workspace.

## Product

- Name: `Claudio OS / Brain OS v1`
- Product ID: `oSI0B6uSKk9ROGyHTsC0tQ==`
- Public URL verified: `https://lrgonzalez.gumroad.com/l/oklvqt`
- Planned slug not used by Gumroad: `https://lrgonzalez.gumroad.com/l/claudio-brain-os`
- Price: `900` cents USD
- File attached: yes
- Gumroad API state after enable: `published=true`
- `shown_on_profile`: not returned as true by API

## Package Evidence

- Package: `products/gumroad_packages/claudio_os_brain_os_v1.zip`
- Size: `18503` bytes
- SHA256: `b4f5fbc10af1d4a4c6bd609458013eb6fc81e2326a08fc02b0811b3f73cf5675`

## Verification Commands

```powershell
python tools\publish_brain_os_gumroad_draft.py --execute --with-file --publish
```

Result before explicit enable: Gumroad accepted the update and file upload, but
returned `published=false`.

```powershell
PUT https://api.gumroad.com/v2/products/<product_id>/enable
```

Result after explicit enable: Gumroad returned `success=true` and
`published=true` for the exact product above.

```powershell
Invoke-WebRequest https://lrgonzalez.gumroad.com/l/oklvqt
```

Public URL verification: HTTP 200 and page content includes the product title.

## Boundaries

- Old broad Gumroad publisher scripts were not used.
- Hardcoded or local Gumroad credential files were not staged.
- The private game, TCG, full canon vault, local runtime, and full workspace are
  excluded from this publication.
- The public URL is the Gumroad-assigned URL `oklvqt`; do not advertise
  `claudio-brain-os` unless the dashboard is later changed and reverified.
