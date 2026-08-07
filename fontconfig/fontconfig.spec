# ifdef'd in source code but runtime dep will be made for FT_Done_MM_Var symbol in freetype-2.9.1
# so update the build deps as well to keep deps consistency between runtime and build time.
%global freetype_version 2.9.1

Summary:	Font configuration and customization library
Name:		fontconfig
Version:	2.18.1
Release:	1%{?dist}
# src/ftglue.[ch] is in Public Domain
# src/fccache.c contains Public Domain code
## https://gitlab.com/fedora/legal/fedora-license-data/-/issues/177
# fc-case/CaseFolding.txt is in the UCD
# otherwise MIT
License:	HPND AND LicenseRef-Fedora-Public-Domain AND Unicode-DFS-2016
Source0:	https://gitlab.freedesktop.org/api/v4/projects/890/packages/generic/fontconfig/%{version}/fontconfig-%{version}.tar.xz
URL:		http://fontconfig.org
Source1:	25-no-bitmap-fedora.conf
Source2:	fc-cache

# https://bugzilla.redhat.com/show_bug.cgi?id=140335
Patch0:		%{name}-sleep-less.patch
Patch4:		%{name}-drop-lang-from-pkgkit-format.patch
Patch6:		%{name}-lower-nonlatin-conf.patch

BuildRequires:	libxml2-devel
BuildRequires:	freetype-devel >= %{freetype_version}
# fontpackages was retired in el10: fonts-rpm-macros (CRB) provides fontpackages-devel
# (fonts-srpm-macros from AppStream defines %{_fontconfig_templatedir} etc.)
BuildRequires:	fontpackages-devel
BuildRequires:	gettext
BuildRequires:	gperf
BuildRequires:	gcc make

Requires:	fonts-filesystem freetype
# Register DTD system-wide to make validation work by default
# (used by fonts-rpm-macros)
Requires(pre):    xml-common
Requires(postun): xml-common
PreReq:		freetype >= 2.9.1-6
Requires(post):	grep coreutils
Requires:	font(:lang=en)
Suggests:	font(notosans)

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
# To reduce a maintenance cost of fontconfig-lower-nonlatin-conf.patch
mv conf.d/65-nonlatin.conf conf.d/69-nonlatin.conf
for f in test/*.json; do
  sed -i -e 's/65-nonlatin.conf/69-nonlatin.conf/g' $f
done
# conf.d/Makefile.in, po-conf/POTFILES.in and the po files are prebuilt and
# not regenerated (see below), so the 65-nonlatin.conf -> 69-nonlatin.conf
# rename must be applied to them as well
sed -i 's/65-nonlatin.conf/69-nonlatin.conf/g' conf.d/Makefile.in po-conf/POTFILES.in po-conf/*.po
# 2.18.1 upstream bug: fcconffile.c is in src/meson.build but missing from
# the autotools source list, so FcConfigFileGenerate & co are not built into
# the library and fc-genconf fails to link. Add it to both the .am (for
# consistency) and the prebuilt .in (which config.status actually uses).
sed -i 's/^\([[:space:]]*\)fcformat\.c \\$/\1fcformat.c \\\n\1fcconffile.c \\/' src/Makefile.am src/Makefile.in
# the prebuilt OBJECTS list (not SOURCES) drives compilation, add it there too
sed -i 's/fccharset\.lo fccompat\.lo fcdbg\.lo/fccharset.lo fccompat.lo fcconffile.lo fcdbg.lo/' src/Makefile.in
grep -q 'fcconffile\.c' src/Makefile.in && grep -q 'fcconffile\.lo' src/Makefile.in || { echo "fcconffile injection failed"; exit 1; }


# The release tarball was generated with automake 1.18, which is not
# available in el10. The shipped generated files (configure, Makefile.in,
# aclocal.m4, config.h.in) must be kept as-is, so re-stamp them newer than
# their .am/.ac sources; otherwise `make` would try to regenerate them
# (Patch6 above modifies conf.d/Makefile.am) and fail on missing automake.
find . \( -name 'Makefile.in' -o -name configure -o -name aclocal.m4 \
          -o -name 'config.h.in' \) -exec touch {} +

# autotools build: RHEL 10 (and EPEL 10) ship meson 1.4.x, while
# fontconfig >= 2.18 requires meson >= 1.11, so we build via configure/make
# (the release tarball ships prebuilt docs/man pages, so no docbook is needed;
#  --disable-docbook makes sure docbook tools are not required)
%build
%configure \
        --disable-static \
        --disable-docbook \
        --disable-cache-build \
        --enable-libxml2 \
        --with-cache-dir=/usr/lib/fontconfig/cache \
        --with-add-fonts=/usr/share/X11/fonts/Type1,/usr/share/X11/fonts/TTF,/usr/local/share/fonts
make %{?_smp_mflags}
# fc-genconf is built by the meson build but is missing from the autotools
# SUBDIRS list in the 2.18.1 release tarball (upstream bug), build it manually
make %{?_smp_mflags} -C fc-genconf

%install
%make_install

# the autotools install puts the docs under %{_docdir}/%{name}, but the
# Fedora-style layout ships them in the -devel-doc subpackage docdir instead
rm -f $RPM_BUILD_ROOT%{_docdir}/%{name}/fontconfig-devel.html \
      $RPM_BUILD_ROOT%{_docdir}/%{name}/fontconfig-devel.pdf \
      $RPM_BUILD_ROOT%{_docdir}/%{name}/fontconfig-devel.txt

# fc-genconf: see the comment in %%build (upstream SUBDIRS omission)
install -p -m 0755 fc-genconf/fc-genconf $RPM_BUILD_ROOT%{_bindir}/

install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d
ln -s %{_fontconfig_templatedir}/25-unhint-nonlatin.conf $RPM_BUILD_ROOT%{_fontconfig_confdir}/

# Use implied value to allow the use of conditional conf
rm $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d/10-sub-pixel-*.conf

# Do not enable bitmap-related conf
rm $RPM_BUILD_ROOT%{_sysconfdir}/fonts/conf.d/70-*bitmaps*.conf

# Install docs manually
install -d $RPM_BUILD_ROOT%{_mandir}/man1
install -d $RPM_BUILD_ROOT%{_mandir}/man3
install -d $RPM_BUILD_ROOT%{_mandir}/man5
for f in doc/*.1; do
  install -p -m 0644 $f $RPM_BUILD_ROOT%{_mandir}/man1
done
for f in doc/*.3; do
  install -p -m 0644 $f $RPM_BUILD_ROOT%{_mandir}/man3
done
for f in doc/*.5; do
  install -p -m 0644 $f $RPM_BUILD_ROOT%{_mandir}/man5
done
for f in doc/*.txt doc/*.pdf doc/*.html; do
  install -p -m 0644 $f .
done

# adjust the timestamp to avoid conflicts for multilib
touch -r doc/fontconfig-user.sgml fontconfig-user.txt
touch -r doc/fontconfig-user.sgml fontconfig-user.html
touch -r doc/fontconfig-user.sgml fontconfig-user.pdf
touch -r doc/fontconfig-devel.sgml fontconfig-devel.txt
touch -r doc/fontconfig-devel.sgml fontconfig-devel.html
touch -r doc/fontconfig-devel.sgml fontconfig-devel.pdf

# rename fc-cache binary
mv $RPM_BUILD_ROOT%{_bindir}/fc-cache $RPM_BUILD_ROOT%{_bindir}/fc-cache-%{__isa_bits}

# create link to man page
echo ".so man1/fc-cache.1" > $RPM_BUILD_ROOT%{_mandir}/man1/fc-cache-%{__isa_bits}.1

install -p -m 0755 %{SOURCE2} $RPM_BUILD_ROOT%{_bindir}/fc-cache

%find_lang %{name}
%find_lang %{name}-conf
cat %{name}-conf.lang >> %{name}.lang

%check
# The upstream test suite (run-test.sh) requires the separate fonttest data
# submodule which is not part of the release tarball, so tests are skipped.

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
%doc fontconfig-user.txt fontconfig-user.html fontconfig-user.pdf
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
%dir /usr/lib/fontconfig
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
%doc fontconfig-devel.txt fontconfig-devel.html fontconfig-devel.pdf

%changelog
* Fri Aug 07 2026 like-me <like-me@opensuse.org> - 2.18.1-1
- Initial packaging of fontconfig 2.18.1 for EPEL 10- rebuilt against the epel-10 repo (AlmaLinux:10 baseos/appstream/CRB + Fedora:EPEL:10 standard)

- autotools build (meson >= 1.11 required upstream, but RHEL 10 has meson 1.4.x)
- based on the Fedora rawhide spec, adapted to el10 and 2.18.1
