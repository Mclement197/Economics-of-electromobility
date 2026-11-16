# VoltoShare: design and implementation specification

**Version:** 2.0  
**Prepared:** 16 November 2026  
**Audience:** OpenClaw implementation agent and project team  
**Deliverable:** A public website and a responsive tenant-app demonstration sharing the supplied VoltoShare identity.

The bundled `index.html` is an interactive local design reference. The JSON and CSS files are reusable implementation inputs. This guide retains the detailed product requirements and distinguishes the preview from later operational integrations.

## 1. Start here

### Packaged implementation inputs

| File | Use |
|---|---|
| `OPENCLAW_IMPLEMENTATION_GUIDE.md` | Complete AI implementation brief and acceptance criteria |
| `implementation-guide.html` | The same specification formatted for reading |
| `index.html` | Interactive local website and resident interface reference |
| `tokens.css` | Shared palette, typeface declarations and core CSS variables |
| `design-tokens.json` | Structured design decisions for implementation |
| `demo-data.json` | Canonical fictional records and fixed demo clock |

Open `index.html` from the extracted folder. It uses relative assets, inline JavaScript and inline demo fixtures so it works without a server or CDN. Keep the adjacent logos, images and fonts folders intact. The JSON file is the implementation source of truth; the preview embeds an identical copy to avoid local-file fetch restrictions. Synchronize both when changing demo records.

The local preview demonstrates public content, the vacancy revenue scenario, map/list selection, reservation creation and cancellation, vehicle editing, household invitation states and invoice views. It saves changes in local storage where available. November-only booking dates are a preview constraint. The full product requirements below also define later integrations and additional states that the compact preview does not simulate.



Build a small, coherent product that explains VoltoShare's business model and demonstrates the resident experience. The public website must make the offer understandable within one screen. The app must make availability, reservations and costs understandable without training.

Use this document as the implementation brief. Reuse the existing project scaffold and its conventions. No framework, version, hosting provider or payment provider is mandated. Keep the initial demonstration self-contained, with centralized fixtures and a replaceable data-access boundary. Do not deploy as part of implementing this brief unless the user separately requests deployment.

The proposed service finances, installs and operates shared charging points in apartment buildings. The landlord or property manager contracts with VoltoShare. Residents reserve charging times and pay for measured energy. These are two connected user experiences, with distinct responsibilities and financial views.

### Evidence and decision labels

| Label | Meaning |
|---|---|
| Proposal | Explicit in `VoltoShare_Expose_DE(1).pdf`, page 1, sections 1-5 |
| User requirement | Requested tenant features: availability, parking map, reservations, vehicles, family, usage, spending and invoices; plus a public business-model website |
| Design decision | Recommended visual, navigation or interaction choice in this specification |
| Demo assumption | Fictional data for demonstrating the experience, not a commercial offer or measured result |
| To confirm | A commercial or operational decision not settled by the proposal |

All colours, typography, layouts and copy below are design decisions. All sample properties, people, cars, tariffs and account records are demo assumptions.

### Scope

Include the public website, resident demo, household vehicles/members, reservation flow, charging history and invoice views. Design loading, empty, error and stale-data states as well as the default populated screens.

Real authentication, charger control, NFC provisioning, live telemetry, payment collection and property-management operations need later integrations. The proposal includes manager access administration and reservation-abuse review, but a full manager console is outside this first resident-focused build. V2G is not part of the proposal's current offer. Intelligent load management is part of the proposal, but must not become a fabricated resident-facing battery-trading feature.

## 2. Business model: preserve these distinctions

| Party | Receives | Pays or provides |
|---|---|---|
| Landlord/property manager | Shared infrastructure, platform and operation for the building | A monthly subscription per billable apartment |
| Resident/household | Access to shared chargers, booking and consumption records | Metered electricity at a dynamic tariff plus provider margin |
| VoltoShare | Subscription revenue and an electricity margin | Hardware, installation, software, maintenance and operation |

The proposal's example is **20 apartments, 5 shared charging points and 20 subscriptions at full occupancy**. Subscriptions are per apartment, not per charger. Present this as an illustrative configuration from the proposal, not a customer installation or proven sizing ratio.

The landlord may seek additional rent reflecting charging access. Do not promise that additional rent exceeds subscription costs. The subscription is not automatically an extra line on the tenant's electricity invoice. Any rent treatment belongs to the tenancy arrangement and is unresolved here.

Explain the tradeoff: sharing distributes fixed costs across households and reduces equipment needs, while residents may face waiting, moving vehicles and coordination. Financial outcomes depend on demand, utilization, installation cost and subscription price. Do not invent savings percentages, installation prices, ROI, customer logos, testimonials or CO2 totals.

**Vacancy billing is open:** subscriptions might continue for all contracted apartments or pause for vacant ones. Show both alternatives as an unresolved decision. Never bury this assumption inside a revenue figure.

## 3. Brand and visual language

### Character

Calm, practical and trustworthy. Use clear spatial diagrams, useful numerical summaries and generous whitespace. The product should feel like a reliable building service, with an accessible contemporary interface.

Use the packaged **VoltoShare** logo assets. They are cleaned vector reconstructions from the supplied raster artwork, not original editable brand files. The continuous V/loop mark is the established symbol, not an optional new illustration. Preserve the original letterforms, spacing and proportions. Use the black-and-green version on light backgrounds and the all-white version on graphite or green. Do not redraw, stretch or retype the logo. Avoid decorative lightning everywhere, emojis, stock greenery, glossy car imagery, gradients and excessive card shadows.

### Colour tokens

```css
/* VoltoShare identity v2.0. Fonts accompany this kit under SIL OFL 1.1. */
@font-face { font-family: "Liberation Sans"; src: url("../04_Fonts/LiberationSans-Regular.ttf") format("truetype"); font-style: normal; font-weight: 400; font-display: swap; }
@font-face { font-family: "Liberation Sans"; src: url("../04_Fonts/LiberationSans-Bold.ttf") format("truetype"); font-style: normal; font-weight: 700; font-display: swap; }
:root {
  --color-ink: #1E2023;
  --color-muted: #58615C;
  --color-primary: #28563B;
  --color-primary-hover: #1E422E;
  --color-graphite: #23262B;
  --color-canvas: #F8F5F0;
  --color-surface: #FFFFFF;
  --color-tint: #EAF0EB;
  --color-border: #D9DFD9;
  --color-border-strong: #748178;
  --color-accent: #D6E5D6;
  --color-info: #1959A6;
  --color-info-bg: #EAF2FE;
  --color-warning: #8A5200;
  --color-warning-bg: #FFF3D6;
  --color-danger: #B42318;
  --color-danger-bg: #FDECE9;
  --color-neutral: #56645E;
  --color-neutral-bg: #EEF1EE;
  --font-family: "Liberation Sans", Arial, Helvetica, sans-serif;
  --radius-control: 8px; --radius-card: 12px; --radius-feature: 20px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px; --space-16: 64px; --space-24: 96px;
}
```

Primary buttons use white text on primary green. The supporting pale green uses dark text. Status chips pair their foreground and background tokens with an icon and written label. Use the light border for decorative card separation. Use the stronger border where identifying an input boundary depends on it. Do not treat every colour combination as automatically accessible; verify actual rendered combinations.

### Type, spacing and geometry

Use **Liberation Sans** regular and bold, self-hosted when available. Fall back to `Arial, Helvetica, sans-serif`. The original editable font is unknown and cannot be identified with certainty from raster references. Liberation Sans is the supplied Arial-compatible companion; preserve the logo artwork rather than retyping its wordmark. Use tabular numerals for prices, energy and tables. Install the packaged TTF files before editing the presentation. Font licensing accompanies the files in `04_Fonts/LICENSE.txt`.

| Role | Desktop size/line height | Mobile size/line height |
|---|---|---|
| Public hero | 56/64 px, bold | 36/42 px, bold |
| Public section heading | 40/48 px, bold | 28/36 px, bold |
| App page heading | 28/36 px, bold | 28/36 px, bold |
| Card heading | 20/28 px, bold | 20/28 px, bold |
| Body | 16/24 px, regular | 16/24 px, regular |
| Labels and supporting text | 14/20 px | 14/20 px |

Use the spacing scale **4, 8, 12, 16, 24, 32, 48, 64 and 96 px**. Avoid arbitrary near-duplicate values. Use radii of 8 px for controls, 12 px for cards, 20 px for featured panels and 999 px for badges. Icons use a consistent 2 px stroke at 20 or 24 px.

Public content has a 1200 px maximum width and a 12-column desktop grid. App content has a 1280 px maximum width. Horizontal gutters are 16 px on mobile, 24 px on tablet and 32 px on desktop. Breakpoints are 640, 1024 and 1280 px. Typical public sections have 64-96 px vertical separation; app content uses 24-32 px gaps.

Buttons and form fields are 48 px high. Aim for at least 44 by 44 px interactive targets throughout. This is our design rule, not a statement that WCAG's minimum target criterion is 44 px. Use a visible 2 px information-blue focus outline with 2 px offset. Verify it against the surrounding surface.

### Logo assets and image use

The package preserves the supplied identity through cleaned vector reconstructions and transparent raster exports. It does not contain the original editable brand files. The navigation lockup has an approximate 5.81:1 aspect ratio, and the primary lockup including tagline has an approximate 4.44:1 ratio. Scale proportionally and preserve intrinsic dimensions.

Use `02_Logos/voltoshare-logo-navigation.png` in site navigation and `voltoshare-logo-primary.png` when the German tagline is legible. Use `voltoshare-logo-white.png` on dark backgrounds. The standalone mark is suitable for app identity and compact placements. Use at least one quarter of the mark height as clear space around a logo. Do not compress the logo or put the forest-green wordmark on graphite at small sizes.

The garage and NFC images in `03_Images` are supplied concept visuals. Preserve their proportions and label them as concepts when shown as evidence. Do not present these images as proof of completed installations. The original reference artwork remains in `07_References`.

## 4. Public website structure and copy

### Routes and navigation

| Destination | Route |
|---|---|
| Home | `/` |
| How it works | `/#how-it-works` |
| Business model | `/business-model` |
| For buildings | `/#for-buildings` |
| FAQ | `/#faq` |
| Discuss your building | `/contact` |
| Resident sign in | `/login` |
| Explore resident demo | `/demo` |

The downloadable preview uses hash routes so it opens locally without a server. Production routes remain as specified below.

The public header contains the wordmark, four section/navigation links, resident sign-in and a restrained primary contact action. Collapse into an accessible menu on small screens. Make the demo easy to find without presenting it as a real resident account.

### Homepage section order

1. **Hero.** Heading: “Shared charging. Built for your building.” Supporting copy: “VoltoShare finances, installs and operates shared charging points for apartment buildings. Residents reserve a time, charge their car and track their costs.” Primary action: “Discuss your building”. Secondary action: “Explore resident demo”. Place a small parking/app illustration beside the text on desktop and below it on mobile.
2. **Proposal example.** Three simple figures: 20 apartments / 5 shared charging points / 20 subscriptions. Caption: “Illustrative configuration at full occupancy. Subscriptions are per apartment.” Do not present these as traction metrics.
3. **How it works.** Three resident steps: “Find a charger”, “Reserve a time”, “Charge and track costs”. Explain separately that building installation and ongoing operation are handled by VoltoShare.
4. **Resident preview.** A compact dashboard showing availability, next booking and costs. Mark it “Demo data”. Make the preview lead to `/demo`.
5. **Value for each audience.** Landlords: shared infrastructure with low or potentially zero upfront payment depending on the building, a potential rental amenity and one operating partner. Residents: access without buying an individual wallbox, household use and clear consumption records. Do not guarantee zero upfront cost for every building or availability at every time.
6. **Responsibilities.** A readable table: VoltoShare operates and maintains; the property manager administers resident access and the building contract; residents reserve, charge and vacate in accordance with the building's rules.
7. **FAQ.** Address dedicated versus shared spaces, dynamic energy pricing, app/NFC access, load management and the need for a site assessment. If a booking/no-show rule is undecided, say it will be specified for each building.
8. **Closing contact section.** Repeat “Discuss your building” with concise explanatory text, followed by a simple footer.

### Business-model page

Start with “One shared system. Two clear revenue streams.” Show money and service flows with distinct, labeled arrows or a three-column diagram. Keep landlord subscription payments and resident energy payments visually separate.

Include the proposal example, what the recurring revenue funds, the sharing tradeoff and the unresolved vacancy policy. A compact responsibility/revenue table is preferable to an elaborate pitch deck. Use “potential”, “depends on” and specific assumptions where an outcome is uncertain.

A small optional revenue explainer may start with 20 apartments and 5 points, but all money inputs must be blank until the viewer supplies assumptions. It may accept occupied apartments, monthly subscription and a vacancy switch. Subscription revenue equals billable apartments multiplied by the monthly apartment subscription. If energy volume and provider margin are supplied, show the electricity margin separately. These outputs are revenue or margin, not profit; hardware, installation, financing and operating costs have not been deducted. A full financial scenario planner is a later feature.

### Contact, sign-in and demo entry

The contact page asks for name, email, organization/building, location, approximate apartments and a message. In the demonstration, use an explicit “Demo form: no message will be sent” notice. Validate fields and show a review/preview state, not “Message sent”. Do not transmit contact information without a configured, authorized destination.

The login page may show the intended resident sign-in layout, but must not pretend to authenticate. Provide “Open resident demo” as the working action. `/demo` enters the sample app with a persistent “Demo data” label and an accessible reset control. Avoid collecting real credentials in demo mode.

## 5. Tenant navigation and screens

### Navigation

| Route | Desktop label | Purpose |
|---|---|---|
| `/app` | Home | Current situation and next action |
| `/app/chargers` | Chargers | Map/list and booking entry |
| `/app/reservations` | Reservations | Upcoming and historical bookings |
| `/app/activity` | Activity | Charging sessions and consumption |
| `/app/billing` | Billing | Unpaid and paid invoices |
| `/app/household` | Household | People and vehicles |
| `/app/help` | Help | Rules, status explanations and support |

Desktop uses a sidebar containing all routes. Mobile uses four bottom destinations: **Home, Chargers, Bookings, More**. More opens Activity, Billing, Household and Help. Preserve safe-area spacing, visible page titles and a clear active state. Do not squeeze seven labels into a mobile bar.

### Home

Lead with “Available now: 2 / 5” and a primary “Reserve a charger” action. Supporting text: “Charger status and bookings; parking occupancy unverified.” Show the next reservation: C03, City EV, today 18:00-20:00. Make its detail/cancellation action reachable.

The current-month section shows 8 completed sessions, 112.0 kWh and CHF 35.84 charging cost. Display 10 bookings with the breakdown 8 completed, 1 upcoming and 1 cancelled. Avoid calling all ten “charges”. Show the CHF 28.40 overdue invoice as a separate billing item, with a link to its details.

A small weekly usage chart is optional. If included, derive it from the same sessions, label kWh or CHF clearly, expose exact values and provide a table/list equivalent. Do not fabricate comparison percentages or savings. Default to useful summaries rather than multiple decorative charts.

### Chargers

On desktop, show the parking plan beside the selected charger's details and booking controls. On mobile, use a Map/List switch and place details below the selection or in an accessible sheet. Both views use the same records and selected time interval.

The parking plan has **20 bays, P01-P20, in two rows of ten**, a central drive aisle, an entry on the left and a pedestrian exit on the right. The top row is P01-P10 left to right; the bottom row is P11-P20 left to right. Chargers are C01/P03, C02/P04, C03/P05, C04/P13 and C05/P14. Other bays are neutral and not bookable. This is an illustrative plan, not a surveyed site drawing.

Each charger includes identifier, state label and icon. Distinguish selected styling from status styling. The detail panel repeats charger/bay, selected interval, status freshness, technical state, occupancy caveat and tariff explanation. Show nominal power only when supplied; it is not guaranteed charging speed. Do not imply battery percentage or a completion forecast without vehicle data.

### Reservations

Separate Upcoming and History. Each booking shows date, time, charger, bay, vehicle and state. Upcoming items offer details and cancellation. Cancellation requires a clear confirmation, returns focus appropriately and updates availability and counts. Historical states include completed, cancelled and no-show if the latter is explicitly simulated or provided.

### Activity

List completed sessions with end date, vehicle, charger, measured kWh and final cost. Filters include period and vehicle. Empty filters show a helpful explanation and reset action. A session detail shows its energy/cost breakdown and whether it is billed or unbilled. Keep historical vehicle labels even if a car is later removed.

### Billing

Place unpaid invoices first, then paid history. Show amount, invoice period, due date, state and remaining balance. The current month's unbilled usage is a separate summary, not an unpaid invoice. Offer a detailed invoice view and a browser-printable or PDF representation labeled as a demo. Use “View invoice”, not an unimplemented “Pay now”. An optional payment simulation must say “Simulate payment” and affect demo state only.

### Household and help

Show household identifier, members and registered vehicles. Vehicle fields are display name, registration identifier and optional make/model; avoid unnecessary VIN collection. Support add/edit/remove with validation and clear effects on future bookings. If removal would strand an upcoming booking, require reassignment or cancellation first.

The household administrator can add a pending invitation in the demonstration. State that no email was sent. Help explains reservations, charger states, dynamic tariffs, building rules and how to report an issue. Do not promise 24/7 support or fabricate a working support number.

## 6. Availability, booking and interaction rules

### Distinct state dimensions

| Dimension | Values | Meaning |
|---|---|---|
| Technical charger status | ready, charging, offline, unknown | Connector/operator condition |
| Bay occupancy | free, occupied, unknown | Physical space condition, only if verified |
| Reservation status | upcoming, active, completed, cancelled, no-show | Booking lifecycle |
| Session status | active, completed, interrupted | Actual energy-session lifecycle |

Visible status combines technical state and reservations for the selected interval. Offline/unknown status blocks an assertion of availability. An active reservation makes a technically ready connector unavailable to other households. A verified occupied bay also prevents immediate use. Unknown bay occupancy must remain explicit.

The headline **“Available now: 2 / 5”** means connectors ready and not blocked by current bookings in the sample data. It does not certify empty parking bays. A current charging session can end before a future booking; evaluate future schedule separately. Do not mark a charger unavailable for the whole day merely because it is charging now.

Use text plus colour: Available/primary, Charging/info, Reserved/warning, Offline/neutral, Unknown/neutral. Errors and overdue payment notices use danger where appropriate. Never identify another household, its apartment or its vehicle on the resident map.

### Booking sequence

1. Choose date and start/end time in the building's time zone.
2. Choose a compatible available charger and a household vehicle.
3. Review interval, charger, vehicle, indicative rate and relevant rules.
4. Confirm; recheck availability at this point.
5. Show confirmation with a booking reference, summary and cancellation action.

Require end after start and require a new booking's start to be at or after the current demo/building time. A "Start now" action uses that current time; do not accept a booking that has already partly elapsed. Treat intervals as start-inclusive/end-exclusive, so adjacent bookings may share a boundary. Any turnaround buffer is a configurable building rule, not an invented universal fee or restriction. Reject overlaps for either the charger or the same household vehicle, while leaving household limits configurable. Recheck overlaps after edits. The demo checks conflicts against its fixtures; production must enforce them on the server so simultaneous users cannot both reserve the same interval.

A failed confirmation preserves the vehicle/time selection, explains the conflict and offers another slot. Do not silently move a booking. Offline, missing vehicle, no available slot and stale status each need explicit states. When status becomes stale, show its last update and a retry action. Do not keep a “Live” badge after a data failure.

A reservation does not start charging. Production app/NFC authorization belongs to the charger integration. A demo start/stop control, if included, must say “Simulate start” or “Simulate stop”. Do not animate fictional live meter readings as real telemetry.

## 7. Central demo fixtures and derived metrics

### Environment

- Demo clock: `2026-11-16T14:30:00+01:00`.
- Building: **Lindenhof**, fictional; 20 apartments and 5 chargers.
- Building time zone: `Europe/Zurich`; display currency: CHF.
- Household: **A-12**.
- Members: **Alex**, household administrator; **Sam**, household member.
- Vehicles: **City EV**, registration `DEMO001`; **Family EV**, registration `DEMO002`.
- Initial user: Alex. All dates, totals and due states use the demo clock until explicitly reset or advanced.

Do not combine a frozen booking dataset with the computer's current date. Keep the clock injectable so the demonstration remains reproducible.

### Charger records at the demo clock

| Charger | Bay | Technical state | Booking/session situation | Visible state |
|---|---|---|---|---|
| C01 | P03 | ready | No current booking | Available |
| C02 | P04 | charging | Another household's session | Charging |
| C03 | P05 | ready | A-12 booking today 18:00-20:00 | Available now; reserved later |
| C04 | P13 | ready | Another household's active booking | Reserved |
| C05 | P14 | offline | Unavailable | Offline |

Bay occupancy is `unknown` for all five. Use anonymous external records for the two other-household situations. For predictable overlap examples, their intervals may be configured as 14:00-16:00 today; they do not enter A-12's counts or billing. All map/list/summary views derive from these same records.

### Completed household sessions

Use the following eight completed sessions. Dates refer to session end in the building time zone. Corresponding completed reservations start on the same listed date. Assign stable identifiers and link each session to its booking and vehicle. A consistent illustrative time interval such as 18:00-20:00 is acceptable for these past records.

| End date in November 2026 | Vehicle | Charger | Measured energy | Final cost |
|---|---|---|---:|---:|
| 3 | City EV | C01 | 12.0 kWh | CHF 3.84 |
| 4 | Family EV | C03 | 14.0 kWh | CHF 4.48 |
| 6 | City EV | C01 | 10.0 kWh | CHF 3.20 |
| 8 | Family EV | C03 | 18.0 kWh | CHF 5.76 |
| 10 | City EV | C01 | 16.0 kWh | CHF 5.12 |
| 12 | Family EV | C03 | 12.0 kWh | CHF 3.84 |
| 14 | City EV | C01 | 14.0 kWh | CHF 4.48 |
| 15 | Family EV | C03 | 16.0 kWh | CHF 5.12 |
| **Total** | | | **112.0 kWh** | **CHF 35.84** |

The history uses an illustrative weighted rate of CHF 0.32/kWh for every completed session. This makes the sample easy to reconcile; it is not a claim that the production dynamic tariff stays constant.

Add one upcoming reservation for C03, City EV, today 18:00-20:00. Add one cancelled reservation with a scheduled start in November, for example 13 November. The household then has **10 bookings scheduled this month: 8 completed + 1 upcoming + 1 cancelled**. Calculate this from records; do not store a separate hard-coded dashboard count.

The canonical new-booking example uses **C01/P03, City EV, 17 November 2026, 18:00-20:00**. This is an unsubmitted draft until confirmed, so it does not enter the baseline counts and does not conflict with the existing 16 November booking.

### Invoice records

| Period | Amount | Due date | State at demo clock |
|---|---:|---|---|
| September 2026 | CHF 31.20 | 10 October 2026 | Paid |
| October 2026 | CHF 28.40 | 10 November 2026 | Unpaid and overdue |
| November 2026 usage | CHF 35.84 | Not applicable | Unbilled usage, not an invoice |

Outstanding invoice balance is **CHF 28.40**, independent of the activity chart's month filter. Prior-period invoices are standalone billing fixtures; do not manufacture session history to suggest their totals were derived from the eight November sessions.

### Pricing illustration and definitions

The indicative sample rate is **CHF 0.28 energy + CHF 0.04 provider margin = CHF 0.32/kWh**. An optional 20 kWh estimate is CHF 6.40 if that rate remains unchanged. Label the rate and estimate illustrative, dynamic and not price-locked by a reservation. Shared load and vehicle behaviour also mean a booking does not guarantee 20 kWh delivery.

Mock taxes and additional fees are zero solely to simplify the demonstration. State this assumption near detailed cost views; do not present it as Swiss tax treatment. Do not add the margin again when using the all-in rate.

For real dynamic pricing, energy cost is the sum of each tariff interval's measured energy multiplied by its applicable all-in rate, plus any explicitly defined extra fees. Store measured energy and monetary amounts with documented precision. Use integer minor units for final CHF amounts, not unrounded floating-point display values. Snapshot final billed amounts rather than repricing history from today's rate.

Monthly completed-session count, kWh and cost use **session end date** in `Europe/Zurich`. Monthly booking count uses **scheduled booking start date**, including cancellations, with the breakdown visible. Outstanding balance sums unpaid invoice balances regardless of usage filters. These definitions must be reused throughout the app.

## 8. Components, data boundary and permissions

### Reusable components

Create a small shared set: Button, TextField, Select, StatusBadge, StatCard, SectionHeader, EmptyState, ErrorState, Dialog/Sheet, Toast, ChargerTile, ChargerListItem, ReservationCard, SessionTable and InvoiceCard. Keep sizes, spacing and keyboard behaviour consistent. Avoid separate one-off implementations of each primary action.

Buttons need default, hover, focus, disabled and submitting states. Forms need persistent labels, inline errors and clear required indicators. Disable repeated submissions while pending. A successful toast supplements the updated page; it is not the only confirmation. Destructive actions identify the affected vehicle, member or booking.

### Data organization

Keep fixtures outside view components. A small repository/service interface should supply building, membership, vehicles, chargers, bookings, sessions and invoices. Domain helpers calculate availability, monthly totals, invoice balances and formatted values. The same selectors feed dashboard cards, lists, maps and detail panels.

Demo persistence may use local storage with a versioned schema and reset action. This is a single-browser demonstration, not production authorization or multi-user reservation storage. A later backend can replace the repository without redesigning the screens.

### Role visibility

| Capability | Alex: household administrator | Sam: household member |
|---|---|---|
| View building availability | Yes, anonymous other households | Yes, anonymous other households |
| Use authorized shared vehicles | Yes | Yes |
| View household bookings | Yes | Yes, within household policy |
| Manage members and billing | Yes | No |
| View charging costs | Household totals and authorized detail | Own session detail by default |
| Cancel reservations | Household bookings | Own bookings by default |

The default demo is Alex, so the provided household totals are visible. If role switching is added, it must change the visible data and available actions, not just a badge. The final household billing-sharing policy is to be confirmed. Other households' identities, vehicle registrations, access cards, invoices and histories are never disclosed through availability views.

Removing access must preserve historical billing records. Production permissions must be enforced by the server, not only by hidden navigation controls. Property managers are building-scoped; their eventual console must not automatically expose unnecessary individual charging details.

## 9. Accessibility, responsive behaviour and content

Target **WCAG 2.2 AA**, with verification against the rendered interface. Use semantic headings, native controls, explicit form labels and descriptive button names. Normal text needs at least 4.5:1 contrast; qualifying large text needs at least 3:1. Essential control boundaries and state indicators need appropriate non-text contrast. Colour alone never carries availability, payment or validation meaning.

Provide keyboard access to map chargers through real focusable controls with labels such as “C03, bay P05, available now, reservation at 18:00”. Maintain an equivalent list. A selected tile should expose its selected state. Avoid inaccessible text drawn only inside an image/canvas.

Dialogs trap focus, expose a title, close with Escape where appropriate and return focus to their trigger. Announce validation and status changes without excessive repeated live announcements. Respect reduced-motion preferences. Motion should support state changes, not continually pulse to imply live telemetry.

At 360 px, forms stack, summaries become one or two columns as space permits, and tables become labeled rows or contained scroll regions. Essential controls must remain visible at text zoom. Avoid horizontally scrolling the whole page. At larger widths, use whitespace rather than stretching text across the entire container.

English is v1. Externalize strings for German later and allow longer translated labels. Use locale-aware CHF and date formatting with `Europe/Zurich` as the building time zone. Show kWh for energy, kW only for power and CHF/kWh for a rate. Use concise labels such as “Charging cost”, “Outstanding invoices”, “Reserved until 16:00” and “Last updated 14:30”.

## 10. Implementation sequence and acceptance criteria

Build the design tokens and shared shell first, then centralized fixtures and selectors. Implement the public pages, the populated tenant routes, the booking flow and the supporting empty/error states. Finish with responsive and accessibility checks. Use focused checks for meaningful risks; do not add extensive tests that merely repeat static styling.

The first implementation is ready for review when:

1. Public copy correctly shows landlord subscription per billable apartment and resident metered electricity payments.
2. The 20/5/20 example is labeled illustrative and vacancy billing is explicitly unresolved.
3. Desktop and mobile navigation reach every specified route without dead ends.
4. The initial map, list and dashboard show the same five chargers and “Available now: 2 / 5”, with occupancy caveat.
5. A resident can choose interval, charger and vehicle, review an indicative price and confirm or cancel a demo booking.
6. Conflicts, offline chargers, invalid intervals and missing vehicles produce clear recoverable states.
7. The baseline totals reconcile to 8 completed sessions, 112.0 kWh, CHF 35.84 and 10 bookings with the specified breakdown.
8. October's CHF 28.40 remains overdue at the demo clock; changing the activity month does not erase the outstanding balance.
9. November usage stays unbilled rather than appearing as an overdue invoice.
10. Household changes preserve historical records and respect the chosen role boundaries.
11. Demo forms, invitations, charging controls and payment simulations never claim an external action occurred.
12. The booking flow works with keyboard navigation, visible focus and labeled controls; status remains understandable without colour.
13. Layouts are checked at 360, 768 and 1440 px and with enlarged text, with no clipped primary actions.
14. The reset action restores the same baseline fixtures and clock.
15. No fabricated financial returns, environmental impact, customer proof or V2G functionality appears.

## 11. Decisions still requiring project input

Keep the initial build configurable while the team settles: actual installation responsibilities/costs, subscription amount, vacancy billing, tariff provider and interval, taxes and fees, billing cycle, payment method, cancellation/no-show rules, any turnaround buffer, visitor access, household billing visibility, hardware telemetry and support process. These are product/commercial decisions, not values the implementation agent should invent.

## Sources

- **Provided proposal:** `VoltoShare_Expose_DE(1).pdf`, page 1. Section 1: product and 20/5/20 example. Section 2: payer/revenue split. Section 3: reservation, app/NFC, management and load-management functions. Section 4: customer value. Section 5 and final note: economic tradeoffs and unresolved vacancy billing.
- **User brief:** tenant availability/dashboard, usage and reservation counts, vehicle registration, family/household, booking, parking map, spending and unpaid invoices; public website explaining the business model; PDF design guide and packaged assets for OpenClaw.
- **W3C WCAG 2.2:** <https://www.w3.org/TR/WCAG22/>
- **W3C target size minimum explanation:** <https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum>
- **Design and demo choices:** original recommendations in this specification. They are not claims that the commercial or technical service already exists.

