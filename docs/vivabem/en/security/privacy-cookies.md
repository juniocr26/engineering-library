# Privacy Policy and Cookie Notice

[Catalog](../index.md) | [Português](../../pt-br/security/privacy-cookies.md)

Static verification on 2026-11-15 against VivaBem `031acf0`. This page describes the local implementation; it does not establish deployment, visual acceptance or legal approval.

## Privacy information

The Privacy Policy is at `/politica-de-privacidade`, linked from public and authenticated footers. The “aviso de cookies” button in its data-collection section opens the dialog without leaving the policy. The policy covers personal data use and rights; the supporting notice explains cookies in plain language. The notice mentions the policy but contains no return link.

The effective date comes from policy configuration (default: July 22, 2026), not the login date. The inspected flow has no document version identifier, version history or notice acceptance record. Published legal wording was preserved; its presence in source does not establish current specialist approval.

## Display lifecycle

| Event | Implemented behavior |
| --- | --- |
| Successful patient or psychologist login | Authenticates and marks the notice as pending. |
| Successful account activation | Automatically authenticates, redirects to the dashboard and supplies a success snackbar. |
| Successful password reset | Automatically authenticates, redirects to the dashboard and supplies a success snackbar. |
| Requesting a recovery link | Neither authenticates nor marks the notice as pending. |
| Logout followed by login | Invalidates the previous session; the new login marks a new display. |
| Existing authenticated session, authentication restoration, navigation and refresh | Do not create a new pending display by themselves. |

The first authenticated render of the dashboard or Pix-key screen consumes the pending marker and mounts the notice with automatic opening. Other pages do not consume it. Once consumed, navigation and refresh do not automatically reopen it; manual opening through the policy remains available. Consumption happens on server rendering, not on closing or confirmed reading: unavailable JavaScript or an unseen response can consume the marker without reading. This is not a guarantee of exactly one opening across concurrent requests.

## Reusable component

Blade mounts an Alpine.js component around a native HTML dialog. The policy uses its slot for the opening control; the authenticated layout reuses the same component in automatic mode. The dialog uses `showModal()`, a backdrop, an accessible title and a scrollable content region. Opening focuses the close button and locks background scrolling; Tab/Shift+Tab cycle through controls. Escape and the close button restore scrolling and focus to a still-connected trigger. Backdrop clicks do not close it.

The shared close button is circular and red, with a white X at the upper-right corner and an accessible label. Width and height are viewport bounded, with internal scrolling and smaller spacing/type on narrow screens. Theme variables provide light/dark colors and visible focus. These are source-verified properties, without browser or screen-reader testing in this review.

## Snackbar and visual priority

The intended order is page, backdrop, dialog and success snackbar. Opening temporarily moves the existing snackbar into the dialog through Alpine-controlled DOM mutation, restoring its position on close/destruction. This places it in the native dialog top layer; a page z-index alone would not solve that layering. Activation and password reset preserve their success messages through this path. Normal snackbar timing continues; the notice does not keep the message visible indefinitely.

## Information is not consent

The current notice has a short introduction and sections about necessary cookies, preferences and additional functionality, browser management, and privacy/data protection. It explains sessions, form protection, scheduling and services. Non-essential cookies are mentioned conditionally: this does not establish active optional categories or implemented choices. The current content has no comparison table, although table styles remain in the component.

Opening or closing the notice records no consent, acceptance, withdrawal, preferences or tracking authorization. This flow has no consent manager. Essential cookies support operation, authentication, sessions and security; blocking them can interrupt functionality and require another login. WebSocket, Redis, payments and professional presence are operational infrastructure, not optional cookie categories that users can freely disable while retaining full functionality.

## Limits and maintenance

Browser checks remain pending for both roles, manual/automatic opening, focus, Escape, mobile, themes and success messages above the dialog. Legal approval and any optional-cookie inventory/management require separate work; this documentation does not complete them. No application code or legal wording changed.
