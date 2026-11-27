# Jeni Tools VPM repository

This repository publishes the VCC/VPM catalog and release ZIPs. The builder,
canonical `VRC_Tools` sources, Unity verification project, and metadata snapshots
are in the maintainer's external workspace, not this checkout.
See [the release checklist](#release-checklist) for what can be verified here.

`tools/build_vpm.py` in that workspace builds from `VRC_Tools` into `dist-ready/`.
For verification and missing `.meta` files, it uses the first existing copy in
`MCP Project/Packages/com.jenitool.<tool>`, `MCP Project/Packages/com.suzuki-y0.jeni.<tool>`,
or `MCP Project/Assets/Jeni_tool/<tool>`, with `metadata/` as a fallback for GUIDs.
As of 2026-11-25, the MCP Project still uses the legacy embedded package IDs.
The builder reports which copy it used and does not modify or migrate that project.

The public index is `https://raw.githubusercontent.com/szyey/jeni-tools-vpm/main/index.json`.
New projects should install the unified `liltoon-material-override` package,
which contains the Preset Applicator. Version `0.2.6` clarifies the single Material Override entry,
makes Preset optional in the creation window, and explains that Build-only saves
the Avatar Root configuration while leaving existing Scene/Prefab assets untouched;
Scene apply remains the explicit alternative before Scene Preview checks the lilToon package automatically.
Standalone package 10 is retired and has no public index entries.

The historical source-side static audit and Unity acceptance plan are documented in
[`TOOL_STATIC_AUDIT.md`](TOOL_STATIC_AUDIT.md).

## Current versions

Use VCC or ALCOM to see the latest version for each package in the
[published catalog](index.json).

## Release notes

- **2026-11-27:** `eye-texture-adapter@0.1.7`. The tool is one tabbed window
  (Profile Maker and Transform) that opens on Profile Maker. Profiles start from
  a two-eye or one-eye texture; after the first eye, the second is mirrored by
  shape with or without adjusting. Explanations are shorter and the save hint
  names the unfinished eye. Includes the warp mesh fix from 0.1.6.
- **2026-11-16:** `eye-texture-adapter@0.1.6`. Fixes warp meshes not being
  drawn, which could make the converted texture fully transparent.
- **2026-11-08:** `avatar-reactive-motion@0.1.4`. Transform motions merge into FX so they can read the VRCFT
  template's values; rotation uses quaternions and Generated PhysBone rotates around the target's pivot. Reversed
  response curves reach full strength at the input minimum, turning a Motion off releases its target, and cheek
  shapes without a transfer source no longer stop every Motion. New: pick the parameter from the template's
  expressions, and a reaction direction toggle.
- **2026-11-05:** `eye-texture-adapter@0.1.5`. Both windows are rebuilt with a cleaner look. The converter
  previews by itself, always shows what is missing, and can create the destination profile; the profile
  maker puts the canvas beside the controls, shows one step at a time, and asks before closing unsaved work.
- **2026-11-03 (fourth):** `face-tracking-blendshape-composer@0.1.6`. Opening another recipe no longer
  shows the strength value still being typed in the previous recipe; the saved values were always correct.
- **2026-11-03 (third):** `face-tracking-blendshape-composer@0.1.5`. "Create Composer Component" places
  the template again: the template Prefab no longer uses a reserved object ID that made Unity fail to load it.
- **2026-11-03 (second):** `face-tracking-blendshape-composer@0.1.4`. The LIVE preview is visible while
  NDMF previews are enabled: NDMF previews pause only while LIVE is shown and resume when it ends.
- **2026-11-03:** `face-tracking-blendshape-composer@0.1.3`. The Composer Inspector caches the full
  reference/target mesh comparison instead of repeating it on every repaint, which made it very slow on
  face meshes. Build-time validation still compares the meshes in full every time.
- **2026-10-18 (fourth batch):** `eye-texture-adapter@0.1.4`, `avatar-variant-integrator@0.1.5`.
  The windows explain the tool's purpose and terms (eye profile; canonical avatar and variants) in plain words.
- **2026-10-18 (third batch):** `avatar-y-offset@0.1.5`, `liltoon-material-override@0.2.11`,
  `orbit@0.2.4`, `avatar-reactive-motion@0.1.3`. Windows create and Inspectors adjust: each screen says so,
  windows can open existing configurations, and Avatar Y Offset no longer regenerates from the window over
  values adjusted in the Inspector.
- **2026-10-18 (second batch):** `avatar-y-offset@0.1.4`, `liltoon-material-override@0.2.10`,
  `magic-ray@0.1.5`, `orbit@0.2.3`. A field you clear by hand is no longer refilled from the selection;
  lilToon Outline Animation targets show the renderer and material slot; Orbit errors point to the
  advanced section.
- **2026-10-18:** `avatar-y-offset@0.1.3`, `liltoon-material-override@0.2.9`, `magic-ray@0.1.4`,
  `orbit@0.2.2`, `avatar-variant-integrator@0.1.4`. Windows fill the avatar from the selection,
  Magic Ray and Orbit fold optional settings, and Avatar Variant Integrator shows the next step.
- **2026-10-17:** `facetra-prefab-exporter@0.1.3`, `avatar-variant-integrator@0.1.3`,
  `avatar-y-offset@0.1.2`, `liltoon-material-override@0.2.8`, `magic-ray@0.1.3`. FaceTra Prefab Exporter
  accepts baked meshes whose base vertices FaceTra moved (eye socket option) and has a read-only Japanese
  installer Inspector; the others polish wording and labels.
- **2026-10-03:** maintenance release of every package with bug fixes and a Japanese UI cleanup
  (notably Avatar Variant Integrator analysis and Cigarette controller persistence).

## VCC install

1. In VCC or ALCOM, open `Settings > Packages > Add Repository`.
2. Add `https://raw.githubusercontent.com/szyey/jeni-tools-vpm/main/index.json`.
3. Add the Jeni package you want to the project. Use the green update arrow when a newer release is available.

The update arrow only applies to the same package ID. If a project uses
`com.suzuki-y0.jeni.*`, follow the [migration steps below](#migrate-from-the-old-package-ids).

After adding the URL, use the project manager to install or update packages.
Since `0.2.0`, Orbit contains only
the Orbit Asset Generator; Eye Wobble moved to Avatar Reactive Motion. The generic package menus use English,
descriptive paths under `Tools/Jeni Tools` (with matching
`GameObject`, `Assets/Create`, and `Jeni Tools` component roots where applicable).

Register the NDMF, Modular Avatar, lilToon, and other external repositories in each project as needed.

## Migrate from the old package IDs

The current catalog uses `com.jenitool.*`. An old ID locked in
`Packages/vpm-manifest.json` cannot be restored from this catalog. For packages
listed in the current catalog, keep the suffix and replace `com.suzuki-y0.jeni.`
with `com.jenitool.`. For example, `com.suzuki-y0.jeni.orbit` becomes
`com.jenitool.orbit`. The [unified lilToon package](#liltoon-package-910-integration)
is the exception for the retired Preset Applicator.

1. Close Unity. Back up the entire project, including `Packages`, and work on
   a copy. Do not delete the only installed copy of an old package: the old
   release downloads may be unavailable.
2. In VCC or ALCOM, note the old Jeni Tools packages in the copied project.
   Remove them before adding their replacements. Remove old dependents such as
   Avatar Reactive Motion and FaceTra Prefab Exporter before removing their old
   Face Tracking Blendshape Composer dependency.
3. Add the new IDs from the current catalog. The package manager will install
   dependencies; confirm that no `com.suzuki-y0.jeni.*` entries remain in the
   project's `Packages/vpm-manifest.json` or as installed packages.
4. Open Unity only after the replacement packages are installed. Check for
   compile errors and missing scripts, confirm that Scene and Prefab references
   still resolve, and test the avatar build before replacing the original project.

If the migration fails, keep using the backup with its installed packages;
the current catalog is not an archive of the old IDs.

## lilToon package 9/10 integration

`com.jenitool.liltoon-material-override` is the canonical unified
package. It includes the former Preset Applicator Runtime and Editor sources
under `Legacy/PresetApplicator/` and has no internal dependency on standalone
package 10. Package 10 is retired and absent from the public index; migrate any
project that still references that ID to package 9 `0.2.x` before resolving.
The `Legacy/PresetApplicator/` directory and its historical assembly namespace
are internal contents of package 9, not a second installed package. The
`VRC_Tools/LilToonPresetApplicator` source folder is retained only as build input
for that merged release and is never published as package 10.

The package set deliberately excludes the empty `EyeWobble` folder, legacy
`FaceTraBlendshapeComposer` documents, generated avatar assets, test fixtures,
archives, nested `.git` directories, and the source-only `Outline`, `QVPenSigner`
and `URLDisplay` folders that are not present in the MCP project. `Orbit`
contains only the Orbit Asset Generator; Avatar Reactive Motion owns the
canonical Eye Wobble component. `LilToonMaterialOverride` contains
ProbeAnchorNormalizer.

The source scope is the 13 generic Jeni tools originally mirrored from MCP
`Assets/Jeni_tool`. Their read-only verification copies may now be embedded
packages under the current or legacy IDs. The empty EyeWobble folder is excluded
because the canonical implementation is in Avatar Reactive Motion.
Outline, QVPenSigner, URLDisplay, and Cazalis are separate future work.

If the project has scripts from a manual installation in `Assets/Jeni_tool/<tool>`,
check the project copy for duplicate scripts. Remove only the old tool files;
keep generated assets and user files. VPM does not remove that folder automatically.

## Release checklist

1. Build in the external source workspace. Record its source revision and the
   build tooling used in the GitHub release notes.
2. Add the new ID/version to `index.json` and `release-manifest.json`. Before
   publishing, run `python3 tools/check_catalog.py --zip-dir /path/to/built/zips`.
   The verifier uses published ZIPs for versions not present in that directory.
3. Commit the catalog entries before creating the `<package-id>-<version>` tag.
   Publish the ZIP on that tag before merging the catalog PR so CI can verify
   both the tag and the public download. Keep existing version entries and ZIP
   bytes unchanged; if the bytes change, publish a new version.
4. Verify installation and Unity import/build in a fresh project. The catalog
   check does not replace Unity testing.

Some historical tags predate their catalog entries. Use the current catalog
and its checksums for those releases; do not move existing tags.

## Usage terms

This repository does not state license terms for its downloads. Contact the
maintainer to confirm the terms that apply before redistributing or modifying them.
