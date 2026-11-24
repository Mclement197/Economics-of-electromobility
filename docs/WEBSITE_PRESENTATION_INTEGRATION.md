# Website and resident-app integration — 24 November 2026

This update implements Mathis’s request to simplify the public website and expose the supplied presentation and financial models. It supersedes the earlier homepage FAQ and closing enquiry sections from the original implementation brief.

- The homepage no longer includes the FAQ or closing “Ihre Liegenschaft. Der nächste Schritt.” enquiry panel. Its hero now leads to the concept rather than an unconnected enquiry form.
- Navigation is reduced to Konzept, Geschäftsmodell, Finanzen, Präsentation and App-Demo. The existing contact route remains available directly for compatibility, but is not promoted in the navigation/footer.
- `/finanzen/` mounts the shared financial component via `finance-page.mjs`; `/praesentation/` and the bottom homepage section mount the same presentation renderer through `[data-presentation]`.
- Generated PDF and PowerPoint downloads are copied from the explicit `website-src/downloads/` folder, not from the full source/brand archives. Both downloads represent the documented baseline presentation; changing a local financial scenario does not silently alter a downloaded file.
- The authenticated resident app exposes Financial scenarios and Project presentation in its desktop sidebar and mobile More dialog. They open the public project pages in a separate tab. The labels explicitly separate project simulations from household bills. No database, permissions, reservation, tariff or billing logic is changed.

The builder now requires the finance/presentation source modules and data to be present. Run `scripts/build-website.py` only after those artifacts and the downloads have been generated. App assets still require the normal backup/collectstatic/restart deployment flow; no reset or seed is needed.
