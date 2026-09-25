# Third-party code

`cgltf.h` and `cgltf.LICENSE` are from cgltf 1.15, commit `360db1a`.

`masked_occlusion_culling/` is Intel/Lund University's MaskedOcclusionCulling,
commit `6cbbd7621cce670cf081a44272669e240300879e`, under Apache-2.0. Its two
compiler-helper names are locally prefixed to avoid collisions with GCC 15 intrinsics;
non-MSVC builds disable strict-aliasing optimization as required by its SIMD implementation.

`miniz.c`, `miniz.h`, and `miniz.LICENSE` are miniz 3.1.2, commit
`77d0dce8627735138c51770d1799a1ef48f2117d`, used to unpack verified
automatic-update packages.

`picosha2.h` and `picosha2.LICENSE` are PicoSHA2, commit
`161cb3fc4170fa7a3eca9e582cebd27cc4d1fe29`, used to verify update SHA-256
digests.

`vrf_licenses/` records the exact ValveResourceFormat 19.2 release files,
restored package graph, and redistribution notices copied into core packages.
