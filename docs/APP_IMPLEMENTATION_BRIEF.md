# VoltoShare: OpenClaw Implementation Brief

## 1. Your task

Build a small, functional web app called **VoltoShare** for tenants who share electric vehicle chargers in a residential car park.

Tenants must be able to see which chargers are available or in use, reserve a charger, manage their household and vehicles, review their charging activity, and see spending and outstanding invoices.

**Before implementing the interface, locate and read the user's design guidelines and inspect the brand assets available in the repository and any supplied asset package.** The design guidelines govern appearance, layout, typography, colours, components, and interaction styling. This document defines functionality and implementation behaviour. Do not invent a competing visual direction. If the guidelines have not arrived, continue with the data model and application logic while leaving the visual design open.

Deliver a working application with persistent data and connected user journeys. Keep the first version small and easy to use.

### Required use of design guidelines and repository assets

- Inspect the repository for the supplied design guidelines, brand documentation, design tokens, existing components, logos, fonts, icons, illustrations, and photographs. Check relevant folders such as `public`, `assets`, `brand`, `design`, and `docs` if they exist. These are examples, not assumed paths. Also inspect any design or asset ZIP supplied by the user.
- **Reuse the actual VoltoShare logo files and approved variants available in the repository or supplied package.** Preserve their proportions, colours, clear space, and background rules. Prefer the supplied vector version when suitable. Do not redraw the logo, recreate it as plain text, or replace it with a generic charging symbol.
- Use the typography specified in the guidelines, including the correct families, weights, and hierarchy. Load supplied font files from the project when available and appropriate. Do not silently substitute a different font; document any unavailable required font and the temporary fallback.
- Reuse the supplied icons, illustrations, and photographs where they fit the app's purpose. Follow their intended treatments and avoid adding decorative images that make the tenant dashboard harder to use. Use an existing approved favicon or app icon if available.
- Translate the guidelines into shared design tokens and reusable interface components. Apply them consistently to navigation, forms, cards, tables, charts, parking statuses, mobile layouts, and printable invoices. Reuse compatible existing components in the repository.
- Use the appropriate approved logo variant for light or dark backgrounds. Keep asset references local to the project and verify they resolve in the production build. Preserve original source assets when creating web optimisations.
- If a required asset is missing or an existing repository style conflicts with the supplied guidelines, identify the exact issue. Follow the user's latest explicit direction and the supplied brand guidelines; do not silently invent replacement branding. Continue unrelated implementation work while identifying what is needed.
- Record the actual guideline files, asset paths, logo variants, and font files used in the README so the user can trace the implementation back to the supplied materials.

The app should visibly belong to the same VoltoShare brand as the supplied website and presentation materials, while adapting the interface to practical tenant tasks.

## 2. Scope and implementation assumptions

### Required features

- A dashboard showing charging sessions, reservations, energy used, and spending.
- Charger availability and usage, with a selectable parking map.
- Creating, viewing, changing, and cancelling reservations.
- A household containing family members and registered vehicles.
- Charging history and household spending.
- Invoices, including outstanding and overdue amounts.

### Sensible defaults

These are implementation assumptions, not additional requirements from the user. Keep them configurable.

| Setting | Initial default |
| --- | --- |
| Interface language | English |
| Currency | CHF |
| Property timezone | Europe/Zurich |
| Property scope | One residential property with multiple households |
| Dashboard period | Current calendar month |
| Booking increments | 30 minutes |
| Booking duration | Minimum 30 minutes, maximum 8 hours |
| Booking horizon | 30 days ahead |
| Reservation fee | None |
| Charging tariff | A configurable price per kWh |
| Household billing | One shared household account |

Use an illustrative tariff and fictional property details in demo mode. Label them as sample data. Do not present them as an actual VoltoShare price or location.

### Keep outside the first version

Do not add V2G trading, subscriptions, charger installation workflows, dynamic electricity pricing, a full property management dashboard, or real payment processing. Provide clear extension points for future charger and payment integrations.

## 3. Navigation and main screens

Use five clear sections, with the final presentation following the supplied design guidelines:

1. Dashboard
2. Parking & reservations
3. Charging history
4. Household & vehicles
5. Billing

The app must work comfortably on a phone as well as a desktop. Avoid requiring tenants to understand electricity markets or charging infrastructure to make a booking.

## 4. Dashboard

The dashboard should answer: **Can I charge, what have I used, and what do I owe?**

Include:

- Household name and property name.
- A period selector, defaulting to this month, with previous months available.
- Number of completed charging sessions in the selected period.
- Number of non-cancelled reservations starting in the selected period.
- Total energy delivered in kWh during completed sessions in that period.
- Actual charging cost for those completed sessions.
- Current outstanding invoice balance, explicitly labelled as covering all periods.
- Current charger availability, such as “2 of 4 chargers available now”.
- The household's next reservation, with a link to its details.
- A small activity chart showing daily energy use or daily charging cost.
- Recent sessions and a clear “Reserve a charger” action.

All numbers must come from application records. Do not hardcode separate dashboard totals.

For consistency, assign completed sessions to reporting periods by their end time in the property timezone. Explain this convention in the implementation documentation.

Keep these concepts separate:

| Figure | Meaning |
| --- | --- |
| Reservations | Booked time slots, whether or not charging eventually occurs |
| Charging sessions | Actual or explicitly simulated energy delivery records |
| Charging cost | Final cost of completed charging sessions |
| Payments | Money recorded as received against invoices |
| Outstanding balance | Unpaid amount on issued invoices |

A reservation must never automatically increase charging counts, energy consumption, or spending.

## 5. Parking map and charger availability

### Parking map

Build a simple schematic of the property's parking layout. A geographical map or external maps service is unnecessary.

- Show numbered parking bays and identify which contain chargers.
- Use stable bay labels, for example P01, P02, and P03.
- Make each charging bay selectable by touch, mouse, and keyboard.
- Include a matching list view for accessibility and small screens.
- Show status with text or icons as well as colour.
- Keep the layout configurable in property data so it can later match a real car park.

Selecting a charging bay opens charger details, available time slots, and the booking action.

### Charger details

Show charger name, bay number, connector type, maximum power in kW, tariff per kWh, current status, and the last status update time.

Use these operational states:

- Available
- Charging
- Offline
- Unknown or status unavailable

Display reservation occupancy separately. For example, a charger can be operationally available but “Reserved now”, or “Available now, reserved from 18:00”.

**Availability now and availability for a selected future interval are different calculations.** A reservation later today must not make a charger appear occupied for the entire day.

When another household has reserved a charger, show only the occupied interval. Do not reveal their names, registration plates, vehicles, or billing details.

When connected to hardware, do not interpret missing or stale status information as proof that a charger is free. In the first version, simulated statuses must be clearly identified as demo data.

## 6. Reservations

### Create a reservation

The booking flow should be:

1. Select a date and time interval.
2. See chargers available for that interval, in the map and list.
3. Select a charger and a registered household vehicle.
4. Review the bay, date, start and end time, duration, and tariff.
5. Confirm the booking.
6. Display confirmation and add it to upcoming reservations.

Also allow entry from a selected charger on the map, with that charger preselected.

If the household has no vehicle, provide a direct route to add one and return to the booking flow without losing the selected slot.

For the first version, display the tariff and duration. A cost estimate is optional. If included, explicitly label it as an estimate based on estimated energy. Do not calculate actual billed energy from charger power multiplied by the reserved duration.

### Manage reservations

- List upcoming, past, and cancelled bookings.
- Show charger, bay, vehicle, booking creator, start, end, and status.
- Allow household members to change or cancel future household reservations.
- Confirm cancellation before applying it.
- Keep cancelled records for history, but remove their effect on availability.
- A completed booking interval means the reservation has ended. It does not prove that charging occurred.
- Restrict the first version to edits and cancellations before the start time. Explain this clearly in the interface.

### Server-side booking rules

- Start must be in the future; end must be after start.
- Enforce the configured increments, duration limit, and advance booking horizon.
- Do not book offline chargers or incompatible connectors.
- Do not overlap an active booking for the same charger.
- Do not book the same vehicle into overlapping intervals, even on different chargers.
- Allow adjacent intervals, such as 10:00 to 11:00 and 11:00 to 12:00.
- Use half-open intervals: the start is included and the end is excluded.
- Apply all the same checks when changing an existing booking, excluding that booking from its own conflict check.
- An unsuccessful change must preserve the original reservation.
- Handle duplicate submissions so a double tap or retry does not create two bookings.

Validate and commit reservations atomically in the backend. A frontend availability check alone is insufficient. If two tenants request the same slot simultaneously, exactly one request may succeed. Return a useful conflict message and refresh available alternatives.

Store unambiguous timestamps and display them in the property timezone. Handle daylight-saving changes explicitly, including invalid or ambiguous local times.

Future bookings reserve access; they do not guarantee that physical hardware will be functioning or vacated on time. If a previous session overruns, display the conflict and current status rather than silently changing the tenant's booking.

## 7. Household, family members, and vehicles

### Household

Show household name, apartment identifier, members, and registered vehicles.

Use two roles:

| Role | Permissions |
| --- | --- |
| Household owner | All household features, plus managing membership and household details |
| Household member | View household activity and invoices, manage household vehicles, and create or manage household bookings |

All members share visibility of their household's bookings, vehicles, charging history, and bills. Other households' private records must remain inaccessible.

### Family members

- The owner can invite a family member and remove a member.
- Invitations must securely associate an authenticated user with the intended household.
- A copyable, expiring invitation link is sufficient for the first version if email delivery is unavailable.
- Do not display “Invitation sent” unless an email service actually sent it.
- Prevent the last owner from removing themselves without transferring ownership.
- Removing a member revokes their access but preserves historical bookings and charging records.

### Vehicles

Allow adding and editing:

- Vehicle display name, such as “Family car”.
- Make and model, which can be optional.
- Registration plate.
- Primary household driver.
- Connector type.
- Battery capacity in kWh, optional.

Allow vehicle archiving. Historical sessions and invoices must retain their vehicle information. If a vehicle has future bookings, require the user to reassign or cancel those bookings before archiving it.

Do not guess battery capacity or charging capability from a vehicle's name. All connector compatibility and power assumptions must come from explicit configuration.

## 8. Charging history

Show a searchable or filterable list of charging sessions with:

- Date, start time, end time, and duration.
- Charger and parking bay.
- Vehicle and household driver, where known.
- Energy delivered in kWh.
- Final session cost.
- Session status and associated invoice, if already invoiced.

Provide filters for month and vehicle. Show filtered energy and cost totals. A CSV export is useful and small enough to include.

Keep reservations and charging sessions as separate entities. A session may link to a reservation, but the relationship must be optional.

Only finalised completed sessions contribute to final spending. If an active session is shown, label its running energy or cost as provisional.

Do not include start/stop controls that imply a real charger has responded when no hardware integration exists.

## 9. Billing and invoices

### Billing summary

Show:

- Actual charging cost for the selected month.
- Unbilled completed charging, if applicable.
- Total outstanding invoices across all periods.
- Overdue amount.
- Invoice list with billing period, invoice number, total, due date, and status.

### Invoice details

Each issued invoice must include:

- Unique invoice number.
- Household and property information.
- Billing period, issue date, and due date.
- Itemised charging sessions with date, vehicle, charger, energy, tariff, and charge.
- Total, currency, and payment status.
- A downloadable or printable version. A print-friendly invoice with browser “Save as PDF” is acceptable for the first version.

Use paid and unpaid as stored payment states. Derive overdue from an unpaid invoice's due date in the property timezone. In version one, invoices may be paid in full; partial payments are outside scope.

### Accounting rules

- Store monetary amounts in integer minor units, such as CHF cents.
- Use an explicitly defined decimal calculation and rounding policy for energy-based charges.
- Preserve the applicable tariff on each finalised session.
- Preserve issued invoice line items and totals so later tariff or vehicle changes cannot rewrite history.
- Each finalised session can belong to at most one issued invoice.
- Generating a monthly invoice twice must not duplicate invoices or charges.
- Do not count session costs and invoice totals twice in dashboard spending.
- Do not invent taxes or tax treatment. Keep any production tax configuration as an explicit deployment decision.

Tenants can view and download invoices. They must not be able to mark real invoices as paid. Real payment status changes must come from a trusted administrative or payment process.

Provide a documented server-side command or service for issuing monthly invoices from unbilled sessions. A full administration interface is unnecessary. Demo invoices and payment states can be seeded or changed through development-only tools.

## 10. Data model

Use a persistent relational database. The exact ORM and schema implementation may follow the chosen stack, but preserve these entities and relationships.

| Entity | Essential information |
| --- | --- |
| Property | Name, timezone, currency, parking layout, booking policy |
| User | Authentication identity, name, email |
| Household | Property, household name, apartment identifier |
| Membership | User, household, role, membership status |
| Invitation | Household, intended recipient if applicable, token hash, expiry, used or revoked state |
| Vehicle | Household, name, plate, driver, connector, optional capacity, archived state |
| Parking bay | Property, label, layout coordinates, optional charger |
| Charger | Property, bay, name, connector, maximum power, operational status, last update |
| Tariff | Property or charger, currency, price per kWh, effective dates |
| Reservation | Household, creator, vehicle, charger, start, end, status, creation time |
| Charging session | Household, vehicle, charger, optional reservation and driver, start, end, energy, tariff snapshot, final cost, status |
| Invoice | Household, number, period, issue and due dates, currency, total, payment state, paid time if applicable |
| Invoice line | Invoice, charging session, immutable description, energy, tariff, charge |

Preserve referential integrity and use archiving where deleting data would break historical records.

## 11. Technical implementation

### Stack and structure

If a repository already exists, inspect and follow its conventions. Otherwise choose a small, maintainable web stack that OpenClaw can deploy: a responsive frontend, server-side API, established authentication, and a relational database.

Do not introduce extra frameworks or infrastructure without a concrete need. Record the chosen stack and the reason in the README. Browser-only storage is not sufficient for shared reservations between tenants.

Separate presentation, booking logic, billing logic, data access, and external integrations. Keep important business rules on the server.

### Authentication and privacy

- Require authentication for household data and changes.
- Use an established authentication implementation rather than custom password handling.
- Derive household access from the authenticated membership, not a client-supplied household ID.
- Authorise every read and mutation, including invoice downloads and exports.
- Let all property tenants see anonymous occupancy; limit personal records to their own household.
- Do not allow public signup to claim an arbitrary apartment or household.
- Document a trusted setup process for provisioning initial household owners, such as a server-side setup command.
- Validate input and use the chosen framework's protections for sessions and state-changing requests.

### Shared state and persistence

- Save bookings, vehicles, household changes, sessions, and invoices in the database.
- Refresh availability after every booking change.
- Refresh shared availability periodically while the parking view is active, for example every 15 to 30 seconds. WebSockets are optional.
- Show the last update time and a visible error if availability cannot refresh.
- Enforce conflicts through database constraints or suitable transactional locking, not only through separate read-then-write queries.
- Keep database access credentials on the server.

## 12. Demo data and future integrations

Provide a complete demo that works without a charger account, payment provider, or email service.

Seed fictional data covering:

- At least two households, allowing privacy and cross-household availability to be tested.
- Several family members and at least two vehicles in the main demo household.
- A parking layout with charging and ordinary bays.
- At least four chargers covering available, charging, reserved, and offline situations.
- Future, past, and cancelled reservations.
- Completed charging sessions spread across several months.
- Paid, unpaid, and overdue invoices.

Generate internally consistent data. Dashboard totals, session costs, invoice line items, and outstanding balances must reconcile. Use dates relative to the seed date so the demo remains useful later.

Identify simulated charger information and sample billing data visibly. Keep any simulation or demo reset actions disabled outside demo mode.

Define a small charging-provider interface for reading charger statuses and ingesting session/meter records. Use a mock provider initially. Session ingestion must be idempotent so repeated provider events cannot create duplicate sessions or bills.

Real hardware, payments, and email delivery are later integrations. Document what each would need, without making them prerequisites for demonstrating the requested tenant workflows.

## 13. Suggested implementation order

1. Read the design guidelines, inspect the repository and supplied asset packages, and identify the actual logos, fonts, and other brand assets to reuse.
2. Set up the application, database, authentication, households, and seed data.
3. Implement vehicle and household management.
4. Implement shared charger availability, parking map, and booking validation.
5. Implement create, change, and cancel reservation flows.
6. Implement charging history and dashboard calculations from stored records.
7. Implement invoice views, invoice generation, and exports.
8. Apply the complete design guidelines across desktop and mobile.
9. Verify the critical journeys, fix failures, and prepare the deployment handoff.

Do not stop after producing static screens. Connect the interface to real application state and make the required actions work.

## 14. Acceptance criteria

The implementation is complete when these checks pass:

- [ ] A tenant can sign in and see only their household's private data.
- [ ] Family members can join through an authorised invitation and share household access.
- [ ] A removed member immediately loses household access.
- [ ] A tenant can add a vehicle, book it, change the booking, and cancel it.
- [ ] Bookings and household changes survive refresh and server restart.
- [ ] Another household sees a newly booked slot as occupied without seeing private details.
- [ ] Two simultaneous attempts to reserve the same charger interval produce exactly one success.
- [ ] Overlapping vehicle bookings are rejected; adjacent intervals are allowed.
- [ ] A failed booking edit preserves the original reservation.
- [ ] Cancelling a reservation frees the slot and updates reservation counts without creating a charge.
- [ ] Map and list views show consistent availability for the selected interval.
- [ ] Dashboard totals reconcile with the underlying sessions and invoices.
- [ ] Tariff changes do not change historical session costs or issued invoices.
- [ ] Repeated invoice generation or session ingestion does not duplicate charges.
- [ ] Tenants can view and print invoices but cannot mark real invoices paid.
- [ ] Direct requests for another household's records, downloads, or mutations are rejected.
- [ ] Mobile layouts, keyboard navigation, and status labels are usable.
- [ ] The interface follows the supplied design guidelines and uses the actual approved VoltoShare logo and available brand assets from the repository or supplied package.
- [ ] Required fonts and image assets load correctly in the production build, with no broken paths, distorted logos, or undocumented substitutions.
- [ ] Loading, empty, offline, validation-error, and no-availability states are handled.
- [ ] Demo information is identifiable and no control falsely claims to operate real hardware or move money.

Use focused automated checks for booking concurrency, authorisation, and financial reconciliation, plus browser checks of the main user journeys. Avoid a large test suite that only mirrors trivial implementation details.

## 15. OpenClaw handoff deliverables

Provide:

- Complete source code.
- Database schema and migrations.
- Repeatable fictional demo seed data.
- An environment-variable example containing placeholders only.
- A README with exact local run, build, test, and deployment instructions.
- A short README section identifying the design guidelines and the actual logo, font, icon, and image paths used.
- The chosen database persistence and backup approach for deployment.
- A description of demo mode, setup of real household owners, and future integration points.
- A concise summary of what was implemented, what was verified, and any remaining limitation.

Do not include real credentials or enable demo accounts in a production deployment by default.

**General rule: a reservation books access; a charging session records energy delivered; an invoice requests payment. Keep all three separate and linked.**

---

Brief provenance: the user's requested features, with explicitly stated implementation defaults and recommendations. This brief does not define the visual design or claim that real charger or payment integrations already exist.
