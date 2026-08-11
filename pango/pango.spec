
Name:    pango
Version: 1.57.1
Release: 2%{?dist}
Summary: System for layout and rendering of internationalized text

License: LGPL-2.0-or-later
URL:     https://pango.gnome.org/
Source0: https://download.gnome.org/sources/%{name}/1.57/%{name}-%{version}.tar.xz

# lower the upstream glib requirement (2.82 -> 2.80) to match EPEL 10
Patch0:  %{name}-glib-2.80.patch
# replace g_sort_array() (glib 2.82+ only) with g_qsort_with_data() in the
# non-installed gen-script-for-lang tool
Patch1:  %{name}-glib-2.82-api.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  meson >= 1.2.0
BuildRequires:  ninja-build
BuildRequires:  pkgconfig

BuildRequires:  glib2-devel
BuildRequires:  gobject-introspection-devel

BuildRequires: pkgconfig(fribidi) >= 1.0.6
BuildRequires: pkgconfig(libthai) >= 0.1.9
BuildRequires: pkgconfig(harfbuzz) >= 8.4.0
BuildRequires: pkgconfig(fontconfig) >= 2.17.0
BuildRequires: pkgconfig(xft) >= 2.0.0
BuildRequires: pkgconfig(cairo) >= 1.18.0
BuildRequires: pkgconfig(cairo-ft) >= 1.18.0
BuildRequires: pkgconfig(freetype2) >= 2.1.5

Provides: pango-tests = %{version}-%{release}
Obsoletes: pango-tests < 1.54.0-1

%description
Pango is a library for laying out and rendering of text, with an emphasis
on internationalization. Pango can be used anywhere that text layout is needed,
though most of the work on Pango so far has been done in the context of the
GTK+ widget toolkit. Pango forms the core of text and font handling for GTK+.

Pango is designed to be modular; the core Pango layout engine can be used
with different font backends.

The integration of Pango with Cairo provides a complete solution with high
quality text handling and graphics rendering.

%package devel
Summary: Development files for pango
Requires: pango%{?_isa} = %{version}-%{release}
Requires: glib2-devel%{?_isa}
Requires: freetype-devel%{?_isa}
Requires: fontconfig-devel%{?_isa}
Requires: cairo-devel%{?_isa}

%description devel
The pango-devel package includes the header files for the pango package.

%prep
%autosetup -n pango-%{version} -p1

%build
export CFLAGS='-std=c11 %optflags'
%meson \
  -Dbuild-testsuite=false \
  -Dbuild-examples=false \
  -Ddocumentation=false \
  -Dintrospection=enabled

%meson_build


%install
%meson_install

# Sanity check: the Xft backend must have been built (requires libXft-devel
# and the FreeType/FontConfig-enabled cairo).
PANGOXFT_SO=$RPM_BUILD_ROOT%{_libdir}/libpangoxft-1.0.so
if ! test -e $PANGOXFT_SO; then
        echo "$PANGOXFT_SO not found; did not build with Xft support?"
        ls $RPM_BUILD_ROOT%{_libdir}
        exit 1
fi

%files
%license COPYING
%doc NEWS README.md
%{_libdir}/libpango*-*.so.*
%{_bindir}/pango-list
%{_bindir}/pango-segmentation
%{_bindir}/pango-view

%files devel
%{_libdir}/libpango*.so
%{_includedir}/*
%{_libdir}/pkgconfig/*


%changelog
* Fri Aug 07 2026 like-me <like-me@opensuse.org> - 1.57.1-1
- Initial packaging of pango 1.57.1 for EPEL 10
- glib 2.82 requirement lowered to 2.80 (RHEL 10 ships glib2 2.80.4; the
  upstream bump was a version-number-only change, only g_sort_array() in a
  non-installed tool needed replacing)
