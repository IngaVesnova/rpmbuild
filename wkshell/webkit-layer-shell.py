#!/usr/bin/python3
# SPDX-License-Identifier: MIT
"""webkit-layer-shell - display a WebKit web view on a Wayland layer-shell surface.

Python 3 port of wkshell/example.c for modern WebKitGTK 4.1 (webkit2gtk4.1),
GTK 3 and gtk-layer-shell, using PyGObject (gi).

Behaviour, options and error messages mirror the C reference implementation
(exit status 2 for command line errors, 1 for runtime errors).
"""

import sys
from typing import NoReturn

import gi  # type: ignore[import-not-found]

gi.require_version("Gtk", "3.0")
gi.require_version("WebKit2", "4.1")

from gi.repository import Gdk, Gtk, WebKit2  # noqa: E402  # type: ignore[import-not-found]

try:
    gi.require_version("GtkLayerShell", "0.1")
    from gi.repository import GtkLayerShell  # noqa: E402  # type: ignore[import-not-found]
except (ImportError, ValueError) as exc:
    print(
        "webkit-layer-shell: error: gtk-layer-shell (GtkLayerShell-0.1 typelib) "
        "is required but not available: %s" % exc,
        file=sys.stderr,
    )
    sys.exit(1)

PROG = "webkit-layer-shell"
DEFAULT_URL = "https://example.com"

_LAYERS = {
    "background": GtkLayerShell.Layer.BACKGROUND,
    "bottom": GtkLayerShell.Layer.BOTTOM,
    "top": GtkLayerShell.Layer.TOP,
    "overlay": GtkLayerShell.Layer.OVERLAY,
}

_KEYBOARD_MODES = {
    "none": GtkLayerShell.KeyboardMode.NONE,
    "on-demand": GtkLayerShell.KeyboardMode.ON_DEMAND,
    "exclusive": GtkLayerShell.KeyboardMode.EXCLUSIVE,
}

_EDGES = {
    "top": GtkLayerShell.Edge.TOP,
    "bottom": GtkLayerShell.Edge.BOTTOM,
    "left": GtkLayerShell.Edge.LEFT,
    "right": GtkLayerShell.Edge.RIGHT,
}


def fatal_usage(fmt, *args) -> NoReturn:
    """Report a command line error and exit with status 2 (like example.c)."""
    print("%s: error: %s" % (PROG, (fmt % args if args else fmt)), file=sys.stderr)
    sys.exit(2)


def fatal_runtime(fmt, *args) -> NoReturn:
    """Report a runtime error and exit with status 1 (like example.c)."""
    print("%s: error: %s" % (PROG, (fmt % args if args else fmt)), file=sys.stderr)
    sys.exit(1)


def warning_msg(fmt, *args):
    """Print a warning to stderr (like example.c)."""
    print("%s: warning: %s" % (PROG, (fmt % args if args else fmt)), file=sys.stderr)


def usage():
    print("Usage: %s [options] [--] [URL]" % PROG)
    print()
    print("Options:")
    print("  --layer=LAYER        background|bottom|top|overlay (default: top)")
    print("  --keyboard=MODE      none|on-demand|exclusive (default: exclusive)")
    print("  --monitor=N          monitor index used for percentages and target output")
    print("                       -1 = primary monitor (default)")
    print("                       0,1,2,... = monitor index reported by GDK")
    print()
    print("Anchor flags:")
    print("  --top                anchor to top edge")
    print("  --bottom             anchor to bottom edge")
    print("  --left               anchor to left edge")
    print("  --right              anchor to right edge")
    print()
    print("Size options:")
    print("  --width=SIZE         pixels or percent, e.g. 800 or 50%%")
    print("  --height=SIZE        pixels or percent, e.g. 600 or 10%%")
    print()
    print("Margin options, pixels only:")
    print("  --margin=PX          margin for all edges")
    print("  --margin-top=PX      top margin")
    print("  --margin-bottom=PX   bottom margin")
    print("  --margin-left=PX     left margin")
    print("  --margin-right=PX    right margin")
    print()
    print("  -h, --help           show this help")
    print()
    print("If no anchor flags are given, no anchors are set.")
    print("Fullscreen requires: --top --bottom --left --right")
    print()
    print("Examples:")
    print("  %s --top --bottom --left --right https://example.com" % PROG)
    print("  %s --top --left --width=360 --height=220 --margin=16 https://example.com" % PROG)
    print("  %s --top --left --right --height=48 file:///home/user/panel/index.html" % PROG)
    print("  %s --width=50%% --height=50%% https://example.com" % PROG)
    print("  %s --monitor=1 --width=30%% --height=20%% https://example.com" % PROG)


def parse_int_option(str_, option):
    if str_ is None or str_ == "":
        fatal_usage("%s requires a value", option)

    try:
        value = int(str_, 10)
    except ValueError:
        fatal_usage("invalid integer value for %s: '%s'", option, str_)

    if value < -(2 ** 31) or value > 2 ** 31 - 1:
        fatal_usage("integer value out of range for %s: '%s'", option, str_)

    return value


def parse_layer(str_):
    key = str_.lower()
    if key in _LAYERS:
        return _LAYERS[key]
    fatal_usage("invalid --layer value: '%s' (expected background|bottom|top|overlay)", str_)


def parse_keyboard_mode(str_):
    key = str_.lower()
    if key in _KEYBOARD_MODES:
        return _KEYBOARD_MODES[key]
    fatal_usage("invalid --keyboard value: '%s' (expected none|on-demand|exclusive)", str_)


def get_next_value(i, argv, option):
    """Return argv[i + 1] as the value for the space-separated form of option."""
    if i + 1 >= len(argv):
        fatal_usage("%s requires a value", option)
    return argv[i + 1]


def resolve_size(str_, base_px, option):
    """Resolve a 'PX' or 'NN%%' size against a monitor dimension (like example.c)."""
    if str_ is None or str_ == "":
        fatal_usage("invalid value for %s: empty value", option)

    if base_px <= 0:
        fatal_runtime("invalid monitor dimension for size calculation")

    if str_.endswith("%"):
        number = str_[:-1]

        if len(number) <= 0:
            fatal_usage("invalid percentage value for %s: '%s'", option, str_)

        try:
            percent = float(number)
        except ValueError:
            fatal_usage("invalid percentage value for %s: '%s'", option, str_)

        if percent != percent:  # NaN
            fatal_usage("invalid percentage value for %s: '%s'", option, str_)

        if percent < 0.0 or percent > 100.0:
            fatal_usage("percentage for %s must be between 0 and 100: '%s'",
                        option, str_)

        try:
            return int(base_px * percent / 100.0 + 0.5)
        except (ValueError, OverflowError):
            fatal_usage("invalid percentage value for %s: '%s'", option, str_)

    try:
        value = int(str_, 10)
    except ValueError:
        fatal_usage("invalid pixel value for %s: '%s'", option, str_)

    if value < 0:
        fatal_usage("pixel value for %s must be non-negative: '%s'", option, str_)

    if value > 2 ** 31 - 1:
        fatal_usage("pixel value out of range for %s: '%s'", option, str_)

    return value


def on_key_press(widget, event):
    del widget
    if event.keyval == Gdk.KEY_Escape:
        Gtk.main_quit()
        return True
    return False


def main(argv):
    layer_str = "top"
    keyboard_str = "exclusive"
    url = None

    width_str = None
    height_str = None

    monitor_index = -1

    anchor_top = False
    anchor_bottom = False
    anchor_left = False
    anchor_right = False

    margin_all = 0
    margin_top = -1
    margin_bottom = -1
    margin_left = -1
    margin_right = -1

    no_more_options = False

    i = 1
    argc = len(argv)
    while i < argc:
        arg = argv[i]

        if not no_more_options:
            if arg == "--":
                no_more_options = True
                i += 1
                continue

            if arg in ("-h", "--help"):
                usage()
                return 0

            if arg == "--layer":
                layer_str = get_next_value(i, argv, "--layer")
                i += 2
                continue

            if arg.startswith("--layer="):
                layer_str = arg[len("--layer="):]
                i += 1
                continue

            if arg == "--keyboard":
                keyboard_str = get_next_value(i, argv, "--keyboard")
                i += 2
                continue

            if arg.startswith("--keyboard="):
                keyboard_str = arg[len("--keyboard="):]
                i += 1
                continue

            if arg == "--monitor":
                monitor_index = parse_int_option(
                    get_next_value(i, argv, "--monitor"), "--monitor")
                i += 2

                if monitor_index < -1:
                    fatal_usage("invalid --monitor=%d (must be -1 or non-negative)",
                                monitor_index)
                continue

            if arg.startswith("--monitor="):
                monitor_index = parse_int_option(arg[len("--monitor="):], "--monitor")
                i += 1

                if monitor_index < -1:
                    fatal_usage("invalid --monitor=%d (must be -1 or non-negative)",
                                monitor_index)
                continue

            if arg == "--top":
                anchor_top = True
                i += 1
                continue

            if arg == "--bottom":
                anchor_bottom = True
                i += 1
                continue

            if arg == "--left":
                anchor_left = True
                i += 1
                continue

            if arg == "--right":
                anchor_right = True
                i += 1
                continue

            if arg == "--width":
                width_str = get_next_value(i, argv, "--width")
                i += 2
                continue

            if arg.startswith("--width="):
                width_str = arg[len("--width="):]
                i += 1
                continue

            if arg == "--height":
                height_str = get_next_value(i, argv, "--height")
                i += 2
                continue

            if arg.startswith("--height="):
                height_str = arg[len("--height="):]
                i += 1
                continue

            if arg == "--margin":
                margin_value = get_next_value(i, argv, "--margin")
                margin_all = parse_int_option(margin_value, "--margin")
                i += 2

                if margin_all < 0:
                    fatal_usage("margin value must be non-negative: '%s'", margin_value)
                continue

            if arg.startswith("--margin="):
                margin_value = arg[len("--margin="):]
                margin_all = parse_int_option(margin_value, "--margin")
                i += 1

                if margin_all < 0:
                    fatal_usage("margin value must be non-negative: '%s'", margin_value)
                continue

            if arg == "--margin-top":
                margin_value = get_next_value(i, argv, "--margin-top")
                margin_top = parse_int_option(margin_value, "--margin-top")
                i += 2

                if margin_top < 0:
                    fatal_usage("margin-top value must be non-negative: '%s'", margin_value)
                continue

            if arg.startswith("--margin-top="):
                margin_value = arg[len("--margin-top="):]
                margin_top = parse_int_option(margin_value, "--margin-top")
                i += 1

                if margin_top < 0:
                    fatal_usage("margin-top value must be non-negative: '%s'", margin_value)
                continue

            if arg == "--margin-bottom":
                margin_value = get_next_value(i, argv, "--margin-bottom")
                margin_bottom = parse_int_option(margin_value, "--margin-bottom")
                i += 2

                if margin_bottom < 0:
                    fatal_usage("margin-bottom value must be non-negative: '%s'", margin_value)
                continue

            if arg.startswith("--margin-bottom="):
                margin_value = arg[len("--margin-bottom="):]
                margin_bottom = parse_int_option(margin_value, "--margin-bottom")
                i += 1

                if margin_bottom < 0:
                    fatal_usage("margin-bottom value must be non-negative: '%s'", margin_value)
                continue

            if arg == "--margin-left":
                margin_value = get_next_value(i, argv, "--margin-left")
                margin_left = parse_int_option(margin_value, "--margin-left")
                i += 2

                if margin_left < 0:
                    fatal_usage("margin-left value must be non-negative: '%s'", margin_value)
                continue

            if arg.startswith("--margin-left="):
                margin_value = arg[len("--margin-left="):]
                margin_left = parse_int_option(margin_value, "--margin-left")
                i += 1

                if margin_left < 0:
                    fatal_usage("margin-left value must be non-negative: '%s'", margin_value)
                continue

            if arg == "--margin-right":
                margin_value = get_next_value(i, argv, "--margin-right")
                margin_right = parse_int_option(margin_value, "--margin-right")
                i += 2

                if margin_right < 0:
                    fatal_usage("margin-right value must be non-negative: '%s'", margin_value)
                continue

            if arg.startswith("--margin-right="):
                margin_value = arg[len("--margin-right="):]
                margin_right = parse_int_option(margin_value, "--margin-right")
                i += 1

                if margin_right < 0:
                    fatal_usage("margin-right value must be non-negative: '%s'", margin_value)
                continue

            if arg.startswith("-"):
                fatal_usage("unknown option: %s", arg)

        if url is None:
            url = arg
        else:
            fatal_usage("unexpected extra argument: %s", arg)

        i += 1

    if url is None:
        url = DEFAULT_URL

    layer = parse_layer(layer_str)
    keyboard_mode = parse_keyboard_mode(keyboard_str)

    if not Gtk.init_check():
        fatal_runtime("failed to initialize GTK")

    display = Gdk.Display.get_default()

    if display is None:
        fatal_runtime("failed to get display")

    n_monitors = display.get_n_monitors()

    if n_monitors <= 0:
        fatal_runtime("no monitors found")

    monitor = None

    if monitor_index == -1:
        monitor = display.get_primary_monitor()

        if monitor is None:
            warning_msg("primary monitor not found, using monitor 0")
            monitor = display.get_monitor(0)
    else:
        if monitor_index >= n_monitors:
            fatal_usage("invalid --monitor=%d (available: -1, 0..%d)",
                        monitor_index, n_monitors - 1)

        monitor = display.get_monitor(monitor_index)

    if monitor is None:
        fatal_runtime("failed to get monitor")

    geometry = monitor.get_geometry()

    if geometry.width <= 0 or geometry.height <= 0:
        fatal_runtime("invalid monitor geometry")

    width_px = -1
    height_px = -1

    if width_str is not None:
        width_px = resolve_size(width_str, geometry.width, "--width")

    if height_str is not None:
        height_px = resolve_size(height_str, geometry.height, "--height")

    width_stretched = anchor_left and anchor_right
    height_stretched = anchor_top and anchor_bottom

    if width_str is not None and width_px > geometry.width:
        if width_stretched:
            fatal_usage(
                "--width=%d exceeds monitor width %d and cannot be used when width is "
                "stretched by anchors", width_px, geometry.width)
        else:
            warning_msg("--width=%d is larger than monitor width %d",
                        width_px, geometry.width)

    if height_str is not None and height_px > geometry.height:
        if height_stretched:
            fatal_usage(
                "--height=%d exceeds monitor height %d and cannot be used when height is "
                "stretched by anchors", height_px, geometry.height)
        else:
            warning_msg("--height=%d is larger than monitor height %d",
                        height_px, geometry.height)

    if width_str is not None and width_px == 0:
        warning_msg("--width is set to 0; the surface may be invisible")

    if height_str is not None and height_px == 0:
        warning_msg("--height is set to 0; the surface may be invisible")

    all_anchors = anchor_top and anchor_bottom and anchor_left and anchor_right

    if all_anchors:
        if width_str is not None or height_str is not None:
            warning_msg("--width/--height have little effect when all anchors are set")
    else:
        if height_stretched and height_str is not None:
            warning_msg("--height is mostly ignored because both --top and --bottom anchors are set")

        if width_stretched and width_str is not None:
            warning_msg("--width is mostly ignored because both --left and --right anchors are set")

    window = Gtk.Window()

    window.set_title("webkit-layer-shell")
    window.set_decorated(False)

    GtkLayerShell.init_for_window(window)
    GtkLayerShell.set_namespace(window, "webkit-shell")
    GtkLayerShell.set_layer(window, layer)
    GtkLayerShell.set_monitor(window, monitor)

    GtkLayerShell.set_anchor(window, _EDGES["top"], anchor_top)
    GtkLayerShell.set_anchor(window, _EDGES["bottom"], anchor_bottom)
    GtkLayerShell.set_anchor(window, _EDGES["left"], anchor_left)
    GtkLayerShell.set_anchor(window, _EDGES["right"], anchor_right)

    mt = margin_top if margin_top >= 0 else margin_all
    mb = margin_bottom if margin_bottom >= 0 else margin_all
    ml = margin_left if margin_left >= 0 else margin_all
    mr = margin_right if margin_right >= 0 else margin_all

    GtkLayerShell.set_margin(window, _EDGES["top"], mt)
    GtkLayerShell.set_margin(window, _EDGES["bottom"], mb)
    GtkLayerShell.set_margin(window, _EDGES["left"], ml)
    GtkLayerShell.set_margin(window, _EDGES["right"], mr)

    # example.c parses --keyboard but never applies the result; apply it here so
    # the documented option actually takes effect.
    GtkLayerShell.set_keyboard_mode(window, keyboard_mode)

    if width_str is not None or height_str is not None:
        window.set_default_size(width_px if width_px > 0 else -1,
                                height_px if height_px > 0 else -1)

        window.set_size_request(width_px, height_px)
    elif not (anchor_top or anchor_bottom or anchor_left or anchor_right):
        # Reasonable fallback for an unanchored surface when no size was given.
        window.set_default_size(800, 600)

    web_view = WebKit2.WebView.new()

    web_view.set_hexpand(True)
    web_view.set_vexpand(True)

    if width_str is not None or height_str is not None:
        web_view.set_size_request(width_px, height_px)

    web_view.load_uri(url)

    window.add(web_view)

    window.connect("destroy", Gtk.main_quit)
    window.connect("key-press-event", on_key_press)

    window.show_all()
    Gtk.main()

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
