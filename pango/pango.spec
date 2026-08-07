# pango 1.57.1 is a development snapshot requiring glib >= 2.82, but EPEL 10
# (RHEL 10) ships glib2 2.80.4. The upstream glib 2.82 bump was a pure
# version-number change (commit 7020a41a, no code changes); the only 2.82-only
# API used anywhere in the tree is g_sort_array() in tools/gen-script-for-lang.c
# (a non-installed dev tool), so both are patched to build against glib 2.80.
%global glib2_version 2.80
%global fribidi_version 1.0.6
%global libthai_version 0.1.9
%global harfbuzz_version 8.4.0
# RHEL 10 ships fontconfig 2.15.0, but pango 1.57.1 requires >= 2.17.0;
# this project builds fontconfig 2.18.1 for the same epel-10 repository,
# so the dependency resolves against that build.
%global fontconfig_version 2.17.0
%global libXft_version 2.0.0
%global cairo_version 1.18
%global freetype_version 2.1.5

Name:    pango
Version: 1.57.1
Release: 1%{?dist}
Summary: System for layout and rendering of internationalized text

License: LGPL-2.0-or-later
URL:     https://pango.gnome.org/
Source0: https://download.gnome.org/sources/%{name}/1.57/%{name}-%{version}.tar.xz

# lower the upstream glib requirement (2.82 -> 2.80) to match EPEL 10
Patch0:  %{name}-glib-2.80.patch
# replace g_sort_array() (glib 2.82+ only) with g_qsort_with_data() in the
# non-installed gen-script-for-lang tool
Patch1:  %{name}-glib-2.82-api.patch

BuildRequires: pkgconfig(cairo) >= %{cairo_version}
BuildRequires: pkgconfig(cairo-ft) >= %{cairo_version}
BuildRequires: pkgconfig(freetype2) >= %{freetype_version}
BuildRequires: pkgconfig(glib-2.0) >= %{glib2_version}
BuildRequires: pkgconfig(fontconfig) >= %{fontconfig_version}
BuildRequires: pkgconfig(harfbuzz) >= %{harfbuzz_version}
BuildRequires: pkgconfig(libthai) >= %{libthai_version}
BuildRequires: pkgconfig(xft) >= %{libXft_version}
BuildRequires: pkgconfig(fribidi) >= %{fribidi_version}
BuildRequires: meson
BuildRequires: ninja-build
BuildRequires: gcc gcc-c++

Requires: glib2%{?_isa} >= %{glib2_version}
Requires: freetype%{?_isa} >= %{freetype_version}
Requires: fontconfig%{?_isa} >= %{fontconfig_version}
Requires: cairo%{?_isa} >= %{cairo_version}
Requires: harfbuzz%{?_isa} >= %{harfbuzz_version}
Requires: libthai%{?_isa} >= %{libthai_version}
Requires: libXft%{?_isa} >= %{libXft_version}
Requires: fribidi%{?_isa} >= %{fribidi_version}

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
Requires: glib2-devel%{?_isa} >= %{glib2_version}
Requires: freetype-devel%{?_isa} >= %{freetype_version}
Requires: fontconfig-devel%{?_isa} >= %{fontconfig_version}
Requires: cairo-devel%{?_isa} >= %{cairo_version}

%description devel
The pango-devel package includes the header files for the pango package.

%prep
%autosetup -n pango-%{version} -p1
# el10 gobject-introspection (1.79.1) cannot satisfy pango's >= 1.83.2
# requirement and sysprof is not shipped on el10; both deps are optional
# (introspection stays auto -> effectively disabled), but meson would try to
# satisfy them via the bundled subproject .wrap files, which need network
# access. Remove all wraps so missing optional deps resolve as not-found.
find subprojects -name '*.wrap' -delete



%build
export CFLAGS='-std=c11 %optflags'
# el10's %%meson passes --auto-features=enabled, which would turn the 'auto'
# introspection feature into 'enabled' and hard-fail on GI < 1.83.2; disable it
# explicitly (documentation also needs introspection, hence false).
%meson \
  -Dbuild-testsuite=true \
  -Dbuild-examples=true \
  -Ddocumentation=false \
  -Dintrospection=disabled

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
- built against the epel-10 repo (AlmaLinux:10 baseos/appstream/CRB + Fedora:EPEL:10 standard)
- based on the Fedora rawhide spec, adapted to el10 and 1.57.1

- glib 2.82 requirement lowered to 2.80 (RHEL 10 ships glib2 2.80.4; the
  upstream bump was a version-number-only change, only g_sort_array() in a
  non-installed tool needed replacing)
- gobject-introspection on el10 is 1.79.1 < required 1.83.2, so introspection
  is auto-disabled (no GIR/typelib files); documentation is off as a result
  (it requires introspection)
- fontconfig >= 2.17.0 requirement is satisfied by the project's own
  fontconfig 2.18.1 build for the same repository (RHEL 10 has 2.15.0)
