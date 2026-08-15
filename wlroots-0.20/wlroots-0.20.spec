%global debug_package %{nil}

Name:           wlroots0.20
Version:        0.20.2
Release:        1%{?dist}
Summary:        Modular Wayland compositor library (version 0.20)

License:        MIT
URL:            https://gitlab.freedesktop.org/wlroots/wlroots
Source0:        https://gitlab.freedesktop.org/wlroots/wlroots/-/archive/%{version}/wlroots-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson >= 0.59.0
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  hwdata-devel
BuildRequires:  systemd-devel
BuildRequires:  pkgconfig(libseat)
BuildRequires:  wayland-devel
BuildRequires:  pkgconfig(wayland-protocols) >= 1.38
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(libdrm) >= 2.4.129
BuildRequires:  pkgconfig(gbm) >= 17.1.0
BuildRequires:  pkgconfig(libinput) >= 1.14.0
BuildRequires:  pkgconfig(xkbcommon) >= 1.8.0
BuildRequires:  pkgconfig(pixman-1) >= 0.46.0
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires: pkgconfig(libliftoff)
BuildRequires:  pkgconfig(xwayland)
BuildRequires:  pkgconfig(x11-xcb)
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-composite)
BuildRequires:  pkgconfig(xcb-dri3)
BuildRequires:  pkgconfig(xcb-errors)
BuildRequires:  pkgconfig(xcb-ewmh)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(xcb-present)
BuildRequires:  pkgconfig(xcb-render)
BuildRequires:  pkgconfig(xcb-renderutil)
BuildRequires:  pkgconfig(xcb-res)
BuildRequires:  pkgconfig(xcb-shm)
BuildRequires:  pkgconfig(xcb-xfixes) >= 1.15
BuildRequires:  pkgconfig(xcb-xinput)
BuildRequires:  pkgconfig(lcms2)

%description
Modular Wayland compositor library.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Development files for %{name}.

%prep
%autosetup -n wlroots-%{version}

%build
%meson \
  -Dxwayland=enabled \
  -Dexamples=false \
  -Drenderers=gles2

%meson_build

%install
%meson_install

%files
%license LICENSE
%{_libdir}/libwlroots-0.20.so*

%files devel
%{_includedir}/wlroots-0.20/
%{_libdir}/libwlroots-0.20.so
%{_libdir}/pkgconfig/wlroots-0.20.pc

%changelog
* Tue Aug 04 2026 Custom Maintainer - %{version}-1
- Initial build of wlroots 0.20
