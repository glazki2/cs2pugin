# ValveResourceFormat CLI

CS2FOW packages Source2Viewer-CLI release 19.2 (build 19.2.6339) from the official ValveResourceFormat
release assets. Their SHA-256 values, exact packaged files, dependency graph,
and licenses are recorded in `third_party/vrf_licenses/DEPENDENCIES.txt`.

The binaries are not committed to git. For local packaging, place the extracted
CLI files here:

```text
tools/vrf/win64/Source2Viewer-CLI.exe
tools/vrf/linux64/Source2Viewer-CLI
```

GitHub Actions downloads the matching `cli-windows-x64.zip` and
`cli-linux-x64.zip` assets during the build.
