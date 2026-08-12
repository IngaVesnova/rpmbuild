Name:           gobject-introspection
Version:        1.84.0
Release:        1%{?dist}
Summary:        Introspection system for GObject-based libraries

License:        GPL-2.0-or-later AND LGPL-2.0-or-later AND LGPL-2.1-or-later AND BSD-2-Clause
URL:            https://wiki.gnome.org/Projects/GObjectIntrospection
Source:         https://download.gnome.org/sources/gobject-introspection/1.84/gobject-introspection-%{version}.tar.xz

# Workaround for Python 3.12 compatibility
# https://bugzilla.redhat.com/show_bug.cgi?id=2208966
Patch:          gobject-introspection-workaround.patch

BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  gcc
BuildRequires:  gettext
BuildRequires:  meson
BuildRequires:  python3-devel
BuildRequires:  python3-mako
BuildRequires:  python3-markdown
BuildRequires:  python3-setuptools
BuildRequires:  pkgconfig(cairo-gobject)
BuildRequires:  pkgconfig(gio-2.0) >= 2.80.0
BuildRequires:  pkgconfig(libffi)

Requires:       glib2%{?_isa} >= 2.80.0

%description
GObject Introspection can scan C header and source files in order to
generate introspection "typelib" files.  It also provides an API to examine
typelib files, useful for creating language bindings among other
things.

%package devel
Summary:        Libraries and headers for gobject-introspection
Requires:       %{name}%{?_isa} = %{version}-%{release}
# Not always, but whatever, it's a tiny dep to pull in
Requires:       libtool
# For g-ir-doctool
Requires:       python3-mako
Requires:       python3-markdown
# This package only works with the Python version it was built with
# https://bugzilla.redhat.com/show_bug.cgi?id=1691064
Requires:       (python(abi) = %{python3_version} if python3)
# The package uses distutils which is no longer part of Python 3.12+ standard library
# https://bugzilla.redhat.com/show_bug.cgi?id=2135406
Requires:       (python3-setuptools if python3 >= 3.12)

%description devel
Libraries and headers for gobject-introspection

%prep
%autosetup -p1
mv giscanner/ast.py giscanner/gio_ast.py

%build
%meson -Ddoctool=enabled -Dgtk_doc=false -Dpython=%{__python3}
%meson_build

%install
%meson_install

%files
%doc NEWS README.rst
%license COPYING COPYING.GPL COPYING.LGPL
%{_libdir}/libgirepository-1.0.so.1*
%dir %{_libdir}/girepository-1.0
%{_libdir}/girepository-1.0/*.typelib

%files devel
%{_libdir}/libgirepository-1.0.so
%{_libdir}/gobject-introspection/
%{_libdir}/pkgconfig/gobject-introspection-1.0.pc
%{_libdir}/pkgconfig/gobject-introspection-no-export-1.0.pc
%{_includedir}/gobject-introspection-1.0/
%{_bindir}/g-ir-*
%dir %{_datadir}/gir-1.0
%{_datadir}/gir-1.0/*.gir
%{_datadir}/gir-1.0/gir-1.2.rnc
%{_datadir}/gobject-introspection-1.0/
%{_datadir}/aclocal/introspection.m4
%{_mandir}/man1/g-ir-compiler.1*
%{_mandir}/man1/g-ir-doc-tool.1*
%{_mandir}/man1/g-ir-generate.1*
%{_mandir}/man1/g-ir-scanner.1*

%changelog
* Wed Aug 13 2026 Inga Vesnova <inga.vesnova@gmail.com> - 1.84.0-1
- 1.84.0 for EPEL 10 (provides g-ir-scanner >= 1.83.2 for pango)
