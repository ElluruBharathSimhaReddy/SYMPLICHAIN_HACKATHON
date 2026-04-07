# Mobile architecture recommendation

## Recommendation

Use **React Native with TypeScript** for the first customer-facing SymFlow mobile app.

## Why this is the best fit here

- The existing web team already works with React, so onboarding is faster.
- Business logic, API client code, validation rules, and design patterns can be shared between web and mobile.
- One codebase reduces delivery time and maintenance cost for an early-stage team.
- Native modules can still be added later for camera, offline sync, scanning, or performance-sensitive flows.

## Interaction model

Use a **primary tap-first workflow** with **optional voice shortcuts** for high-friction field operations.

### Recommended UX pattern

1. Large thumb-friendly buttons for common actions.
2. Camera-first screens for POD uploads.
3. Minimal forms with progressive disclosure.
4. Offline queue for low-connectivity environments.
5. Optional voice notes or speech-to-text for remarks, not for every step.

## App architecture

- **Mobile UI:** React Native + TypeScript
- **State management:** Redux Toolkit or Zustand
- **Networking:** Axios or Fetch wrapper with token refresh
- **Offline cache:** SQLite or MMKV for drafts and queued uploads
- **Media upload:** Multipart upload with retry and resume support
- **Auth:** JWT or session token with refresh flow
- **Crash/error tracking:** Sentry
- **Analytics:** lightweight product analytics for drop-off tracking

## High-level flow

1. User captures POD photo.
2. App compresses and stores metadata locally.
3. Upload job is queued locally.
4. App syncs when network is available.
5. Backend returns upload id and status.
6. Poll or socket event updates validation result.

## Why not fully speech-first

Speech is helpful for notes and quick actions, but logistics workflows still depend on scanning, image capture, and clear confirmations. A speech-first model would add noise in warehouses, roadside environments, and multilingual settings.
