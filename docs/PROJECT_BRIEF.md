# VoltoShare — project baseline

Source: [German project proposal](VoltoShare_Expose_DE.pdf), dated **15 October 2026**, supplied by Mathis on **16 November 2026**. This is the team's **first working draft**, not a finalized specification. Preserve its assumptions when designing the future website and web app; later explicit decisions can supersede them.

## Product and customers

VoltoShare finances, installs and operates shared EV wallboxes in apartment-building garages, together with the resident app. Residents reserve charging spaces instead of every apartment needing its own wallbox. Landlords/property managers obtain infrastructure with little or no initial payment; recurring fees fund provision and operation.

## Business model — keep the units correct

- The landlord or property manager is VoltoShare's contractual customer.
- A monthly infrastructure/platform subscription is charged **per billable apartment, not per charging point**.
- The illustrative fully occupied building has **20 apartments, 5 shared charging points and 20 subscriptions**. These are example values, not a universal capacity recommendation or validated financial result.
- Residents pay for their metered electricity consumption at a dynamic tariff plus a small provider markup.
- Subscription revenue and the electricity margin cover hardware, installation and ongoing operating costs. The proposal does not set prices or tariff formulas.

## Proposed app and operating capabilities

- Residents reserve charging times and unlock charging points using the app or an NFC card.
- Landlords/property managers add/remove users, issue access cards and review reservations for misuse.
- VoltoShare provides hardware, software updates and maintenance.
- Intelligent load management distributes the building's available charging power.

These are proposed capabilities, not claims that integrations, payment processing or physical charger control already exist.

## Website positioning and economic analysis

- Landlords can market apartments with shared charging access rather than dedicated wallboxes. A rent premium may provide additional income after subscription costs; do not present that outcome as guaranteed.
- Residents gain charging access without buying or installing an individual wallbox.
- Shared use spreads fixed costs and reduces infrastructure requirements.
- Evaluation must balance these benefits against waiting, moving vehicles and coordination costs. Viability depends on demand, utilization, installation costs and subscription price.

## Explicitly unresolved: vacant apartments

The proposal leaves two alternatives open:

1. Subscriptions continue for all contracted apartments, including vacant ones: the landlord bears the vacancy cost.
2. Subscriptions pause for vacant apartments: VoltoShare loses that revenue and bears the corresponding risk.

Do not silently choose a rule in marketing claims, calculators, billing logic or dashboards. Keep the alternatives explicit until Mathis/the team decides.

## Work status

The repository is cloned on the Pi. Mathis has supplied this proposal as future implementation context and will supply design guidelines. On 16 November 2026 Mathis additionally authorized **blank placeholder deployment only** at `website-electromobility.mclement.ch` and `app-electromobility.mclement.ch`. The actual website/web-app design and functional implementation still await his further instructions. No technology stack, visual identity, final pricing or additional product requirements should be inferred from this document.
