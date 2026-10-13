# Preview log

## 2026-10-13: CP-2 (PHASE 2): the real map with flood layers
- **Shown:** Overview at 1440 px with card C1 as a real Leaflet map: OpenStreetMap basemap, dashed study zone, flood layer for the selected scenario, road outline (major roads dark, minor roads pale), layer toggles, area statistics, attribution. English (observed, mild, severe), Tamil (severe) and Hindi (mild) were captured; the Tamil capture was inspected, the Hindi one was captured but not opened.
- **Real:** the flood layers (observed composite = union of OpenCity layers, 41.6 km2 of 70.2; simulated mild 28.4, moderate 49.0, severe 59.1), the road outline (12,330 nodes, 30,403 edges, today's roads), the scenario switch, the area statistics.
- **Placeholder:** all five KPI values and cards C2 to C6 ("Not built yet"); no routes, facilities or road classes yet.
- **Found and fixed during this phase:** (1) the first scenario buffers (-100, 0, +150 m) gave 2% and 100% of the zone, so they were recalibrated (docs/DATA_LIMITS.md); (2) the flood fill hid the roads, so roads now draw on top and are styled by hierarchy; (3) the dev server served stale CSS after edits, fixed by restarting it; (4) the in-app browser pane's capture of an emulated 1440 px viewport comes out scaled into a corner, so wide screenshots use a separate headless browser.
- **Known limits:** the road outline is dense at this zoom; the map cannot be panned beyond the basemap tiles' needs offline (tiles need internet); the observed composite is not a real observed extent; the severe scenario is an arbitrary +30 m buffer.
- **User decision:** pending.

One entry per preview checkpoint (blueprint Section 14.12). Screenshots are taken from the running app in a browser pane; none is a mockup.

## 2026-10-13: PHASE 1 skeleton preview (before CP-2)
- **Shown:** the preview skeleton at 1440 px width, Overview page in English, Tamil and Hindi; the Data and limits page in Hindi (Tamil and English load without errors in the smoke tests but were not photographed on that page).
- **Real:** layout, teal theme, left rail (sidebar with Material icons), header, language selector (English, தமிழ், हिन्दी), event pill, scenario and focus controls, the persistent simulation banner, five KPI card frames, six overview card frames, the Data and limits page (four standing gaps with an "original English" line, datasets table, assumptions table, translation status).
- **Placeholder:** every KPI value and chart ("Not built yet"); the Route explorer page.
- **Checks:** banner visible in all three languages; Tamil and Hindi render with no missing-glyph boxes on this machine; long Tamil labels wrap and are not truncated.
- **Found and fixed during the preview:** the default Streamlit red and black widget theme clashed with the teal design (fixed with `.streamlit/config.toml`); the scenario control was cut off at narrow widths (moved to its own full-width row).
- **Known limits:** the left rail is a standard sidebar with icons and labels, not an icon-only rail (accepted fallback, blueprint 6.2); cards in one row can have unequal heights when captions wrap.
- **User decision:** the user asked for the look of the reference image (twice), then asked to use Next.js, then supplied a reference website (shpp3.vercel.app) and chose the "blend" style. The Streamlit skeleton was replaced (see next entry).

## 2026-10-13: PHASE 1 skeleton in Next.js, final style (supersedes the blend entry below)
- **User decision:** after the blend preview the user sent the reference image again and asked for "front ui/ux like this and blue color palette". The interface was restyled to the image's look (floating rail with a round blue logo, raised 24 px cards, dark and pale pill toggles with a blue selected state, large grey title, event pill top right) with a blue accent. The thin-border website style was dropped.
- **Shown:** Overview in English, Tamil and Hindi at 1440 px, captured with a separate headless browser against the running dev server (the in-app pane's capture of an emulated 1440 px viewport came out scaled into a corner, so it was not used). The pane at its own narrow width was also checked.
- **Found and fixed:** the header controls first stacked down the left side instead of sitting top-right opposite the title; the right-hand group is now flexible so long Tamil labels wrap without crowding.
- **Real vs placeholder:** unchanged from the entry below (layout, theme, language switch and the Data and limits page are real; every KPI value and chart is "Not built yet").
- **Not yet checked at this style:** the Data and limits page and the Route explorer page (checked only before the restyle), and any width between the narrow pane and 1440 px.
- **User decision:** pending (commit of PHASE 1).

## 2026-10-13: PHASE 1 skeleton in Next.js, blend style (earlier iteration)
- **Reference website reviewed:** shpp3.vercel.app ("Project 96", an unrelated registry app) was used only as a styling reference. Its demo dashboard did not load ("Unable to load demo dashboard"), and its login shows demo credentials on the page; none were entered. Styling values were read from the public login screen's computed styles.
- **Shown:** `http://localhost:3000` at 1440 px: Overview in English and Tamil; the Data and limits page in Hindi.
- **Real:** icon rail with logo, header (title, scenario and language segmented controls, event pill, focus toggle), persistent simulation banner, five KPI card frames, six card frames in an equal 3 x 2 grid, the Data and limits page (gaps with "original English", datasets, assumptions, translation status).
- **Placeholder:** all KPI values, charts and the Route explorer ("Not built yet"); the dashed lines in the KPI cards are decorative, not data.
- **Checks:** `tsc --noEmit`, `npm run lint` and `npm run build` pass; Tamil and Hindi render without missing-glyph boxes; Tamil labels wrap and the header re-flows; 35 Python tests pass (dictionary and config sync with the web copies included).
- **Known limits:** the Hindi page was looked at in a small screenshot; Route explorer is a placeholder; the Next.js dev indicator shows in the corner in development only; fonts need an internet download once.
- **User decision:** pending (commit of PHASE 1, study zone, blend style).

## 2026-10-13: PHASE 3 (no new screenshot; the dashboard UI is unchanged except the map now shows the redesigned scenario layers)
- **Real:** edge classification, flood-modified graph, routing with unreachable handling, facilities and simulated starts, 61 passing tests.
- **User decision:** option 1 (seeded subset scenarios) after the buffered scenarios isolated every facility.

## 2026-10-13: CP-4 (PHASE 7): KPI cards and charts with real values
- **Shown:** `docs/previews/cp4_moderate_en.png`, `cp4_mild_ta.png`, `cp4_severe_en.png`, `cp4_observed_hi.png` (1440 px, headless Edge against the running dev server). I opened the English moderate, Tamil mild and Hindi observed captures; the English severe one was captured but not opened.
- **Real:** five KPI cards with sparklines across mild, moderate, severe; coverage by scenario (C2), road segments by class (C4), reachability by facility (C5), origins by travel-time increase (C6). Default scenario is now moderate.
- **Placeholder / not built:** isolation card (C3, "Planned, not built"), Route explorer page, explanation text, audit download.
- **Honest limits:** observed composite shows a "not routed on" message instead of numbers; severe shows 0% reachability everywhere (cliff effect, see docs/DATA_LIMITS.md); travel-time increase is empty for moderate and severe; Tamil and Hindi are drafts.
- **User decision:** pending.

## 2026-10-13: CP-5 (PHASE 9, part): Route explorer and explanation text
- **Shown:** `docs/previews/cp5_route_mild_en.png`, `cp5_route_moderate_ta.png`, `cp5_route_severe_hi.png` (1440 px, headless Edge, dev server). All three were opened. Page address `?page=route&scenario=...&lang=...` opens the explorer directly.
- **Real:** start picker (6 simulated ambulance starts, 20 sample origins), map with the conventional route (dashed grey), blocked segments on it (red), flood-aware route (blue), facilities with verification badge in the tooltip, result panel, explanation sentences, unreachable-facility list with reasons. Sentences are built in Python (`src/explain.py`) from computed values only, for each of the three languages; facility names are never translated.
- **Not built:** audit log download, isolation card, Metrics table and Export pages. The observed composite is not routed on and says so.
- **Notes:** the unreachable facilities appear both in the explanation and in the list below it (duplication is deliberate). The basemap's own red cross icons are OpenStreetMap hospital symbols, not this app's facilities (which are the blue and grey circles).
- **User decision:** pending.
