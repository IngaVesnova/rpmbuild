%global debug_package %{nil}

Name:           libdrm
Version:        2.4.129
Release:        1%{?dist}
Summary:        Direct Rendering Manager runtime library

License:        MIT
URL:            https://dri.freedesktop.org/libdrm/
Source0:        https://dri.freedesktop.org/libdrm/%{name}-%{version}.tar.xz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  pkgconfig(pciaccess) >= 0.10

%description
Direct Rendering Manager runtime library.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(pciaccess)

%description    devel
Development files for %{name}.

%prep
%autosetup

%build
%meson \
  -Dudev=true \
  -Dvalgrind=disabled \
  -Dcairo-tests=disabled \
  -Dman-pages=disabled \
  -Dintel=enabled \
  -Dradeon=enabled \
  -Damdgpu=enabled \
  -Dnouveau=enabled \
  -Dvmwgfx=enabled \
  -Dfreedreno=enabled \
  -Dvc4=enabled \
  -Detnaviv=enabled

%meson_build

%install
%meson_install

%files
%{_libdir}/libdrm*.so.*
%{_datadir}/libdrm/

%files devel
%{_includedir}/libdrm/
%{_includedir}/freedreno/
%{_includedir}/libsync.h
%{_includedir}/xf86*.h
%{_libdir}/libdrm*.so
%{_libdir}/pkgconfig/libdrm*.pc

%changelog
* Tue Aug 04 2026 Inga Vesnova <inga.vesnova@gmail.com> - 2.4.129-1
