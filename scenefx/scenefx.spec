%global debug_package %{nil}

Name:           scenefx
Version:        0.5
Release:        1%{?dist}
Summary:        Scene-graph effect library for wlroots compositors

License:        MIT
URL:            https://github.com/wlrfx/scenefx
Source0:        https://github.com/wlrfx/scenefx/archive/refs/tags/%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(wlroots-0.20)
BuildRequires:  pkgconfig(wayland-server) >= 1.24.0
BuildRequires: pkgconfig(libdrm) >= 2.4.129
BuildRequires: pkgconfig(xkbcommon) >= 1.8.0
BuildRequires:  pkgconfig(pixman-1) >= 0.43.0

%description
scenefx is a drop-in replacement for the wlroots scene-graph API
that adds eye-candy effects.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Development files for %{name}.

%prep
%autosetup

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_libdir}/libscenefx-%{version}.so*

%files devel
%{_includedir}/scenefx-%{version}/
%{_libdir}/libscenefx-%{version}.so
%{_libdir}/pkgconfig/scenefx-%{version}.pc

%changelog
* Tue Aug 04 2026 Custom Maintainer - %{version}-1
- Initial build for Rocky Linux
