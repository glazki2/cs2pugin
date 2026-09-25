"""Check that Visibility Studio mirrors the native CS2FOW runtime contract."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
STUDIO = Path(__file__).resolve().parent


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def capsule_rows(source: str, pattern: str) -> list[tuple[str, tuple[float, ...]]]:
    rows = []
    for match in re.finditer(pattern, source):
        values = tuple(
            float(value)
            for field in match.groups()[1:]
            for value in re.findall(r"-?\d+(?:\.\d+)?", field)
        )
        rows.append((match.group(1).lower(), values))
    return rows


def main() -> None:
    sampling_h = text(ROOT / "src/core/visibility_sampling.h")
    sampling_cpp = text(ROOT / "src/core/visibility_sampling.cpp")
    worker = text(ROOT / "src/plugin/visibility_worker.cpp")
    settings = text(ROOT / "src/plugin/settings_model.h")
    smoke_h = text(ROOT / "src/core/smoke_occlusion.h")
    smoke_cpp = text(ROOT / "src/core/smoke_occlusion.cpp")
    viewer = text(STUDIO / "viewer.js")
    fps = text(STUDIO / "fps_runtime.js")
    bvh = text(STUDIO / "bvh8.js")
    cfg = text(ROOT / "cfg/cs2fow.cfg")

    native_capsules = capsule_rows(
        sampling_cpp[sampling_cpp.index("k_visibility_capsule_bindings"):],
        r'\{"([^"]+)", \{([^}]+)\}, \{([^}]+)\}, ([^}]+)\}',
    )
    studio_capsules = capsule_rows(
        viewer[viewer.index("const k_valve_hitbox_capsules"):viewer.index("const k_aabb_edges")],
        r'\["([^"]+)", \[([^\]]+)\], \[([^\]]+)\], ([^\]]+)\]',
    )
    assert len(native_capsules) == len(studio_capsules) == 19
    assert native_capsules == studio_capsules
    assert "k_visibility_capsule_count = 19" in sampling_h

    assert "k_visibility_aabb_point_count = 8" in sampling_h
    assert "k_horizontal_bounds_padding = 32.0f" in sampling_cpp
    assert "k_top_bounds_padding = 8.0f" in sampling_cpp
    assert "const k_horizontal_bounds_padding = 32" in viewer
    assert "const k_top_bounds_padding = 8" in viewer
    assert "bot.origin.x - 48" in fps and "height + 8" in fps

    order = [
        worker.index("pair_started < revealed_until_"),
        worker.index("capsule_visible_from_origin(*data_"),
        re.search(r"for \(const vec3\s*&\s*point : aabb_points\)", worker).start(),
        worker.index("if (has_muzzle)"),
    ]
    assert order == sorted(order)

    for native, studio in ((18, "18"), (28, "28"), (36, "36"), (52, "52")):
        assert f"return {native}.0f" in sampling_cpp
        assert re.search(rf"\b{studio}\b", fps)

    assert "k_visibility_origin_count_max = 6" in sampling_h
    assert sampling_cpp.count("add_origin(origins,") == 6
    assert "export function runtime_origins" in bvh
    defaults = {
        "enable {true}": "cs2fow_enable 1",
        "smoke_occlusion {true}": "cs2fow_smoke_occlusion 1",
        "filter_teammates {}": "cs2fow_filter_teammates 0",
        "update_interval_ms {1}": "cs2fow_update_interval_ms 1",
        "worker_threads {2}": "cs2fow_worker_threads 2",
        "shoulder_base_units {64.0f}": "cs2fow_shoulder_base_units 64",
        "shoulder_rtt_scale {0.64f}": "cs2fow_shoulder_rtt_scale 0.64",
        "max_shoulder_units {}": "cs2fow_max_shoulder_units 0",
        "visibility_hold_ms {1000}": "cs2fow_visibility_hold_ms 1000",
        "debug {}": "cs2fow_debug 0",
        "debug_los_player {}": "cs2fow_debug_los_player 0",
    }
    for native, configured in defaults.items():
        assert native in settings and configured in cfg
    assert cfg.rstrip().endswith("cs2fow_config_loaded")

    assert "k_smoke_axis_cells = 32" in smoke_h
    assert "k_ignore_density = 0.1f" in smoke_cpp
    assert "k_opaque_density = 0.8f" in smoke_cpp
    assert "k_block_density = 0.2f" in smoke_cpp
    assert "he_clear_radius_units {100.0f}" in settings
    assert "he_clear_seconds {2.5f}" in settings
    assert "DEFAULT_HE_RADIUS = 100" in fps
    assert "DEFAULT_HE_SECONDS = 2.5" in fps

    # Studio simulates the verified build (all 19 animated capsules); limited mode
    # feeds the same code a smaller hull-shaped body.
    assert "bool blocked = to.capsule_count != 0 && to.capsule_count <= k_visibility_capsule_count" in worker
    assert "k_visibility_probe_capsule" not in worker
    assert "let rawVisible = !valid" in fps and "let indeterminate = !valid" in fps
    assert "using static points" not in viewer
    assert "default_sas_visibility_points" not in viewer
    print("Visibility Studio matches the native runtime contract")


if __name__ == "__main__":
    main()
