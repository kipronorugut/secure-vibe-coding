# Firebase Audit Reference

Check `firestore.rules`, `database.rules.json` (Realtime Database) and `storage.rules` in the repo, and compare with what is deployed in the Firebase console — the console may differ from the files.

## How rules evaluate

- Rules are **OR'd**: if any `allow` matches, access is granted. A broad rule anywhere (e.g. on `{document=**}`) overrides careful rules elsewhere.
- Rules are **not filters**: a query must be constrained so every possible result is allowed, or it fails.
- The Admin SDK (server) bypasses rules entirely.

## Red flags

```
allow read, write: if true;                                   // open to the internet
allow read, write: if request.time < timestamp.date(2026, 12, 1); // "test mode"
allow read, write: if request.auth != null;                   // any signed-up user, all data
match /{document=**} { allow read, write: if request.auth != null; }
```

Realtime Database:
```json
{ "rules": { ".read": true, ".write": true } }
{ "rules": { ".read": "auth != null", ".write": "auth != null" } }
```

Storage:
```
allow read, write: if request.auth != null;   // every user reads every upload
```

Also flag:
- Users able to write fields like `role`, `isAdmin`, `plan`, `credits`, `ownerId`.
- No validation of document shape or size on create/update.
- Service-account JSON (`*-firebase-adminsdk-*.json`) in the repo or client bundle.

## Good baseline — Firestore

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    function signedIn() { return request.auth != null; }
    function isOwner(uid) { return signedIn() && request.auth.uid == uid; }

    // One document per user, keyed by uid
    match /users/{userId} {
      allow read: if isOwner(userId);
      allow create: if isOwner(userId)
        && request.resource.data.keys().hasOnly(['name', 'email', 'createdAt'])
        && request.resource.data.name is string
        && request.resource.data.name.size() < 100;
      allow update: if isOwner(userId)
        && !request.resource.data.diff(resource.data).affectedKeys()
              .hasAny(['role', 'plan', 'credits']);
      allow delete: if isOwner(userId);
    }

    // Documents owned via a field
    match /orders/{orderId} {
      allow read, delete: if signedIn() && resource.data.userId == request.auth.uid;
      allow create: if signedIn() && request.resource.data.userId == request.auth.uid;
      allow update: if signedIn()
        && resource.data.userId == request.auth.uid
        && request.resource.data.userId == resource.data.userId;   // can't change owner
    }

    // Default deny for everything else (implicit, but keep no broad wildcard allows)
  }
}
```

Admin/role checks: use **custom claims** set by the server (`request.auth.token.admin == true`), never a field the user can write.

## Good baseline — Storage

```
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /users/{userId}/{fileName} {
      allow read: if request.auth != null && request.auth.uid == userId;
      allow write: if request.auth != null && request.auth.uid == userId
        && request.resource.size < 5 * 1024 * 1024
        && request.resource.contentType.matches('image/.*');
    }
  }
}
```

## Verification

Use the Firebase Emulator Suite with `@firebase/rules-unit-testing`:

```ts
import { initializeTestEnvironment, assertFails, assertSucceeds } from "@firebase/rules-unit-testing";
import { readFileSync } from "node:fs";
import { doc, getDoc } from "firebase/firestore";

const env = await initializeTestEnvironment({
  projectId: "demo-rules-test",
  firestore: { rules: readFileSync("firestore.rules", "utf8") },
});

const alice = env.authenticatedContext("alice").firestore();
const anon = env.unauthenticatedContext().firestore();

await assertSucceeds(getDoc(doc(alice, "users/alice")));
await assertFails(getDoc(doc(alice, "users/bob")));   // cross-user read blocked
await assertFails(getDoc(doc(anon, "users/alice")));  // anonymous blocked
```

## Also recommended

- Restrict the web API key in Google Cloud Console (API restrictions, HTTP referrers). It is an identifier, not a secret, but restriction limits abuse.
- Enable App Check to reduce scripted abuse. It is not authorization — rules still must be correct.
- Set budget alerts in Google Cloud.
