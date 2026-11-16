# Existing frontend integration contract

The implementation updates this uploaded application in place. It does not introduce a separate API server or replace the frontend.

## Preserved entry points and types

| Existing interface | Integration behavior |
| --- | --- |
| `utils.model_interface.run_flood_detection(before, after, method_id)` | Same signature. Executes the selected method. The result is on the after-image grid. |
| `Raster` | Original field order/properties retained; optional `radiometry` and `metadata` added. Radiometric units must be declared for detection. |
| `DetectionResult` | Original `mask`, `model_name`, `confidence` retained; optional validity, aligned input rasters and processing metadata added. |
| `DetectionMethod` / `METHODS` | Same dataclass fields and method IDs (`sar_change`, `unet`). U-Net requires an operator's compatible trained checkpoint. |
| `load_raster`, `validate_upload`, `check_alignment` | Original signatures retained. Alignment checking remains a pure check; `prepare_pair` performs reprojection. |
| `compute_flood_stats` | Same first three arguments and original result fields; additionally supports per-pixel ellipsoidal ground areas and reports `valid_pixels`. |
| Display/overlay helpers | Original signatures retained. All comparison images and masks share the processed grid after detection. |

## State and call flow

1. The existing `_sync_upload` callback validates and loads each upload. It fingerprints content, clears stale results, reads acquisition tags and stores original input rasters separately from processed display rasters. A same-name/same-size replacement with different pixels is reloaded.
2. Original region/date/sensor/method controls remain. A calibration expander supplies required units and the operator confirmation. The existing **Run Flood Detection** button calls `_run(method.id)`.
3. `_run` validates the inputs, then calls the preserved detector entry point on the original uploaded rasters. Each run uses originals to avoid cumulative resampling if another after image is uploaded.
4. The detector validates single-band geospatial SAR inputs, masks invalid radiometry before reprojection, aligns the before raster to the after grid, and computes a real candidate mask. The optional U-Net branch refuses missing/untrained/incompatible checkpoints.
5. `_run` adopts `result.before`/`result.after` into `st.session_state['images']`, checks mask shape/finite values, and passes the actual validity and metadata into `_make_analysis`.
6. `_store_analysis` updates `st.session_state['analysis']` and appends a mask-free record to `st.session_state['history']`. No prediction arrays or user results are cached globally.
7. Existing pages read the same keys: Flood Detection renders four image panels and summary; Overview reads current metrics and `analysis['mask']` for the map; Comparison uses processed `images` and the same mask; Analytics reads `analysis`/`history` and separates charts by region, sensor, exact grid extent and method.
8. All five export formats serialize that analysis. Download buttons use `on_click='ignore'` to prevent download-triggered Streamlit reruns. GeoTIFF NoData is 255, valid background is 0, and flood candidate is 1.

The required `images`, `analysis`, `history`, `region`, and `overlay_color` keys are retained. The pre-existing `images['mask']` slot remains the optional sample reference raster; predicted masks remain in the pre-existing `analysis['mask']` location used by all pages.

Region and color selectors synchronize their widget values with the shared keys across pages. Logout and successful identity changes clear private session results. Authentication stays with the original optional Supabase flow; no shared analysis database is added.

## Preserved presentation files

`app.py`, `utils/styles.py`, `components/cards.py`, `pages/comparison.py`, `pages/landing.py`, `pages/about.py`, and the original theme configuration are byte-for-byte unchanged from the uploaded archive. Navigation, page layout, slider HTML/CSS and authentication forms remain in place. Backend-required controls, summary rows and downloads are added within the existing detection page; the map renderer warps actual pixels before placement.

## Scope boundaries

This backend consumes calibrated, georeferenced backscatter. It does not transform raw Sentinel-1/NISAR products into analysis-ready SAR. Catalog discovery and authenticated operator downloads are separate from processing. No trained weights, ground truth, persistent cross-session history or disaster exposure dataset is fabricated or bundled.
