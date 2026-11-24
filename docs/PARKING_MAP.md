# Parking map and bay reservations — 24 November 2026

## Scope and real-site boundary

Mathis requested a more recognisable Papieri parking layout, all spaces (ordinary and EV), clickable reservations, and different floors. The new map/booking implementation is floor-aware and supports both types of space. Other dashboard screens retain their layout and accounting logic.

**The actual Papieri plan has not been supplied.** Official public sources identify Parking A and B but do not establish floor counts, numbered spaces, geometry or charger positions. The user has been asked which facility (A/B/both) and for its detailed floorplans. Do not equate Parking A/B with floors or invent the actual plan.

Until a verified plan arrives, the deployed app retains its existing **20-space Lindenhof fictional demo**, all assigned to the default UG1. No fictional Papieri floors or additional real-site spaces are silently added. The architecture is explicitly labelled **“Illustrative layout · not a surveyed floor plan.”** Multi-floor behavior is verified with a disposable second-floor fixture only.

Official reference pages:

- https://www.papieri-cham.ch/anfahrtsplan — Parking A/B entrances.
- https://www.papieri-cham.ch/quartier/mobilitaet — mobility and charging preparation.
- https://www.wwz.ch/-/media/landingpages/e-mobilitaet/papieri-cham_pdf_factsheet-papieri-cham.pdf — shared/dedicated charging behavior; not a floorplan.

## UI

- Architectural SVG background with perimeter walls, bay markings, aisles/arrows, columns, stairs/lift, pedestrian crossing and ramp; native HTML bay buttons sit over it.
- Every configured bay is visible and selectable, including ordinary spaces. Availability reflects the chosen interval and server records, not a physical occupancy sensor.
- Floor selector with bay/charger counts, search across floors, map/list parity and zoom with contained horizontal scrolling. Native keyboard Tab/Enter/Space and arrow-grid navigation.
- Selected-space panel with floor, space label, type, availability and reservation confirmation. Mobile provides a return-to-map control.
- Reserved/offline/unbookable spaces remain inspectable; reservation is blocked when invalid. Errors and refresh failures do not fabricate availability.

## Data and booking

Migration `0002_parking_bays_and_floors`:

- Adds `Bay.floor` (default UG1), `Bay.bookable` and floor-aware position uniqueness.
- Adds `Reservation.bay`, backfilled from each historical charger; permits a null charger for ordinary parking.
- Retains original reservations, IDs, vehicles, charging sessions, invoices and historical monetary values.

POST `/api/reservations/` and change accept `bay_id`, or the previous `charger_id`. If both are supplied they must match. Selecting an EV-equipped bay by bay ID still applies connector/hardware checks, so the new path cannot bypass charger restrictions. All bay/vehicle conflicts, property/household scope, idempotency and duration rules are checked server-side inside the existing transaction model.

Ordinary-space reservations create **no energy, charging session, invoice or payment**. This demonstration does not claim real ordinary-space parking prices or ownership permissions. The `bookable` flag lets operators exclude private/nonreservable bays; no actual Papieri rights are inferred.

State payloads add bay IDs/floors. Other households' occupancy exposes only bay/charger, interval, kind and ownership flag—never names or plates.

## Verification / deployment

- 33 domain/auth/parking tests pass, including migration preservation and two independent SQLite connections racing for the same ordinary bay.
- Browser tests: `tests/app-parking-browser.mjs` uses disposable database fixtures only. Never run its mutation suite on public shared demo data.
- Existing `tests/app-public-smoke.mjs` is a read-only live smoke check (apart from demo login/session creation).
- Back up live DB, migrate, collectstatic, restart app, verify health and public read-only views. No reset/reseed, no website changes.

## Deployed release verification

Deployed on 24 November 2026: migration applied, static assets collected, Django system checks clean, and `electromobility-app.service` restarted successfully. The live service is active.

- 55 isolated browser checks passed, covering ordinary/EV booking, changes/cancellation, conflicts, keyboard use, search, zoom, responsive layouts and the disposable second-floor fixture.
- 51 read-only public app checks passed after deployment at https://app-electromobility.mclement.ch, including all five dashboard routes at 360/768/1440 px, household privacy and downloads.
- All original rows and column values across the ten business tables matched the pre-migration preservation manifest; the only new values are the migration additions. Live configuration remains 20 bays on UG1.
- Pre-migration SQLite backup: `~/.local/state/voltoshare/backups/voltoshare-20261124T132034008633Z.sqlite3` (private, outside Git/public roots).
- Screenshot review completed; temporary review images removed. No website deployment, account reset or reseeding was performed.

## Next source-dependent step

Once Mathis supplies the selected Papieri garage and plans, map actual floors and bay geometry/identifiers to authoritative configuration, confirm which bays are shared/reservable and charger-equipped, and replace the illustrative geometry. Preserve existing demo booking/accounting records rather than resetting the database.
