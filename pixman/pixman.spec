%global debug_package %{nil}

Name:           pixman
Version:        0.46.4
Release:        1%{?dist}
Summary:        Pixel manipulation library

License:        MIT
URL:            http://www.pixman.org
Source0:        https://cairographics.org/releases/%{name}-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig

%description
Pixman is a low-level software library for pixel manipulation,
providing features such as image compositing and trapezoid rasterization.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Development files for %{name}.

%prep
%autosetup

%build
%meson \
  -Dloongson-mmi=disabled \
  -Dvmx=disabled \
  -Darm-simd=disabled \
  -Dneon=disabled \
  -Da64-neon=disabled \
  -Dmips-dspr2=disabled \
  -Drvv=disabled \
  -Dgtk=disabled \
  -Dlibpng=disabled \
  -Dtests=disabled \
  -Ddemos=disabled

%meson_build

%install
%meson_install

%files
%{_libdir}/libpixman-1.so.*

%files devel
%{_includedir}/pixman-1/
%{_libdir}/libpixman-1.so
%{_libdir}/pkgconfig/pixman-1.pc

%changelog
* Tue Aug 04 2026 Custom Maintainer - %{version}-1
- Update pixman for wlroots 0.20
