# ifdef'd in source code but runtime dep will be made for FT_Done_MM_Var symbol in freetype-2.9.1
# so update the build deps as well to keep deps consistency between runtime and build time.
%global freetype_version 2.9.1

Summary:        Font configuration and customization library
Name:           fontconfig
Version:        2.18.1
Release:        1%{?dist}
# src/ftglue.[ch] is in Public Domain
# src/fccache.c contains Public Domain code
## https://gitlab.com/fedora/legal/fedora-license-data/-/issues/177
# fc-case/CaseFolding.txt is in the UCD
# otherwise HPND
License:        HPND AND LicenseRef-Fedora-Public-Domain AND Unicode-DFS-2016
URL:            https://www.freedesktop.org/wiki/Software/fontconfig/
Source0:        https://gitlab.freedesktop.org/fontconfig/fontconfig/-/archive/%{version}/fontconfig-%{version}.tar.bz2
Source1:        25-no-bitmap-fedora.conf
Source2:        fc-cache

# https://bugzilla.redhat.com/show_bug.cgi?id=140335
Patch0:         %{name}-sleep-less.patch
# NOTE: the original Patch4 hunk was generated against
# 2.13.92, whose context lines used TAB indentation; 2.18.1 src/fcformat.c
# uses spaces, so the hunk could not apply under rpm's fuzz=0 policy. The
# shipped patch has been regenerated against the 2.18.1 source whitespace
# (patch --fuzz=0 --dry-run verified) and applies cleanly in the prep step.
Patch4:         %{name}-drop-lang-from-pkgkit-format.patch

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  fontpackages-devel
BuildRequires:  pkgconfig(freetype2) >= %{freetype_version}
BuildRequires:  pkgconfig(json-c)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  gperf
BuildRequires:  gettext
BuildRequires:  docbook-utils
BuildRequires:  python3

# Register DTD system-wide to make validation work by default
# (used by fonts-rpm-macros)
Requires(pre):    xml-common
Requires(postun): xml-common
Requires(post):   grep coreutils

%description
Fontconfig is designed to locate fonts within the
system and select them according to requirements specified by 
applications.

%package	devel
Summary:	Font configuration and customization library
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	freetype-devel >= %{freetype_version}
Requires:	pkgconfig
Requires:	gettext

%description	devel
The fontconfig-devel package includes the header files,
and developer docs for the fontconfig package.

Install fontconfig-devel if you want to develop programs which 
will use fontconfig.

%package	devel-doc
Summary:	Development Documentation files for fontconfig library
BuildArch:	noarch
Requires:	%{name}-devel = %{version}-%{release}

%description	devel-doc
The fontconfig-devel-doc package contains the documentation files
which is useful for developing applications that uses fontconfig.


%prep
%autosetup -p1

%build
%meson \
  -Ddoc=enabled \
  -Ddoc-pdf=disabled \
  -Dtests=enabled \
  -Dcache-build=disabled \
  -Dxml-backend=libxml2 \
  -Dcache-dir='/usr/lib/fontconfig/cache' \
  -Dadditional-fonts-dirs=/usr/share/X11/fonts/Type1,/usr/share/X11/fonts/TTF,/usr/local/share/fonts \
  -Ddefault-sub-pixel-rendering=noinstall

%meson_build

%install
%meson_install

install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d
ln -s %{_fontconfig_templatedir}/25-unhint-nonlatin.conf $RPM_BUILD_ROOT%{_fontconfig_confdir}/

# move installed doc files back to build directory to package them
# in the right place
mv $RPM_BUILD_ROOT%{_docdir}/fontconfig/* .
rmdir $RPM_BUILD_ROOT%{_docdir}/fontconfig/

# adjust the timestamp to avoid conflicts for multilib
touch -r doc/fontconfig-user.sgml fontconfig-user.txt
touch -r doc/fontconfig-user.sgml fontconfig-user.html

# rename fc-cache binary
mv $RPM_BUILD_ROOT%{_bindir}/fc-cache $RPM_BUILD_ROOT%{_bindir}/fc-cache-%{__isa_bits}

# create link to man page
echo ".so man1/fc-cache.1" > $RPM_BUILD_ROOT%{_mandir}/man1/fc-cache-%{__isa_bits}.1

install -p -m 0755 %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/fc-cache

%find_lang %{name}
%find_lang %{name}-conf
cat %{name}-conf.lang >> %{name}.lang

%check
%meson_test

%post
umask 0022

mkdir -p /usr/lib/fontconfig/cache

[[ -d %{_localstatedir}/cache/fontconfig ]] && rm -rf %{_localstatedir}/cache/fontconfig/* 2> /dev/null || :

# Force regeneration of all fontconfig cache files
# The check for existance is needed on dual-arch installs (the second
#  copy of fontconfig might install the binary instead of the first)
# The HOME setting is to avoid problems if HOME hasn't been reset
if [ -x /usr/bin/fc-cache ] && /usr/bin/fc-cache --version 2>&1 | grep -q %{version} ; then
  HOME=/root /usr/bin/fc-cache -f
fi

%transfiletriggerin -- /usr/share/fonts /usr/share/X11/fonts/Type1 /usr/share/X11/fonts/TTF /usr/local/share/fonts
HOME=/root /usr/bin/fc-cache -s

%transfiletriggerpostun -- /usr/share/fonts /usr/share/X11/fonts/Type1 /usr/share/X11/fonts/TTF /usr/local/share/fonts
HOME=/root /usr/bin/fc-cache -s

%posttrans
if [ -e %{_sysconfdir}/xml/catalog ]; then
  %{_bindir}/xmlcatalog --noout --add system \
                        "urn:fontconfig:fonts.dtd" \
                        "file://%{_datadir}/xml/fontconfig/fonts.dtd" \
                        %{_sysconfdir}/xml/catalog
fi

%postun
if [ $1 == 0 ] && [ -e %{_sysconfdir}/xml/catalog ]; then
  %{_bindir}/xmlcatalog --noout --del "urn:fontconfig:fonts.dtd" %{_sysconfdir}/xml/catalog
fi

%files -f %{name}.lang
%doc README.md AUTHORS
%doc fontconfig-user.txt fontconfig-user.html
%doc %{_fontconfig_confdir}/README
%license COPYING
%{_libdir}/libfontconfig.so.*
%{_bindir}/fc-cache*
%{_bindir}/fc-cat
%{_bindir}/fc-conflist
%{_bindir}/fc-genconf
%{_bindir}/fc-list
%{_bindir}/fc-match
%{_bindir}/fc-pattern
%{_bindir}/fc-query
%{_bindir}/fc-scan
%{_bindir}/fc-validate
%{_fontconfig_templatedir}/*.conf
%{_datadir}/xml/fontconfig
# fonts.conf is not supposed to be modified.
# If you want to do so, you should use local.conf instead.
%config %{_fontconfig_masterdir}/fonts.conf
%config(noreplace) %{_fontconfig_confdir}/*.conf
%dir /usr/lib/fontconfig/cache
%{_mandir}/man1/*
%{_mandir}/man5/*

%files devel
%{_libdir}/libfontconfig.so
%{_libdir}/pkgconfig/*
%{_includedir}/fontconfig
%{_mandir}/man3/*
%{_datadir}/gettext/its/fontconfig.its
%{_datadir}/gettext/its/fontconfig.loc

%files devel-doc
%doc fontconfig-devel.txt fontconfig-devel.html

%changelog
* Fri Aug  7 2026 Inga Vesnova <inga.vesnova@gmail.com> - 2.18.1-1
- New upstream release 2.18.1
- Migrate the build to Meson (%meson/%meson_build/%meson_install/%meson_test),
  dropping the autotools machinery (autoreconf, %configure, HASDOCBOOK)
