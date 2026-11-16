# VoltoShare Website: OpenClaw Implementation Brief

## 1. Your task

Build a polished, responsive public website for **VoltoShare**, explaining the service, its benefits, and its business model. The website should work both as a clear introduction for prospective property customers and as a credible demonstration of the concept during the course presentation.

Use this brief together with:

1. The proposal, **VoltoShare_Expose_DE(2).pdf**, dated 15 October 2026, page 1, sections 1 to 5 and the vacancy decision box.
2. The user's separate VoltoShare design guidelines and asset package.
3. The existing repository, including its logos, fonts, images, components, and any tenant app implementation.

The proposal defines the commercial concept. The design guidelines define the visual identity. This document translates them into website content, behaviour, and implementation requirements.

This is the public website brief. The existing tenant app remains a separate product surface for bookings, household activity, and billing. Link the two where appropriate.

### Audience and goals

- **Primary audience:** landlords and property managers of residential apartment buildings.
- **Secondary audience:** residents who want to understand how shared charging works.
- **Presentation audience:** people assessing the project's business model and economic reasoning.
- **Primary visitor action:** express interest in assessing a property or discussing the concept.
- **Secondary actions:** understand the model, explore the example, and open the tenant app demo if available.

Keep the main explanation concise and visual. Place assumptions and economic detail on the business-model page.

### Language and project status

Write implementation documentation in English. Use **German as the initial website language**, following the German proposal, unless the user's latest instructions or repository require another language. This is a configurable implementation assumption. Do not add an English language switch unless complete English content exists.

The proposal is a working project concept. Use a discreet label such as **“Projektkonzept | Ökonomie der Elektromobilität”**. Do not imply that VoltoShare already has live installations, customers, or commercial operations without supporting project material.

## 2. Required use of design guidelines and repository assets

Before styling the website, inspect the repository and any supplied asset ZIP. Locate the design guidelines, brand documentation, existing design tokens, logos, font files, icons, illustrations, photographs, and app screenshots. Folders such as `public`, `assets`, `brand`, `design`, and `docs` are examples to inspect if they exist, not assumed paths.

- **Follow the supplied design guidelines** for colours, typography, spacing, components, image treatments, and visual hierarchy.
- **Use the actual VoltoShare logo files.** Preserve their proportions, approved colours, clear space, and background rules. Prefer a supplied vector version where suitable. Do not redraw the logo or replace it with styled text or a generic charging icon.
- Use the specified font families and weights. Load supplied font files when available and appropriate. Document any missing required font and temporary fallback.
- Reuse approved images, icons, and illustrations where relevant. A useful diagram is preferable to an unrelated decorative photograph.
- Use existing app screenshots only if available and consistent with the current app. Any illustrative interface must be labelled as a concept or demo and contain fictional personal data.
- Apply the same brand identity to the website, tenant app links, diagrams, calculator, forms, and footer.
- Reuse compatible components already in the repository. Build shared styles and tokens instead of styling every section independently.
- Preserve original assets when creating optimised web versions. Verify that all asset and font paths work in the production build.
- Record the guideline files and actual asset paths used in the README.

If an essential asset or guideline is missing, identify it precisely and continue with content and application logic. Do not silently invent replacement branding. The user's latest explicit instructions take precedence when supplied materials conflict.

## 3. Commercial facts that the website must preserve

The following are taken from the supplied proposal. Present them as the proposed VoltoShare model, not as independently validated operating results.

| Topic | Required explanation | Proposal source |
| --- | --- | --- |
| Product | VoltoShare finances, installs, and operates shared wallboxes in residential garages and provides the associated app. | Section 1 |
| Shared access | Residents reserve charging spaces instead of every apartment needing its own wallbox. | Section 1 |
| Upfront payment | The concept allows low or no initial payment for the landlord. The exact arrangement is not specified. | Section 1 |
| Contracting customer | The landlord or property manager contracts with VoltoShare. | Section 2 |
| Infrastructure subscription | The landlord or manager pays monthly per billable apartment for infrastructure and platform. | Section 2 |
| Resident payment | Residents pay for measured charging electricity at a dynamic tariff plus a small provider markup. | Section 2 |
| Provider income | Subscription income and the electricity margin contribute to hardware, installation, and ongoing operating costs. | Section 2 |
| Tenant platform | Residents reserve charging times and unlock chargers through the app or an NFC card. | Section 3 |
| Property administration | Landlords and managers can add or remove users, issue access cards, and review reservations for misuse. | Section 3 |
| Operations | VoltoShare handles hardware, maintenance, and software updates. | Section 3 |
| Load management | Available charging power in the building is distributed intelligently among charging points. | Section 3 |
| Landlord benefit | Charging access may support an additional amount within rent. Additional rental income after subscription costs is an objective, not a guaranteed return. | Section 4 |
| Resident benefit | Residents gain charging access without buying or installing their own wallbox. | Section 4 |
| Economics | Shared use can reduce equipment requirements and distribute fixed costs, with tradeoffs in waiting, moving cars, and coordination. | Section 5 |
| Viability drivers | Demand, utilisation, installation cost, and subscription price affect economic viability. | Section 5 |
| Vacancy | Whether subscriptions continue or pause for vacant apartments remains undecided. | Vacancy decision box |

Do not broaden the main offer into workplace charging, public fast charging, individually rented wallboxes, or V2G trading based on older ideas. This website should reflect the attached residential shared-charging proposal.

## 4. Recommended website structure

Keep the site compact: one landing page, one business-model page, and one contact page. Reuse existing routing conventions where appropriate.

| Route | Purpose | Required content |
| --- | --- | --- |
| `/` | Explain the offer and guide visitors | Hero, shared-charging example, audience benefits, how it works, operations, app preview, business-model summary, FAQ, CTA |
| `/geschaeftsmodell` | Explain who pays, who benefits, and the economic tradeoffs | Payment flows, 20/5/20 example, scenario calculator, vacancy alternatives, assumptions and limits |
| `/kontakt` | Provide a concrete next step | Property enquiry form or clearly labelled demo enquiry flow |
| Existing app URL or route | Open the tenant product | Working app or labelled demo, configured centrally |
| `/impressum` and `/datenschutz` | Provide relevant operator and privacy information when confirmed | Verified project/operator details and an accurate description of implemented data handling |

The last two routes do not authorise inventing a company address, legal entity, registration number, or approved legal text. Any missing publication details belong in the deployment handoff. For a presentation-only preview, clearly identify the project and avoid collecting real enquiries until the receiving operator and data handling are configured.

Suggested navigation: **Lösung · So funktioniert’s · Geschäftsmodell · FAQ**, with a **Kontakt** action and an **App-Demo** link when available. Landing-page items should scroll to stable section anchors; links from other pages must return to the correct section.

Do not add a blog, news feed, job board, investor portal, or CMS unless already required by the repository or user.

## 5. Landing page content

### A. Hero: explain the offer immediately

Answer three questions in the first screen: what is it, who is it for, and what should I do next?

Suggested draft copy, to adapt to the approved brand voice:

**Headline:** “Geteilte Ladepunkte für Ihr Mehrfamilienhaus.”

**Supporting copy:** “VoltoShare übernimmt Finanzierung, Installation und Betrieb gemeinsamer Ladepunkte. Bewohner reservieren Ladezeiten per App. Vermieter und Verwaltungen erhalten Infrastruktur und Plattform aus einer Hand.”

Mention low or potentially zero upfront payment as part of the proposed arrangement, not as a universally available guarantee.

- Primary CTA: **“Liegenschaft anfragen”**, opening the contact page.
- Secondary CTA: **“So funktioniert’s”**, scrolling to the explanation.
- Use an approved image, a relevant branded illustration, or a clear building-to-parking schematic.
- Keep the project/concept status visible without overwhelming the main content.

Do not invent an alternative brand slogan if the design guidelines already supply one.

### B. The central example: 20 apartments, 5 chargers, 20 subscriptions

Make this example prominent:

**20 Wohnungen · 5 geteilte Ladepunkte · 20 Abonnements**

Immediately explain: **“Beispiel bei Vollvermietung. Das Abonnement gilt pro abrechnungspflichtiger Wohnung, nicht pro Ladepunkt.”**

Use a simple diagram linking apartments to shared charging bays. Show that the five charging points are shared across the building; do not draw one permanently assigned charger per apartment.

This is the proposal's illustrative configuration. It is not a universal sizing rule or proof that five chargers meet every 20-apartment building's demand.

### C. Benefits for the two audiences

Use two clear content groups:

| Vermieter und Verwaltungen | Bewohner |
| --- | --- |
| Access to centrally operated shared infrastructure | Access to charging without buying a wallbox |
| Low or potentially zero initial payment under the proposed arrangement | Reservation of charging times through the app |
| VoltoShare manages technical operations and maintenance | Charger access using app or NFC card |
| Charging access as an apartment amenity | Charges based on measured electricity consumption |
| Potential additional rental income, dependent on assumptions | Shared access, with availability governed by reservations |

Avoid absolute promises such as “immer verfügbar”, “garantierte Rendite”, or “kostenlose Installation”.

### D. How it works

Distinguish the building setup from the resident journey. These can be two tabs or two short sequences.

**Property journey:** assess building and demand → agree the arrangement → install shared charging points → operate and maintain the service.

The assessment and agreement steps are recommended website explanations, not detailed processes specified by the proposal. Do not invent installation deadlines or service-level commitments.

**Resident journey:** reserve a charging slot → access the charger by app or NFC → charge → pay for measured electricity use.

Explain any proposed hardware steps as concept capabilities unless an actual working integration is available.

### E. Platform and operation

Show the three areas of responsibility:

- **Residents:** reservations, app or NFC access, charging activity, and billing visibility.
- **Landlords and managers:** user administration, access cards, and review of reservation misuse.
- **VoltoShare:** financing, hardware, installation, software updates, maintenance, and operation.

Include a short load-management explanation: **“Das Lastmanagement verteilt die im Gebäude verfügbare Ladeleistung auf die angeschlossenen Fahrzeuge.”**

Do not equate load management with V2G, energy export, or electricity trading. Do not promise maximum power at every charger simultaneously.

### F. Tenant app preview

Show three or four actual or clearly labelled illustrative features: parking availability, reservations, household vehicles, and charging/billing history.

- Prefer verified screenshots from the existing tenant app.
- Use fictional residents, vehicles, and invoices.
- Identify sample values as demo data.
- Link to the app only when the URL or route exists and works.
- Use **“App-Demo öffnen”** for a demo and **“Zur App”** for an actual app. Do not label a simulated experience as a live login.
- If the app is unavailable, show the feature preview and honest status text instead of a dead button.

The public website must not expose real household records, parking reservations, invoices, or personal information.

### G. Business-model summary

Show two clearly labelled payment flows:

1. **Vermieter / Verwaltung → VoltoShare:** monthly subscription per billable apartment for infrastructure and platform.
2. **Bewohner → VoltoShare:** measured charging electricity at a dynamic tariff plus provider markup.

Explain that the infrastructure subscription and electricity bill are different payments. A potential rent uplift belongs to the landlord's economic model; it is not an extra direct tenant subscription paid to VoltoShare.

Link to **“Geschäftsmodell verstehen”** on the detailed page.

### H. FAQ and final CTA

Use accessible expandable FAQ items with answers written from the proposal. Include:

- Who signs the contract?
- Who pays the subscription, and what does it cover?
- Is it charged per apartment or per charger?
- What do residents pay for electricity?
- Does every apartment receive its own wallbox?
- How do reservations and app/NFC access work?
- What happens when all chargers are occupied?
- Who maintains the hardware and updates the software?
- What does load management do?
- What happens during vacancy?
- What information is useful for assessing a building?

When all chargers are occupied, explain that residents need to select an available slot and may have to wait or move their vehicle. Do not invent queues, penalties, or cancellation rules that the service has not defined.

The vacancy answer must say that the billing policy is still an open model decision and link to both scenarios.

Finish with a concise property enquiry CTA. Repeat the core offer rather than adding unsupported commercial claims.

## 6. Business-model page

This page should make the economic logic understandable during the presentation and to a prospective property customer.

### Who provides what, and who pays whom?

Use a compact diagram or equivalent accessible layout, followed by a short table:

| Party | Pays or provides | Receives |
| --- | --- | --- |
| Landlord / property manager | Subscription per billable apartment | Infrastructure and platform for the property |
| Residents | Metered electricity charges at dynamic tariff plus markup | Reservation-based access to shared charging |
| VoltoShare | Financing, installation, app, technical operation, and maintenance | Subscription income and an electricity margin |

Distinguish money flows from service flows with labels, not colour alone.

### Revenue, costs, and landlord economics

Explain these as separate perspectives:

- **VoltoShare income:** subscriptions and the electricity markup help fund hardware, installation, financing, maintenance, software, and operations. Subscription income is not automatically profit.
- **Landlord economics:** a possible rent uplift may exceed subscription costs, but the result depends on the actual uplift, occupancy, subscription price, and other costs.
- **Resident cost:** electricity use is metered and charged separately. No subscription price, electricity markup, or rent uplift has been fixed in the supplied proposal.

Explain a dynamic tariff in plain language: the electricity price can vary over time; the resident bill includes measured consumption and the agreed provider markup. Do not invent the tariff source, refresh interval, or detailed pricing formula. Do not imply that dynamic pricing guarantees lower bills.

There should be no published price cards with invented commercial amounts and no invented “Basic / Pro / Premium” plans. Use a tailored enquiry for actual pricing.

### Vacancy is an open decision

Show both possibilities side by side under **“Noch offene Modellentscheidung: Leerstand”**:

| Scenario | What changes | Who bears the immediate revenue effect? |
| --- | --- | --- |
| Subscriptions continue for contracted apartments | The landlord pays for those apartments even when vacant | Landlord continues paying while receiving no rent for the vacant units |
| Subscriptions pause for vacant apartments | The number of billed subscriptions falls with occupancy | VoltoShare receives less subscription income |

Do not choose either as the agreed contractual policy. Let the illustrative calculator compare them.

### Balanced economic assessment

Present both benefits and constraints:

- Fewer charging points may be needed than under one wallbox per apartment.
- Fixed costs are shared across households.
- Residents gain access without individually buying or installing a wallbox.
- Shared access can involve waiting, moving cars, and coordination.
- Demand, utilisation, installation cost, and subscription pricing determine viability.
- Vacancy rules affect the distribution of risk between the landlord and VoltoShare.

“5 statt 20 Ladepunkte” is an illustrative equipment-count comparison. It does not establish 75% lower cost, equivalent service capacity, or a specific emissions reduction.

Include a small source note identifying the proposal and its working-draft date. Keep citations and assumptions readable, not hidden in hover-only tooltips.

## 7. Interactive building and economics example

Implement one small interactive example on the business-model page. Its purpose is to explain the model, not produce a commercial quote or determine engineering capacity.

### Inputs

| Input | Meaning | Initial state |
| --- | --- | --- |
| `N` | Contracted apartments | 20 |
| `O` | Occupied apartments | 20 |
| `P` | Shared charging points | 5 |
| `S` | Assumed subscription per billable apartment per month, CHF | User-entered; no claimed commercial default |
| `R` | Assumed rent uplift per occupied apartment per month, CHF | User-entered; no claimed commercial default |

Show **“Illustrative Modellrechnung. Keine Preisofferte.”** beside the monetary inputs and outputs.

Use labelled inputs with keyboard support. Sliders may supplement numeric inputs, but not replace them. Require whole apartment and charger counts, `N >= 1`, `0 <= O <= N`, and `1 <= P <= N` for this simple example. Allow zero monetary inputs and reject negative monetary inputs. Do not silently overwrite the occupied count when the user changes `N`; visibly explain any adjustment required.

Keep the 20/5/20 visual usable before monetary values are entered. Show a neutral prompt for the financial outputs until both monetary assumptions are supplied. Do not interpret an empty input as zero.

### Calculations

Calculate both vacancy policies from the same inputs:

```text
Scenario A: subscriptions continue during vacancy
Billable apartments B = N

Scenario B: subscriptions pause during vacancy
Billable apartments B = O

Monthly subscription amount = B * S
Assumed additional monthly rental income = O * R
Potential monthly rent contribution after subscriptions = O * R - B * S
```

Label the final output **“Möglicher Mietbeitrag nach Abonnementkosten, vor weiteren Kosten”**. State that it excludes other landlord costs, initial payments, financing, and tax effects. Negative outcomes must remain visible. Do not call this net profit, ROI, or guaranteed income.

Show the subscription amount as a cost to the landlord and subscription income to VoltoShare. Do not add the two as separate revenues.

Changing `P` changes the infrastructure illustration, not the subscription multiplier. Changing the charger count must not automatically change apartment subscriptions or fabricate cost savings. Explain that actual charger sizing needs demand and installation information.

For a fully occupied building, the two vacancy scenarios should return identical subscription amounts.

### Keep the calculator small

Do not add electricity trading, CO2 calculations, loan schedules, or a full provider profit forecast. Explain the electricity markup separately in the payment-flow diagram. The proposal does not provide the inputs needed for a defensible full profitability model.

### Calculation checks

The following are fictional test inputs for implementation checks, not proposed VoltoShare prices:

| N | O | P | S | R | Subscription: continue / pause | Rent uplift | Contribution: continue / pause |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | 20 | 5 | CHF 20 | CHF 30 | CHF 400 / CHF 400 | CHF 600 | CHF 200 / CHF 200 |
| 20 | 16 | 5 | CHF 20 | CHF 30 | CHF 400 / CHF 320 | CHF 480 | CHF 80 / CHF 160 |
| 20 | 0 | 5 | CHF 20 | CHF 30 | CHF 400 / CHF 0 | CHF 0 | CHF -400 / CHF 0 |

Changing only `P` from 5 to 4 must leave these financial outputs unchanged.

## 8. Contact and enquiry flow

Keep the form short:

- Name.
- Email.
- Role: landlord, property manager, resident, or other.
- Organisation, optional.
- Property location, optional, with town or postcode sufficient initially.
- Number of apartments, optional.
- Short message.

Do not request a payment card, ID document, detailed tenant list, or private vehicle information on the public site.

### If a real enquiry destination is configured

- Validate on the server and provide useful field-level errors.
- Send or store the enquiry through the configured backend.
- Show success only after the configured operation succeeds.
- Preserve form entries after a recoverable error and prevent accidental duplicate submissions.
- Use basic abuse protection suitable for the chosen deployment.
- State accurately who receives the enquiry and how the submitted data is handled.
- Do not imply a response-time guarantee unless one has been supplied.

### If this is a presentation demo

- Label the form as a demo before submission.
- Use a result such as “Demo: Ihre Anfrage wurde nicht versendet.”
- Do not send messages or persist real personal details through an unconfigured workflow.
- A configured, visible contact address can be an alternative, but do not invent one.

Keep enquiry mode and destination configurable. Do not claim a message was sent when the interface only displayed an animation.

## 9. Relationship with the existing tenant app brief

The earlier tenant app brief deliberately simplified first-version billing and excluded subscriptions and dynamic tariffs from that implementation. **Both are nevertheless explicit parts of the proposal's business model.**

For this website:

- Treat the proposal as authoritative for the commercial explanation.
- Explain landlord apartment subscriptions and resident dynamic electricity pricing accurately.
- If the app demo uses a flat sample tariff, identify it as a demo simplification.
- Describe app/NFC access, property management controls, and load management as proposed capabilities unless a working integration is verified in the repository.
- Do not imply that an app booking starts a real charger or creates a real electricity charge unless the integration does that.
- Do not silently rewrite the existing tenant app as part of building the public site. Record any alignment work needed for a later app version.

Use the same logo, fonts, components where practical, and navigation language across the two surfaces. Keep their responsibilities clear: the website explains the service; the tenant app manages household charging activity.

## 10. Technical implementation

### Stack and content

- Inspect and follow the existing repository and deployment conventions first.
- Reuse its frontend framework and components where appropriate.
- Keep the public pages lightweight. Static or prerendered content with small interactive components is sufficient unless the existing stack requires otherwise.
- No tenant authentication or booking database is needed for the marketing pages themselves.
- Store reusable copy, configuration, FAQ content, and financial assumptions in organised content/configuration files.
- Configure the app URL, contact mode, contact destination, project status, and approved downloads centrally.
- Do not introduce a CMS or extra backend service solely for a few static pages.
- Keep credentials and server-only configuration out of the frontend bundle and repository.

### Responsive behaviour and accessibility

- Support mobile, tablet, and desktop without horizontal overflow.
- Make menus, FAQ items, forms, and calculator controls usable by keyboard.
- Use semantic headings, labelled inputs, visible focus, sufficient contrast, and text alternatives for meaningful visuals.
- Ensure diagrams and charts have readable labels and a text equivalent.
- Respect reduced-motion preferences and avoid scroll effects that delay access to content.
- Show important content without depending on hover or animation.

### Performance, metadata, and links

- Optimise images appropriately and reserve their display space to avoid layout shifts.
- Load only the fonts and weights that are actually used.
- Give every page a useful German title and description.
- Use approved logo and social preview assets if available.
- Configure the canonical site URL only once the actual domain is known.
- Verify all navigation, app links, downloads, assets, and direct routes.
- Do not fabricate reviews, customer counts, business addresses, or structured-data claims.
- Keep third-party analytics and tracking out of the first version unless explicitly requested and configured.

These are implementation requirements, not a claim that publication or legal checks have already been completed.

## 11. Content and credibility rules

- Prefer concrete explanations to generic sustainability slogans.
- Keep the contracting customer and the resident user distinct.
- State the per-apartment subscription basis wherever the 20/5/20 example appears.
- Make every unconfirmed financial value visibly illustrative.
- Explain potential benefits without guaranteeing savings, rent increases, returns, availability, or charging speed.
- Preserve the vacancy question as unresolved.
- Do not create fabricated testimonials, partner logos, installation counts, certification badges, or customer case studies.
- Do not invent service guarantees, contract length, cancellation fees, or final tariff terms.
- Do not claim numerical carbon savings without supplied evidence and a calculation.
- Identify prototype screenshots and academic project examples appropriately.
- Use the proposal's wording and meaning as the factual base; the suggested copy and calculator in this brief are implementation recommendations.

## 12. Suggested implementation order

1. Read the proposal and design guidelines; inventory the repository and approved assets.
2. Confirm content hierarchy, routes, language, and site/app connection from the available material.
3. Build shared brand styles, header, footer, and responsive page structure.
4. Implement the landing page using the proposal-based content above.
5. Implement the business-model page, payment-flow explanation, and vacancy comparison.
6. Implement the small scenario calculator and verify the provided cases.
7. Add verified app previews and working links.
8. Implement the contact flow in its configured live or explicitly labelled demo mode.
9. Check responsive layouts, accessibility, claims, assets, and page behaviour.
10. Provide a deployment-ready handoff with the remaining commercial and publication decisions documented.

## 13. Acceptance criteria

- [ ] The website follows the supplied design guidelines and uses the actual approved repository assets.
- [ ] The first screen explains shared charging for residential apartment buildings.
- [ ] Landlords and property managers are clearly the contracting customers.
- [ ] Residents are shown as users who pay separately for measured electricity.
- [ ] The subscription is per billable apartment, not per charging point or individual EV user.
- [ ] The 20 apartments / 5 chargers / 20 subscriptions example is labelled as full occupancy and illustrative.
- [ ] Dynamic electricity tariff plus provider markup is explained without invented prices or guaranteed savings.
- [ ] App reservations, app/NFC access, property administration, maintenance, updates, and load management are represented accurately.
- [ ] Proposed capabilities are distinguished from what the app demo actually implements.
- [ ] Both vacancy alternatives are visible and neither is presented as decided.
- [ ] The calculator passes the supplied checks, handles invalid and empty inputs, and permits negative calculated contributions.
- [ ] Changing charger count alone does not change subscription revenue.
- [ ] The economics section covers waiting, moving vehicles, coordination, and the main viability drivers.
- [ ] No unsupported customer proof, price promises, profitability claims, or emissions figures appear.
- [ ] Contact behaviour is functional and honest about whether information was sent or stored.
- [ ] App links, page links, fonts, images, and any downloads work in the production build.
- [ ] Mobile layouts, keyboard navigation, FAQ controls, and forms are usable.
- [ ] Missing contact, operator, domain, or integration details are documented rather than invented.

Use focused calculation checks and browser checks of the main visitor journeys. Do not add unnecessary infrastructure or a large test suite for static text.

## 14. OpenClaw handoff deliverables

Provide:

- Complete website source code in the appropriate repository.
- Organised page copy and configuration.
- Reused brand assets with their sources and actual paths documented.
- A README with exact local run, build, and deployment instructions.
- An environment-variable example containing placeholders only, if configuration requires it.
- A description of the app link and whether it points to a demo or live application.
- A clear description of contact mode and any remaining delivery configuration.
- The assumptions used in the calculator and evidence that the supplied checks pass.
- A short list of unresolved project decisions: vacancy billing, commercial prices, actual operating/contact details, and unimplemented hardware or payment capabilities.
- A concise summary of completed features, verification, and remaining limitations.

Keep the website ready for the user to deploy through OpenClaw. Do not publish invented operator details or silently turn demo enquiries into real submissions.

## 15. Source and interpretation notes

**Primary source:** `VoltoShare_Expose_DE(2).pdf`, “Gemeinsam genutzte Ladeinfrastruktur für Mietwohngebäude”, project proposal dated 15 October 2026, page 1. Sections 1 to 5 define the product, financing, platform, customer benefit, and economic evaluation. The highlighted final box leaves vacancy billing open.

**Additional user requirements:** reuse the separately supplied design guidelines, logos, fonts, and other assets available in the repository or asset package; deliver this document as implementation guidance for OpenClaw.

**Recommendations added in this brief:** page structure, draft German copy, contact flow, interactive scenario example, technical organisation, and acceptance criteria. These are implementation decisions, not claims that the proposal already specifies them.

**General rule: explain who pays, what they receive, and which assumptions determine the result. Keep the proposed business model, the demo's actual capabilities, and unresolved terms clearly distinguishable.**
