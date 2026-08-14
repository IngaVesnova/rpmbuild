Name:          espeak-ng
Version:       1.52.0
Release:       1%{?dist}
Summary:       eSpeak NG Text-to-Speech

License:       GPL-3.0-only AND GPL-3.0-or-later AND Apache-2.0 AND BSD-2-Clause AND Unicode-DFS-2016 AND CC-BY-SA-3.0
URL:           https://github.com/espeak-ng/espeak-ng
Source0:       %{url}/archive/%{version}/%{name}-%{version}.tar.gz

# autotools build: the GitHub tag archive has no generated configure, so
# autogen.sh (autoreconf) is run in %build.
# pcaudiolib-devel is not available in EPEL 10; espeak-ng builds fine without
# it (only the standalone CLI audio *playback* is disabled, which
# speech-dispatcher does not need - it handles audio output itself).
BuildRequires: gcc-c++
BuildRequires: make
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: libtool
BuildRequires: pkgconfig
BuildRequires: gettext-devel

%description
The eSpeak NG (Next Generation) Text-to-Speech program is an open source speech
synthesizer that supports over 70 languages. It is based on the eSpeak engine
created by Jonathan Duddington. It uses spectral formant synthesis by default
which sounds robotic, but can be configured to use Klatt formant synthesis
or MBROLA to give it a more natural sound.

%package devel
Summary: Development files for espeak-ng
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
Development files for eSpeak NG, a software speech synthesizer.

%package vim
Summary: Vim syntax highlighting for espeak-ng data files
BuildArch: noarch
Requires: %{name} = %{version}-%{release}

%description vim
%{summary}.

%prep
%autosetup
# Remove unused files to make sure we've got the License tag right
rm -rf src/include/compat/endian.h src/compat/getopt.c android/

%build
./autogen.sh
%configure
%make_build src/espeak-ng src/speak-ng
make

%install
%make_install
rm -vf %{buildroot}%{_libdir}/libespeak-ng-test.so*
rm -vf %{buildroot}%{_libdir}/*.{a,la}
# Remove files conflicting with espeak
rm -vf %{buildroot}%{_bindir}/{speak,espeak}
rm -vrf %{buildroot}%{_includedir}/espeak
# Move Vim files
mv %{buildroot}%{_datadir}/vim/addons %{buildroot}%{_datadir}/vim/vimfiles
rm -vrf %{buildroot}%{_datadir}/vim/registry

%ldconfig_scriptlets

%files
%license COPYING
%license COPYING.APACHE
%license COPYING.BSD2
%license COPYING.UCD
%doc README.md
%doc ChangeLog.md
%{_bindir}/speak-ng
%{_bindir}/espeak-ng
%{_libdir}/libespeak-ng.so.1
%{_libdir}/libespeak-ng.so.1.*
%{_datadir}/espeak-ng-data

%files devel
%{_libdir}/pkgconfig/espeak-ng.pc
%{_libdir}/libespeak-ng.so
%{_includedir}/espeak-ng

%files vim
%{_datadir}/vim/vimfiles/ftdetect/espeakfiletype.vim
%{_datadir}/vim/vimfiles/syntax/espeaklist.vim
%{_datadir}/vim/vimfiles/syntax/espeakrules.vim

%changelog
* Thu Aug 14 2026 Inga Vesnova <inga.vesnova@gmail.com> - 1.52.0-1
- 1.52.0 for EPEL 10 (EPEL ships outdated 1.51.1)
- Built from upstream GitHub tag; autotools build via autogen.sh
- Subpackages: espeak-ng (lib + binary + data), -devel, -vim, -doc
- Provides espeak-ng.pc / libespeak-ng.so for speech-dispatcher
