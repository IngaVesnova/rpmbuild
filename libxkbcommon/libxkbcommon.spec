%global debug_package %{nil}

Name:           libxkbcommon
Version:        1.8.0
Release:        1%{?dist}
Summary:        Keymap handling library for xkb

License:        MIT
URL:            https://xkbcommon.org
Source0:        https://github.com/xkbcommon/libxkbcommon/archive/refs/tags/xkbcommon-%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  bison
BuildRequires: pkgconfig(xkeyboard-config)
BuildRequires:  pkgconfig(xcb) >= 1.10
BuildRequires:  pkgconfig(xcb-xkb) >= 1.10
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(wayland-client) >= 1.2.0
BuildRequires:  pkgconfig(wayland-protocols) >= 1.12
BuildRequires: pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(icu-uc)

%description
xkbcommon is a keymap compiler and support library which processes
keyboard descriptions.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Development files for %{name}.

%package        x11
Summary:        X11 support for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    x11
X11 support library for %{name}.

%package        x11-devel
Summary:        Development files for X11 support of %{name}
Requires:       %{name}-x11%{?_isa} = %{version}-%{release}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description    x11-devel
Development files for X11 support of %{name}.

%package        registry
Summary:        XKB registry library
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    registry
XKB registry library for querying available rules, models, layouts, variants and options.

%package        registry-devel
Summary:        Development files for XKB registry library
Requires:       %{name}-registry%{?_isa} = %{version}-%{release}
Requires:       %{name}-devel%{?_isa} = %{version}-%{release}

%description    registry-devel
Development files for XKB registry library.

%package        tools
Summary:        CLI tools for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    tools
Tools to inspect, verify and test keymaps (xkbcli).

%prep
%autosetup -n libxkbcommon-xkbcommon-%{version}

%build
%meson \
  -Denable-docs=false \
  -Denable-bash-completion=false

%meson_build

%install
%meson_install

%files
%license LICENSE
%{_libdir}/libxkbcommon.so.*
%{_libexecdir}/xkbcommon/

%files devel
%{_includedir}/xkbcommon/xkbcommon*.h
%exclude %{_includedir}/xkbcommon/xkbcommon-x11.h
%exclude %{_includedir}/xkbcommon/xkbregistry.h
%{_libdir}/libxkbcommon.so
%{_libdir}/pkgconfig/xkbcommon.pc

%files x11
%{_libdir}/libxkbcommon-x11.so.*

%files x11-devel
%{_includedir}/xkbcommon/xkbcommon-x11.h
%{_libdir}/libxkbcommon-x11.so
%{_libdir}/pkgconfig/xkbcommon-x11.pc

%files registry
%{_libdir}/libxkbregistry.so.*

%files registry-devel
%{_includedir}/xkbcommon/xkbregistry.h
%{_libdir}/libxkbregistry.so
%{_libdir}/pkgconfig/xkbregistry.pc

%files tools
%{_bindir}/xkbcli
%{_mandir}/man1/xkbcli*.1*

%changelog
* Tue Aug 04 2026 Custom Maintainer - 1.8.0-1
- Update libxkbcommon for MangoWM stack
