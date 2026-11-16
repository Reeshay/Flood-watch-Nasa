# SAR FloodWatch validation

The backend is integrated into the uploaded Streamlit application. The main workflow has been tested through the **existing app in real Chromium**, using genuine Sentinel-1 RTC GeoTIFF uploads. It is not a separate backend-only demonstration.

## Executed checks

| Check | Result |
| --- | --- |
| `python -m pytest -q` | **35 passed** on Python 3.12.14 / Linux, including optional PyTorch CPU tests |
| Existing `tests/ui_smoke.py` | All 8 page render checks passed; this is explicitly a simulated smoke test |
| Streamlit AppTest | Existing guest entry, Run button, shared analysis state, Dashboard, Comparison, Analytics, session clearing, region/color persistence and changed-content uploads passed |
| Streamlit reprojection integration | A shifted GeoTIFF was aligned by the actual Run button; the Comparison page adopted the processed grid and the valid overlap count was correct |
| Real Chromium workflow | Actual file uploads, calibration/sensor controls, Run, four image panels, all five result downloads, real map overlay, loaded basemap tiles, zoom, mouse pan, comparison overlay and keyboard-operated slider, analytics and history CSV passed |
| Export readback | Downloaded GeoTIFF CRS/transform/shape/classes/validity and PNG pixels matched the report; CSV counts/area matched; source SHA-256 matched the uploaded files |
| Independent area cross-check | GeoJSON polygon geodesic area matched the mask-derived area within 0.00001 relative tolerance |
| Projection accuracy tests | Geographic row areas, UTM ground areas, Web Mercator distortion correction, rotated equal-area grid and valid-pixel exclusion passed against independent geodesic/known-area references |
| U-Net tests | Missing/untrained/incompatible checkpoint rejection, corrupt-file failure, normalization contract and CPU tile reconstruction passed. The reconstruction test uses an explicitly deterministic test stub, not an alleged trained model |
| Live NASA ASF discovery | Real anonymous Sentinel-1 GRD_HD scene metadata returned for Sindh, August 2022 |
| Genuine sample retrieval | STAC discovery and floating-point RTC subset retrieval succeeded, with source attribution saved in `data/sample/metadata.json` |

The browser run used the managed environment's configured HTTPS proxy. Its test context explicitly permitted that proxy's TLS certificate; the application and satellite-download HTTP clients retain their normal certificate verification. No authentication credentials were used for the tested workflow. The app server was restarted before the final browser check to verify current processing code.

## Genuine-data workflow result

These are **rule-based flood candidates**, not independently validated flood observations or model confidence estimates. The observations themselves are genuine satellite data. No ground-truth flood mask is bundled.

| Field | Measured result |
| --- | --- |
| Earlier acquisition | 2022-07-10 |
| Later acquisition | 2022-09-08 |
| Source | Sentinel-1A, VV gamma0 RTC; ascending relative orbit 42 |
| Grid | 512 × 512, 10 m; EPSG:32642 |
| Valid analyzed pixels | 262,144 |
| Candidate flood pixels | 74,431 |
| Analyzed ellipsoidal ground area | 26.226141707 km² |
| Candidate flood ground area | 7.446490572 km² |
| Independent GeoJSON geodesic area | 7.446490119 km² |
| Candidate share of valid pixels | 28.393173% |
| Confidence | Not reported; not invented |

`validation/` contains the actual browser-downloaded report, statistics CSV, history CSV, GeoTIFF, PNG, GeoJSON and page screenshots. Georeferenced exports preserve the after-image grid. PNG is a binary visualization without spatial metadata. Rule parameters, actual thresholds, source acquisition tags, source hashes and area calculation notes are in the JSON report.

## Frontend preservation

Byte comparison against the uploaded ZIP confirmed that `app.py`, `utils/styles.py`, `components/cards.py`, `pages/comparison.py`, `pages/landing.py`, `pages/about.py` and `.streamlit/config.toml` are unchanged. The original navigation, authentication forms, two-column detection layout, slider HTML/CSS and theme are retained. Necessary backend controls/exports are placed inside the existing pages. `INTEGRATION.md` documents preserved signatures, dataclasses, state keys and all result consumers.

## Tests not executed / practical limits

- **Native Windows execution:** not available in this Linux environment. Windows commands and wheel-based installation instructions are included in `README.md`.
- **CUDA inference:** no GPU was available. CPU reconstruction and model-failure tests ran.
- **A genuine trained U-Net checkpoint:** none was supplied or bundled. No real trained-model quality/accuracy or actual trained-checkpoint prediction is claimed. U-Net remains unavailable until configured with a compatible trusted checkpoint.
- **Live authenticated Supabase signup/login and Earthdata product downloads:** credentials were not supplied. Guest flow, authentication-page rendering, session isolation/clearing and public catalog discovery were tested. Authentication forms and original SDK flow are preserved.
- **Real processed NISAR input and live NISAR catalog results:** not available for validation. The upload path accepts compatible single-band, calibrated, georeferenced NISAR GeoTIFFs with explicit radiometric units; raw HDF5/complex products are rejected.
- **Operational flood accuracy and concurrent deployment load:** no independent flood ground truth or production load test was supplied. Darkening can reflect other processes; the detector is an exploratory non-deep-learning method. Session history is not a persistent multiuser database.

The installed Folium dependency emits a generic CartoDB API-key notice, but the existing public basemap tiles loaded during the browser test. Streamlit emits deprecation notices for the original `use_container_width` calls; these remain functional in the tested version. Pytest also reports a dependency deprecation from the environment's anyio plugin. None caused a test failure.

## Tested versions

| Package | Version |
| --- | --- |
| streamlit | 1.67.0 |
| streamlit-folium | 0.27.4 |
| folium | 0.20.0 |
| numpy | 2.3.5 |
| rasterio | 1.5.2 |
| pyproj | 3.8.0 |
| scipy | 1.17.0 |
| scikit-image | 0.26.0 |
| asf-search | 14.1.0 |
| pytest | 9.2.0 |
| playwright | 1.62.0 |
| torch | 2.15.0+cpu |

Start with `README.md` for Windows setup and imagery requirements. Run `python -m pytest -q` for automated tests, then launch Streamlit and run `python tests/browser_workflow.py --url http://localhost:8501` for the genuine-data browser workflow. Browser checks require Playwright Chromium and network access for map assets; the included GeoTIFF processing needs no satellite credentials.
