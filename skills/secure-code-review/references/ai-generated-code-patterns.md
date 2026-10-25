# AI-generated code: common security defects and fixes

Bad/good patterns are illustrative (TypeScript/Node unless noted). Apply the same idea in any stack.

## 1. Authorization / IDOR

**Bad — trusts the ID in the URL**
```ts
export async function GET(req, { params }) {
  const order = await db.order.findUnique({ where: { id: params.id } });
  return Response.json(order);
}
```

**Good — scoped to the session user**
```ts
export async function GET(req, { params }) {
  const session = await auth();
  if (!session) return new Response("Unauthorized", { status: 401 });
  const order = await db.order.findFirst({
    where: { id: params.id, userId: session.user.id },
  });
  if (!order) return new Response("Not found", { status: 404 });
  return Response.json(order);
}
```

Checks:
- [ ] Every server route/action calls the auth check itself (middleware alone can be bypassed by matcher gaps).
- [ ] Every query on user-owned data filters by owner/tenant.
- [ ] Admin routes check role on the server, from the database/session — not from a client-sent flag.
- [ ] `userId`, `ownerId`, `tenantId`, `role` are never read from the request body for authorization.
- [ ] Next.js server actions are treated as public POST endpoints (they are).
- [ ] Sequential/guessable IDs are not the only protection (UUIDs help but are not authorization).

## 2. Authentication

- [ ] Passwords hashed with bcrypt, scrypt or argon2 — never plain, MD5 or SHA-1/256 alone.
- [ ] JWTs are **verified** (`jwt.verify`, `jose.jwtVerify`), not just decoded; algorithm pinned; `exp` enforced.
- [ ] JWT secret is long and random, from env, not `"secret"` or a default.
- [ ] Session tokens in `HttpOnly`, `Secure`, `SameSite=Lax/Strict` cookies — not localStorage for high-value apps.
- [ ] Password reset tokens: single use, short expiry, not guessable, not logged.
- [ ] Login/reset responses don't reveal whether an email exists (where it matters).
- [ ] OAuth: `state` validated, redirect URIs allowlisted.
- [ ] OTP: limited attempts, short expiry, rate-limited sends.

## 3. Injection and XSS

**Bad**
```ts
db.$queryRawUnsafe(`SELECT * FROM users WHERE email = '${email}'`);
exec(`convert ${req.query.file} out.png`);
<div dangerouslySetInnerHTML={{ __html: comment.body }} />
```

**Good**
```ts
db.$queryRaw`SELECT * FROM users WHERE email = ${email}`;   // parameterized
execFile("convert", [safePath, "out.png"]);                  // no shell, validated path
<div>{comment.body}</div>                                     // escaped; or sanitize with DOMPurify
```

- [ ] No string-built SQL; ORM raw helpers use parameters.
- [ ] MongoDB: request objects not passed straight into filters (`{ email: req.body.email }` can receive `{ "$ne": null }`) — validate types.
- [ ] No `eval`, `new Function`, `vm` with user input.
- [ ] Markdown/HTML rendering sanitized.
- [ ] Server fetches of user-supplied URLs block internal ranges (SSRF): `169.254.169.254`, `localhost`, private IPs.

## 4. Validation and mass assignment

**Bad**
```ts
await db.user.update({ where: { id }, data: req.body });
```

**Good**
```ts
const Input = z.object({ name: z.string().max(100), bio: z.string().max(500) });
const data = Input.parse(await req.json());
await db.user.update({ where: { id: session.user.id }, data });
```

- [ ] Every server input validated with a schema; unknown fields stripped.
- [ ] Numeric limits (quantity, amount) enforce sensible min/max; no negatives where they make no sense.

## 5. Rate limiting and cost abuse

- [ ] Limits on login, signup, password reset, OTP/SMS send, contact forms.
- [ ] Per-user and per-IP limits on endpoints that call LLMs, SMS, email or other paid APIs.
- [ ] Hard monthly spend caps set in provider dashboards (OpenAI, Anthropic, Twilio, Africa's Talking, etc.).
- [ ] Serverless platforms: consider platform firewall/rate rules, not only in-memory limiters (which reset per instance).

## 6. AI / LLM features

- [ ] Model API keys server-side only.
- [ ] System prompt is not the access-control layer ("only answer for this user's data" is not enforcement — filter the data before it reaches the model).
- [ ] Retrieved documents (RAG) scoped to the requesting user/tenant.
- [ ] LLM output is never executed, never inserted as raw HTML, never used as SQL, and tool calls it triggers are validated and permission-checked.
- [ ] Prompt injection considered for any content the model reads from users, web pages, emails or files.
- [ ] Max tokens and per-user quotas set.

## 7. Webhooks and payments

- [ ] Signature verified with the provider SDK on the **raw** body (Stripe `constructEvent`, Paystack HMAC SHA-512, etc.).
- [ ] M-Pesa/Daraja callbacks: callback URL not guessable alone; confirm transactions by querying the provider (transaction status API) before fulfilling; validate amount and account reference.
- [ ] Idempotency — same event processed once.
- [ ] Price and amount computed server-side from product IDs; client-sent prices ignored.
- [ ] Fulfilment happens on verified webhook, not on the client redirect to a "success" page.

## 8. Files

- [ ] Allowed MIME types and extensions checked server-side; size limits set.
- [ ] Files stored in private buckets; served via short-lived signed URLs.
- [ ] Filenames generated server-side; no user-controlled paths.
- [ ] SVG/HTML uploads not served inline from the app's own domain.

## 9. Configuration and errors

- [ ] CORS: explicit origin allowlist; never `Access-Control-Allow-Origin: *` together with credentials; never reflect arbitrary `Origin`.
- [ ] Production: debug off, source maps not public (or accepted risk), no stack traces/DB errors in responses.
- [ ] Admin panels, API docs (`/docs`, `/swagger`), and DB tools not publicly reachable without auth.
- [ ] Default credentials changed.

## 10. Logging

- [ ] Auth failures, permission denials, admin actions, payment events logged with user ID and timestamp.
- [ ] Logs exclude passwords, tokens, API keys, full card numbers, national ID numbers.
