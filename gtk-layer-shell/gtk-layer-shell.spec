
Name:           gtk-layer-shell
Version:        0.10.1
Release:        1%{?dist}
Summary:        Library to create components for Wayland using the Layer Shell

License:        LGPL-3.0-or-later AND MIT
Url:            https://github.com/wmww/gtk-layer-shell
Source0:        https://github.com/wmww/gtk-layer-shell/archive/v%{version}/%{name}-%{version}.tar.gz
# OBS's cached AlmaLinux:10 mirror serves a pango-devel build without the
# GIR files; provide the Pango include closure needed by g-ir-scanner.
Source10:       gir-pango-1.0.tar.gz

BuildRequires:  gcc
BuildRequires:  meson >= 0.45.1
BuildRequires:  pkgconfig(gtk+-wayland-3.0) >= 3.22.0
BuildRequires:  pkgconfig(gobject-introspection-1.0)
BuildRequires:  pkgconfig(wayland-client) >= 1.10.0
BuildRequires:  pkgconfig(wayland-protocols) >= 1.16
BuildRequires:  pkgconfig(wayland-scanner) >= 1.10.0
BuildRequires:  pkgconfig(wayland-server) >= 1.10.0
# GIR include closure for g-ir-scanner (RHEL 10 does not pull these
# transitively via gtk3-devel):
BuildRequires:  pkgconfig(atk)
BuildRequires:  pkgconfig(cairo-gobject)
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(harfbuzz)
BuildRequires:  pkgconfig(pango)

%description
A library to write GTK applications that use Layer Shell. Layer Shell is a
Wayland protocol for desktop shell components, such as panels, notifications
and wallpapers. You can use it to anchor your windows to a corner or edge of
the output, or stretch them across the entire output. This library only makes
sense on Wayland compositors that support Layer Shell, and will not work on
X11. It supports all Layer Shell features including popups and popovers
(GTK popups Just Work(tm)).

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for %{name}.

%prep
%autosetup -n %{name}-%{version}

%build
# supply the vendored GIR include closure to g-ir-scanner via GI_GIR_PATH.
mkdir -p gir-pango
tar xzf %{SOURCE10} -C gir-pango/
export GI_GIR_PATH=$PWD/gir-pango
%meson \
    -Dvapi=false \
    %{nil}
%meson_build

%install
%meson_install

%files
%license LICENSE_LGPL.txt LICENSE_MIT.txt
%doc README.md CHANGELOG.md
%{_libdir}/girepository-1.0/GtkLayerShell-0.1.typelib
%{_libdir}/lib%{name}.so.0*

%files devel
%{_datadir}/gir-1.0/GtkLayerShell-0.1.gir
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/*.pc

%changelog
* Mon Aug 10 2026 like-me - 0.8.2-1
- Initial package for EPEL 10 (not available there yet)
- Drop vala/vapi (no vala in EL10), keep introspection typelib
