# Interactive financial scenarios — 24 November 2026

The website and presentation use one deterministic engine, `website-src/finance-model.mjs`, and the same accessible UI component, `finance-ui.mjs` / `finance.css`. No backend, remote calculator service or third-party CDN is required. Editing these scenarios never changes resident invoices or app transactions.

## Sources and the two distinct pricing units

The supplied `Voltoshare_Slides_Final.pptx` and `VoltoShare Profitrechner.html` are different scenarios. Do not silently combine their pricing models.

- **Zürich — original presentation, slides 12–15:** 60 apartments, 15 charging points, 24 EVs, 2,500 kWh/EV/year. The landlord subscription is CHF 25 **per billable apartment per month**. Energy markup is 6 Rp./kWh. Investment is 15 × CHF 3,000 plus CHF 15,000 for connection/load management. Annual platform CHF 1,800; maintenance 4% of investment; other operating costs CHF 1,500.
- **Cham — supplied standalone calculator:** 270 apartments, 70% parking share, 11.9% EV share, four users per box. This newer alternative uses CHF 55 **per wallbox per month**, not per apartment. The interface explicitly names it an alternative model. It does not replace the proposal's apartment subscription business model.

All supplied prices and projections remain team scenario assumptions, not a commercial offer, proven result or independently verified current tariff. The two supplied original documents remain unchanged.

## Baseline reconciliation

| Measure | Zürich deck | Cham calculator |
|---|---:|---:|
| EVs | 24 | 22 (rounded demand) |
| Charging points | 15 | 6 (rounded up) |
| Annual energy | 60,000 kWh | 42,900 kWh |
| Initial investment | CHF 60,000 | CHF 17,400 |
| Annual subscription / compensation | CHF 18,000 | CHF 3,960 |
| Annual cash operating surplus | CHF 15,900 | CHF 4,807.92084 |
| Annual EBIT | Not supplied | CHF 3,067.92084 |
| Simple payback | 3.77358 years | 3.61903 years |

Zürich's annual cash surplus is subscription + energy margin − platform − maintenance − other costs. The source does not specify depreciation life or gross electricity purchase price. Accordingly, the engine returns `ebit: null` and `revenue: null`; it does **not** mislabel net energy margin as gross turnover or invent depreciation. `netRevenue` is subscription plus energy margin.

Cham reproduces the supplied annual cash result, allocated-acquisition EBITDA, depreciation and EBIT. It retains all source calculator input levers: building/parking/EV demand, parties per charger, charger power, mileage/consumption/home charging, battery capacity, day/night slots and durations, per-charger compensation, electricity purchase/markup/losses, hardware/installation/subsidy/lifetime/payment fees/backend/service/overhead, optional acquisition/contract years and public charging comparison.

## Explicit corrections and boundaries

1. **Zero demand:** the supplied calculator forced at least one EV household. Here 0% EV or no apartments yields zero EVs/boxes and no fictitious sales. Tenant comparison becomes unavailable rather than dividing by zero.
2. **Acquisition cash:** optional acquisition is paid once at year 0. Its contract-year allocation remains visible in the source-style annual EBITDA/EBIT calculation, but is added back for annual operating cash. It is not paid twice in the cumulative cash chart or payback denominator.
3. **Vacancy:** Zürich provides both continue/pause subscription alternatives. Paused subscriptions and potential rental income use expected occupied apartments (`flats × (1 − vacancy/100)`), which may be fractional as an annual average. The full-occupancy subscription baseline still reproduces CHF 15,900. At the source's 0.1% vacancy assumption, potential landlord surplus is CHF 10,771.20 rather than the deck's unadjusted CHF 10,800; this difference is explained next to the table. EVs and consumption remain independent demand assumptions.
4. **Capacity is not a promise:** slot overbooking, insufficient charging time, battery limits, >24 combined slot hours and energy demand without chargers produce warnings. Warning states do not silently reduce the requested annual energy or change the financial assumption. Slot feasibility is not a booking schedule or battery simulation.
5. **Bounds:** recognized numeric inputs are finite and clamped to documented UI bounds; physical counts are rounded to whole numbers. Unknown keys are dropped. Invalid/blank live edits leave the last valid result visible with an explanatory validation message.
6. **Cashflow:** year 0 is negative initial investment, then a constant annual operating cash surplus. Zürich shows ten years; Cham uses the selected equipment life. This is a sensitivity illustration, not a growth forecast or discounted cashflow valuation. Taxes, financing, inflation and replacement investment are excluded. A nonpositive annual cash result returns no payback; a payback beyond the displayed horizon is labelled.
7. **Comparison:** Cham resident costs reproduce the supplied compensation allocation and WWZ/public alternatives. The WWZ prices are converted from inclusive to exclusive of 8.1% VAT; owner-financed WWZ installation is not included in the monthly comparison. The display states these are different services and not guaranteed savings.

## Component integration

```js
import {mountFinance, readFinanceState} from '/finance-ui.mjs';
import {calculateFinance} from '/finance-model.mjs';
const component = mountFinance(element, {
  preset: 'zurich', // or 'cham'
  compact: true,   // quick controls + chart for a presentation
  sync: true,      // browser-local persistence and same-preset synchronization
});
component.getState();  // {preset, values}
component.getResult(); // calculated result
component.setState({values: {subscription: 35}});
component.destroy();
const snapshot = calculateFinance(readFinanceState('zurich'));
```

Mounting never overwrites another preset. Storage key `voltoshare-finance-v1` contains `{version:1,presets:{zurich:{...},cham:{...}}}`. Same-origin components synchronize matching presets through `voltoshare:finance-change` with `{state,result,source}` and browser `storage` events. Switching presets preserves each preset's previous edits. `sync:false` mounts source baseline values without reading or writing storage. `destroy()` removes listeners. Origins have separate browser storage; app links/embeds should intentionally use the same website origin if a shared presentation scenario is desired.

The result's shared fields are:

```
state, preset, investment, annualCash, ebitda, ebit, revenue, netRevenue,
subscription, energyMargin, costs, energy, evs, chargers, payback,
horizon, cashflow: [{year,value}], warnings
```

Zürich additionally exposes occupied/billable apartments, rent, landlordNet and maintenance. Cham exposes energy revenue/cost, payment/backend/service/overhead, acquisition and its annual allocation, depreciation, capex, tenant comparison, and slot feasibility. Use these shared results for exports, never a second copied formula.

## Checks

`node --test website-src/finance-model.test.mjs` covers source baselines, sensitivity, vacancy units, zero demand, losses, acquisition double-count prevention, subsidy bounds, technical infeasibility, invalid inputs and finite outputs. Browser checks should additionally verify immediate chart updates, scoped controls with two instances, local persistence per preset, reset, keyboard access, compact layout and mobile 360/768/1440px. Exact chart data is also available as an HTML table; colour is not the only representation.


## Presenter interaction — 25 November 2026

The shared compact UI now occupies an integrated Live-Szenario step after original slide 14. Open it anytime with the player toolbar or **F**; `/praesentation/?live=1` opens it directly. Four slider/number levers offer rapid discussion, with every remaining assumption accessible below. The original 51 slides and static PDF/PPTX remain unchanged. See `FINANCE_LIVE_RELEASE_2026-11-25.md`.
