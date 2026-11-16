# SAR FloodWatch — integrated Streamlit SAR backend

The existing Streamlit app, pages, CSS, navigation, guest entry and optional Supabase login are preserved. The original `run_flood_detection(before, after, method_id)` entry point now runs a complete calibrated SAR change pipeline. Results flow through the existing `images`, `analysis`, `history`, `region`, and `overlay_color` session keys into Flood Detection, Overview/map, Before / After, and Analytics.

## Run on Windows

Use 64-bit Python 3.11 or 3.12. In PowerShell, extract this project, open its folder, and run:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Virtual-environment activation is optional; these commands also avoid PowerShell activation-policy problems. Linux/macOS use `python3 -m venv .venv` and `.venv/bin/python` in place of the Windows executable. GeoTIFF wheels include the required GDAL support; do not install a mismatched system GDAL manually.

## Working workflow

1. Select **Explore live workspace → Flood Detection**.
2. Upload genuine before/after, single-band calibrated SAR GeoTIFFs. Alternatively, **Load sample data** loads the included genuine Sentinel-1 RTC subsets over Sindh. The source scenes, acquisition dates and processing provenance are in `data/sample/metadata.json`.
3. Select the actual SAR sensor and region. Review acquisition dates. Under **SAR calibration and units**, explicitly select each image's units (unless recognized from its tags) and confirm upstream calibration and compatible acquisition geometry.
4. Choose **SAR darkening (rule-based)** and click the existing **Run Flood Detection** button. The backend aligns the before image to the after image grid, filters speckle, detects backscatter darkening, thresholds and cleans segments. Preview images, mask, overlay and statistics use the processed grid.
5. Open **Overview** for the geospatial flood map, **Before / After** for the preserved comparison slider and optional flood overlay, and **Analytics** for charts, results and history CSV.
6. Expand **Download analysis results** on Flood Detection for mask PNG, georeferenced mask GeoTIFF, statistics CSV, report JSON and flood polygons GeoJSON.

A region choice labels the analysis and centers an empty map; it does not crop or relocate uploaded pixels. When a result exists, the map fits its actual extent. Analysis history is kept in the current browser session only. Download results before ending a session.

## Required imagery

- **Supported:** single-band float or integer GeoTIFF backscatter from calibrated/terrain-corrected Sentinel-1, or compatible processed NISAR L/S-band imagery. NISAR HDF5, complex SLC, raw SAR products and RGB previews are not detector inputs. PNG/TIFF images without a CRS remain preview-only.
- Each detector input must have a valid horizontal projected/geographic CRS and affine geospatial transform. Different grids and CRSs are reprojected with Rasterio bilinear resampling to the **after** grid. This does not replace precise upstream SAR coregistration or terrain correction.
- Use the same polarization, comparable orbit/view geometry, spatial support and radiometric convention (`sigma0` with `sigma0`, or `gamma0` with `gamma0`). Tagged polarization mismatches are rejected. Acquisition geometry and calibration must also be verified by the operator.
- Explicit radiometric units: `db`, `linear_power`, or `amplitude`. For power, dB = `10*log10(x)`; for amplitude, dB = `20*log10(x)`. Nonpositive linear values, NoData, NaN/Inf and nonoverlap are excluded. Positive dB values are valid; signs never infer units. File band scale/offset metadata is applied before unit conversion.
- Optional GeoTIFF tags: `SAR_UNITS`, `ACQUISITION_DATE` (ISO 8601), `POLARIZATION`, `SENSOR`. Unknown units must be selected in the existing page's calibration expander.
- Maximum upload: 60 MB per file, 2,000,000 pixels and 4 bands for previews; detection requires one band and at least 100 overlapping valid pixels. Crop large satellite products externally with Rasterio/GDAL/SNAP first. No file is silently downsampled for detection.

No observations, confidence scores, population exposure or infrastructure damage are invented. The included sample is genuine satellite data, **not a reference segmentation**. Tests also use explicitly synthetic numerical fixtures, which are not installed as application imagery.

## Algorithm and area calculation

`GeoTIFF → validate/scale → align → explicit conversion to dB → 3×3 median speckle filter → before−after change → Otsu threshold with a 2 dB minimum → low post-event backscatter criterion → 3×3 opening/closing → remove components <9 pixels → valid flood-candidate mask → area/statistics/exports`.

Post-event backscatter must be at most the lower of −12 dB or the 65th percentile of valid filtered post-event values. These are exploratory defaults, not calibrated universal water thresholds. Nearest-valid fill is used only at speckle-filter boundaries; final segmentation and statistics always exclude invalid pixels. NoData is exported as 255 in the GeoTIFF; valid nonflood is 0 and candidate flood is 1. PNG is binary 0/255 and has no georeferencing.

Projected areas use the full affine determinant and CRS axis-unit conversion, including rotated grids and non-metre units. Equal-area projections use that determinant directly. Other projected CRSs are corrected for ellipsoidal projection distortion **per pixel**, using local areal scale for SAR cells up to 1 km, or geodesic corner polygons for coarser cells. This avoids treating distorted Web Mercator/UTM grid metres as ground area. Small-cell scale correction has negligible within-pixel curvature error at SAR resolutions; coarse-cell polygon edges approximate the projected boundary by geodesic corner-to-corner segments. Geographic grids use ellipsoidal polygon areas per pixel (one calculation per row for north-up grids), rather than a center-pixel approximation. Total and flooded areas sum only valid pixels. The existing percentage is explicitly the flooded fraction of valid pixels. For geographic grids with varying pixel areas, this can differ from the fraction of area.

Map overlays are actually warped to north-up **Web Mercator** with nearest-neighbor resampling before placement on Leaflet; transforming just the bounds would misplace projected/rotated rasters. Map rendering is capped at 1600 pixels per side; exports and statistics use the full detection grid. Geographic display is limited to ±85° latitude; exports are still available beyond that range.

This is a **rule-based, non-deep-learning** flood-candidate detector. Darkening may also reflect radar shadow, crop/soil changes, wind, terrain or acquisition differences; vegetation/urban flooding can brighten SAR and be missed. Permanent water is not an independent mask; terrain, land cover and flood ground truth are not bundled. Validate against independent evidence before interpreting results as inundation.

## Genuine sample and reproducible retrieval

Included `data/sample/before.tif` and `after.tif` are 512×512, 10 m VV gamma0 RTC subsets near 26.65°N, 67.8°E, Sindh. They were retrieved from the Microsoft Planetary Computer Sentinel-1 RTC collection using its documented STAC and floating-point GeoTIFF subset APIs; no rendered preview or display rescaling is used. Both dates use Sentinel-1A ascending relative orbit 42. Contains modified Copernicus Sentinel data (2022), processed by Microsoft. Full IDs, original asset URLs, dates, attribution and license link are recorded alongside the files.

To refresh these observations (requires HTTPS; no API credentials):

```powershell
.\.venv\Scripts\python.exe tools\fetch_real_pair.py
```

The script selects actual available scenes from the specified date ranges; no flood extent or ground truth is fabricated. It defaults to a point with compatible orbit coverage; arbitrary coordinates may have no matching track. External catalog availability and collection retention are outside the app's control.

## Satellite discovery and optional downloads

Expand **Find satellite scenes (NASA ASF catalog)** on Flood Detection. Search by longitude/latitude or west,south,east,north bounding box, dates, Sentinel-1/NISAR and polarization. The default AOI is Sindh. Sentinel-1 searches request GRD_HD to avoid raw/metadata-only products. Download returned real catalog metadata as JSON. See [ASF Search documentation](https://docs.asf.alaska.edu/asf_search/basics/) and [Planetary Computer Sentinel-1 RTC](https://planetarycomputer.microsoft.com/dataset/sentinel-1-rtc).

ASF GRD/SLC products are **not automatically analysis-ready**. Downloading does not calibrate, coregister, terrain-correct or convert products for this detector. NISAR catalog availability/product types vary; only a compatible processed GeoTIFF is accepted by the upload path.

Authenticated ASF downloads are available to an operator through `utils.catalog.download_scene(scene_id, destination)`. Set `EARTHDATA_TOKEN` in the server environment (Earthdata Login, with the required data access permissions). The token is never requested in the public UI or written to reports. A 4 GiB preflight size limit protects the demo from unexpectedly large products. This is a separate operator download, not an automatic analysis action. Manual GeoTIFF upload and the included sample work without satellite credentials.

```powershell
$env:EARTHDATA_TOKEN = "YOUR_EARTHDATA_TOKEN"
.\.venv\Scripts\python.exe -c "from utils.catalog import download_scene; download_scene('VERIFIED_ASF_SCENE_ID', 'downloads')"
```

## Optional trained U-Net

No trained checkpoint is bundled and the rule-based detector runs independently of PyTorch. Selecting U-Net without a checkpoint returns a useful error and no invented mask.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml-optional.txt
$env:FLOODWATCH_UNET_CHECKPOINT = "C:\models\your_trained_checkpoint.pt"
$env:FLOODWATCH_DEVICE = "cpu"  # or cuda with a compatible GPU/PyTorch installation
```

The adapter expects the exact two-input/one-output architecture from `utils.unet.build_unet(base_channels)`: two U-Net encoder levels, skip connections, a bottleneck and a binary-logit head. Channels are ordered **before dB, after dB**. A checkpoint is a `torch.save` dictionary containing:

| Key | Required value |
| --- | --- |
| `architecture` | `floodwatch_unet_v1` |
| `trained` | Boolean `True` supplied by the training operator |
| `provenance` | Actual training dataset, calibration/normalization and validation provenance |
| `state_dict` | Strictly matching, trained model state dictionary |
| `base_channels` | Training architecture width, 4–64; default 16 |
| `mean_db` | Two finite training-set means, in before/after order |
| `std_db` | Two positive finite training-set standard deviations |
| `threshold` | Validated probability threshold between 0 and 1; default 0.5 |

The module checks the contract and strictly loads all weights before any inference. A declaration cannot prove training quality: only use a trusted checkpoint with independently established provenance. An arbitrary third-party U-Net generally needs a compatible adapter or retraining; do not rename it to make it fit. `torch.load(weights_only=True)` is used; only local operator-configured checkpoints are loaded, capped at 256 MB. Models are cached by path, size, mtime and device. Inference uses 256-pixel tiles with 32-pixel context halos and reconstructs the original mask, excludes invalid pixels, and records checkpoint SHA-256. CPU is the default; `cuda` is optional. Probabilities are not displayed as calibrated confidence. No randomly initialized model is offered as a working detector.

## Authentication and private state

Guest access needs no credentials or database account. Existing Supabase signup/login remains available:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-auth-optional.txt
```

Configure server environment variables or `.streamlit/secrets.toml`:

```toml
SUPABASE_URL = "https://YOUR_PROJECT.supabase.co"
SUPABASE_ANON_KEY = "YOUR_PUBLIC_ANON_KEY"
```

Use a public anon/publishable key, never a service-role key. Supabase handles password storage; this application never writes passwords. There is no new shared analysis database: rasters, reports and history stay in the individual Streamlit session. Logout and successful identity changes clear imagery, results, imports and history. Exports are explicit downloads. If adding persistent storage later, enforce ownership using authenticated server identities and database row-level security. Do not use a user-entered ID as an authorization boundary.

`.env.example` documents optional variables; `.env` is not automatically loaded. Set variables in the process environment or use Streamlit secrets for Supabase. Never commit secrets.

## Verification

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe tests\ui_smoke.py
.\.venv\Scripts\python.exe -m playwright install chromium
# Keep Streamlit running in another terminal:
.\.venv\Scripts\python.exe tests\browser_workflow.py --url http://localhost:8501
```

Pytest covers raster loading, explicit radiometric conversion, scale/offset, alignment/reprojection, CRS validation, NoData, no-flood cases, segmentation, shape, geospatial areas, exports, model-load failures and the existing Streamlit Run button/page integration. Optional PyTorch tests skip when torch is absent. The browser script uploads the genuine included GeoTIFFs, runs detection, downloads all exports, checks the dashboard Leaflet overlay, zoom/pan, comparison slider/overlay, analytics and history CSV. It then independently reads back exported pixels, source hashes, georeferencing, CSV values and GeoJSON geodesic area. Browser artifacts default to `work/browser-results/`. See `VALIDATION.md` for executed checks and remaining limits.

## Source map

- `app.py`, `pages/`, `components/cards.py`, `utils/styles.py`: preserved router and UI; result/download/catalog controls integrated into the existing page.
- `utils/image_processing.py`: original interfaces plus explicit units, raster validation, per-pixel areas, reprojection and preview utilities.
- `utils/model_interface.py`: preserved detector signature and dataclasses; results additionally carry aligned inputs, validity and processing metadata.
- `utils/exports.py`: PNG/GeoTIFF/CSV/JSON/GeoJSON serialization.
- `utils/unet.py`: optional trained checkpoint adapter and tiled CPU/GPU inference.
- `utils/catalog.py`: real ASF metadata discovery and operator Earthdata downloads.
- `tools/fetch_real_pair.py`: reproducible genuine RTC sample retrieval.

For a hosted deployment, configure per-process memory/concurrency limits and HTTPS; this bounded Streamlit demo is not a validated operational flood-warning service.

Project video demo : https://vimeo.com/reviews/c4a9403c-4f89-4199-aad5-1b6ef01b8978/videos/1247179045
