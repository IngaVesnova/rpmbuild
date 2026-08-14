
Name:           mangowm
Version:        0.16.0
Release:        2%{?dist}
Summary:        A scrollable-tiling Wayland compositor (Nexus Optimized)

License:        MIT
URL:            https://github.com/mangowm/mango
Source0:        https://github.com/mangowm/mango/archive/refs/tags/%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires: git
BuildRequires:  systemd-rpm-macros

# Wayland
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-server) >= 1.23.1
BuildRequires:  wayland-protocols-devel

# Graphics/Display
BuildRequires:  pkgconfig(libdrm) >= 2.4.129
BuildRequires:  pkgconfig(pixman-1) >= 0.46.0
BuildRequires:  pkgconfig(libinput) >= 1.27.1
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(pangocairo)
BuildRequires:  pkgconfig(libpcre2-8)

# wlroots + scenefx (from X11:Wayland / home projects)
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(scenefx-0.5) >= 0.5.0

# XWayland support
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)

# Utilities
BuildRequires:  pkgconfig(libcjson)

# Runtime
Requires:       xorg-x11-server-Xwayland
Requires:       mesa-dri-drivers
Requires:       mesa-libEGL

%description
Mango is a Wayland compositor built on wlroots and scenefx with
scrollable-tiling and eye-candy effects.

%prep
%autosetup -n mango-%{version}

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_bindir}/mango
%{_bindir}/mmsg
%{_mandir}/man1/mmsg.1*

# Session
%dir %{_datadir}/wayland-sessions
%{_datadir}/wayland-sessions/mango.desktop

# Portal
%dir %{_datadir}/xdg-desktop-portal
%{_datadir}/xdg-desktop-portal/mango-portals.conf

# Config (sysconfdir)
%dir %{_sysconfdir}/mango
%config(noreplace) %{_sysconfdir}/mango/config.conf

%changelog

