---
title: VRMXT Package Delivery
aliases:
  - VRMXTPKG gateway
  - VRMXT Package session
tags:
  - extended-vrm
  - spec/package
  - format/vrmxtpkg
type: specification
status: draft
---

# VRMXT Package Delivery

Provider-neutral access to protected packages. Conforms to
[VRMXT Package Format](README.md). Transport adapters (Cloudflare, Node,
Vite middleware) are non-normative.

Index field `delivery.profile`:

| Value | Keys | Expiry |
|-------|------|--------|
| `session` (default if omitted) | Gateway wrap; not in the file | Session `expiresAt` (gateway clock). **The file does not expire.** |
| `static` | `embeddedChunkKeys` in the signed index | None. File is self-contained. |

The rest of this document is the **session** HTTP contract. `static` packages MUST NOT
require these endpoints. A consumer MUST load `static` packages from the file alone
after signature verification.

## Roles (session)

| Role | Owns |
|------|------|
| Client | Ephemeral P-256 key pair, fetch, abort |
| Gateway | Session, server time, key wrap, authorization |
| Chunk store | Encrypted bytes; no long-lived public ACLs |

The session client MUST NOT receive reusable content keys or unsigned storage URLs that
outlive the session.

## Static profile

No `POST /v1/session`. No TTL. Watermark variant MAY be chosen locally (any variant
whose key is in `embeddedChunkKeys`). Forensic session binding does not apply.

Distributors MUST assume the ciphertext is public. Use `session` when keys must stay
off static hosts (GitHub Pages cannot run this gateway).

## Session

`POST /v1/session`

Request JSON:

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `packageId` | string | yes | Index `packageId` |
| `clientPublicKey` | string | yes | P-256 public key (JWK or COSE) |
| `challenge` | string | no | Bot/captcha token defined by the adapter |

Response JSON:

| Property | Type | Required | Meaning |
|----------|------|----------|---------|
| `sessionId` | string | yes | Opaque id |
| `expiresAt` | string | yes | RFC 3339, gateway clock |
| `packageId` | string | yes | Echo |
| `indexUrl` | string | yes | Header+index or index-only `.vrmxtpkg` |
| `wrappedKeys` | object[] | yes | Per-chunk wrapped AES keys |
| `watermarkSelection` | object | if carriers | Bits for this session |
| `chunkBaseUrl` | string | if `SPLIT` | Prefix for chunk GET |

`wrappedKeys[]`: `{ "chunkId": string, "wrapped": string }` (base64 ciphertext of the
AES content key, wrap AAD = `sessionId|packageId|chunkId|expiresAt`).

The gateway MAY set a `HttpOnly; Secure; SameSite=Lax` cookie with an opaque session
handle. Cookie is an adapter choice. Bearer `sessionId` in `Authorization` is also
allowed.

Suggested TTL: 5–10 minutes. Adapters MUST rate-limit session creation per IP.

## Chunk fetch

`GET /v1/chunks/{packageId}/{chunkId}`

Headers: session cookie or `Authorization: Bearer <sessionId>`.

Gateway MUST verify:

1. Session exists and `expiresAt` is in the future (gateway clock).
2. `packageId` matches the session.
3. `chunkId` is in the signed index.
4. If watermarked, the chunk variant matches `watermarkSelection`.

Response: raw ciphertext body. Headers:

```
Cache-Control: private, no-store
X-Content-Type-Options: nosniff
```

Content-Type: `application/octet-stream`.
CORS: adapter-defined allowlist; credentials if cookie auth.

The gateway MUST NOT support byte-range requests that leak other variants in this draft.

## Errors

| Status | Meaning |
|--------|---------|
| 401 | No or invalid session |
| 403 | Session valid but chunk/variant not allowed |
| 404 | Unknown package or chunk |
| 410 | Session expired |
| 429 | Rate limit |

Expired sessions MUST use 410 (or 401). Clients MUST NOT retry wrap with a stale
session; they MAY request a new session subject to rate limits.

## Client clock

Clients MUST treat `expiresAt` as informational. Authorization is gateway-side.
A client MUST abort in-flight fetches when the user navigates away (AbortSignal).

## Dev adapter

A local Vite or Node handler MAY serve unencrypted packages without wrap for
development. Production configs MUST NOT enable that mode.

## Open questions

- [ ] Challenge / bot signal (Turnstile, etc.)
- [ ] Binding session to origin / referrer
- [ ] HTTP 103 or streaming index

## Related

- [Protection](protection.md)
- [Watermark](watermark.md)
- [Implementation](../../../implementations/vrmxt-package.md)
