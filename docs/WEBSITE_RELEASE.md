# Public website release — 16 November 2026

## Delivered

German landing page, two-audience benefits, shared 20/5/20 illustration, property/resident journeys, responsibilities/load management, labelled conceptual app preview, payment flows, 11 accessible FAQs, business-model page, both open vacancy alternatives, interactive scenario comparison, local-only contact demo and factual project/privacy pages.

No changes to the tenant app. No actual enquiry destination, charger, NFC, account, payment or booking integration. The app hostname still serves a placeholder and is labelled accordingly. The site uses the approved vector logos, Liberation Sans, supplied concept garage image, icons and brand tokens. Full original kit/source archive remains outside the public root.

## Financial model

Counts initially N=20, O=20, P=5. S and R are blank until entered. Monetary results remain neutral until both are supplied; empty is not zero. Counts must be whole, N>=1, 0<=O<=N, 1<=P<=N. Invalid dependent counts are retained with a request to adjust them, never silently rewritten. Money must be finite and nonnegative; representability limits prevent overflow. Zero is valid, calculated negative contributions stay visible. Currency display is CHF, de-CH, two decimals.

- Continue: billable apartments = N; subscription = N×S.
- Pause: billable apartments = O; subscription = O×S.
- Rental uplift = O×R.
- Contribution = rental uplift − subscription, before other landlord costs, upfront payments, financing and tax effects.
- P changes only the infrastructure illustration, not subscriptions.

Fictional implementation-check values, **not VoltoShare prices**:

| N/O/P | S/R | Subscription A/B | Rental uplift | Contribution A/B |
| --- | --- | --- | --- | --- |
| 20/20/5 | 20/30 | 400/400 | 600 | 200/200 |
| 20/16/5 | 20/30 | 400/320 | 480 | 80/160 |
| 20/0/5 | 20/30 | 400/0 | 0 | -400/0 |

Seven focused Node tests pass these scenarios, P independence, blanks, zero/negative/nonfinite inputs, count bounds and decimal amounts. Browser acceptance checks cover rendered results, links, assets, direct routes, phone/tablet/desktop reflow, keyboard menu/FAQ, no-JS enquiry protection, inline validation, retained inputs, zero submission requests/storage and 200% CSS zoom. Exact completed run results are recorded below once deployment is verified.

## Remaining project decisions

1. Vacancy policy: neither continuation nor pause is agreed.
2. Subscription prices, provider markup, rent uplift, installation costs, initial payments, financing and tariff details.
3. Verified operating entity, address, contact/receiving destination, retention and complete publication/privacy information.
4. Actual tenant app implementation and any flat-rate-demo versus dynamic-commercial-tariff alignment.
5. Hardware/NFC/load-management integration, authentication, bookings, payments and property-management controls.
6. Building-specific capacity, usage rules and service commitments.

The current form requests fictional inputs and only validates them in-page. It does not submit, persist, mail or queue an enquiry. Self-hosted fonts and assets; no application analytics/cookies/storage. Hosting access metadata may be processed by the Pi and Cloudflare, as disclosed. This preview makes no claim of legal/commercial launch readiness.
