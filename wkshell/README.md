# webkit-layer-shell

Display a WebKit web view on a Wayland layer-shell surface (background,
bottom, top or overlay layer of a chosen monitor). Useful for desktop panels,
widgets and shell components on wlroots-based compositors.

This is a **Python 3 port** of `wkshell/example.c` (the C utility built
against WebKitGTK 4.1, GTK 3 and gtk-layer-shell). It uses the same libraries
via PyGObject (GI bindings), so it requires:

* `python3-gobject` (PyGObject)
* `gtk3`
* `webkit2gtk4.1` (WebKitGTK 4.1 typelib)
* `gtk-layer-shell` (GtkLayerShell-0.1 typelib)

## Usage

```text
webkit-layer-shell [options] [--] [URL]

Options:
  --layer=LAYER        background|bottom|top|overlay (default: top)
  --keyboard=MODE      none|on-demand|exclusive (default: exclusive)
  --monitor=N          monitor index (-1 = primary, default)
  --top --bottom --left --right   anchor flags
  --width=SIZE         pixels or percent, e.g. 800 or 50%
  --height=SIZE        pixels or percent, e.g. 600 or 10%
  --margin=PX          margin for all edges
  --margin-top/-bottom/-left/-right=PX
  -h, --help           show help
```

Examples:

```text
webkit-layer-shell --top --bottom --left --right https://example.com
webkit-layer-shell --top --left --width=360 --height=220 --margin=16 https://example.com
webkit-layer-shell --top --left --right --height=48 file:///home/user/panel/index.html
webkit-layer-shell --width=50% --height=50% https://example.com
webkit-layer-shell --monitor=1 --width=30% --height=20% https://example.com
```

Press `Escape` to quit.

## Differences from the C original

* `--keyboard` is actually applied via `gtk_layer_set_keyboard_mode()`
  (the C original parses and validates the option but never applies it).
* Exit codes and message formats are identical: 2 for command line errors,
  1 for runtime errors, warnings prefixed with `webkit-layer-shell: warning:`.

## Packaging

The spec `webkit-layer-shell.spec` targets EPEL 10 (AlmaLinux 10 /
Fedora EPEL 10). Note that `gtk-layer-shell` is **not yet packaged for
EPEL 10**; a companion package for it lives in the same OBS project
(`home:like-me/gtk-layer-shell`) so the runtime dependency resolves.
