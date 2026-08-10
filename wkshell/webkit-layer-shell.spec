#
# spec file for package webkit-layer-shell (Python port of wkshell/example.c)
#
# Copyright (c) 2026 like-me
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license is an "Open Source License", which is an Open Source License as
# defined by the Open Source Initiative).

Name:           webkit-layer-shell
Version:        1.0
Release:        1%{?dist}
Summary:        WebKit web view on a Wayland layer-shell surface (Python)

License:        MIT
Url:            https://build.opensuse.org/package/show/home:like-me/wkshell
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel

Requires:       python3-gobject
Requires:       gtk3
Requires:       webkit2gtk4.1
Requires:       gtk-layer-shell

%description
webkit-layer-shell displays a WebKit web view on a Wayland layer-shell
surface (background, bottom, top or overlay layer of a chosen monitor).
It is useful for desktop panels, widgets and similar shell components
running on wlroots-based compositors.

This is a Python 3 reimplementation of the C utility of the same name
(see wkshell/example.c), built against WebKitGTK 4.1 (webkit2gtk4.1),
GTK 3 and gtk-layer-shell via PyGObject.

%prep
%autosetup -n %{name}-%{version}

%build
# Pure Python script: nothing to compile.

%check
python3 -m py_compile %{name}.py

%install
install -D -p -m 0755 %{name}.py %{buildroot}%{_bindir}/%{name}

%files
%{_bindir}/%{name}
%license LICENSE

%changelog
* Mon Aug 10 2026 like-me - 1.0-1
- Initial package: Python 3 port of webkit-layer-shell (wkshell/example.c)
