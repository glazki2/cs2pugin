# Test fixtures

These compiled Source 2 resources are copied unchanged from the
ValveResourceFormat test suite (`Tests/Files/`, MIT license, see
`third_party/ValveResourceFormat.LICENSE`). They cover every binary KV3 layout
the native physics reader supports:

| File | KV3 layout | Used for |
| --- | --- | --- |
| `default_ents_kv3_v0.vents_c` | legacy VKV3 | decoder |
| `default_ents_kv3_v1.vents_c` | version 1, LZ4 | decoder |
| `default_ents_kv3_v4_zstd.vents_c` | version 4, Zstandard with blobs | decoder |
| `arch_apartment_ixia_01_top_cap_l_01.vmdl_c` | version 4, LZ4, PHYS block | physics import |
| `unnamed_15451_kv3_v5_uncompressed.vmdl_c` | version 5, uncompressed CTRL + LZ4 PHYS | physics import |

Expected values in `tests/physics_import_tests.cpp` were checked against
ValveResourceFormat 19.2's own decoding and physics GLB export.
