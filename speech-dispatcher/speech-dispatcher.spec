Name:           speech-dispatcher
Version:        0.12.1
Release:        1%{?dist}
Summary:        Common interface to speech synthesis

License:        GPL-2.0-or-later AND LGPL-2.1-or-later AND GFDL-1.2-or-later
URL:            https://freebsoft.org/speechd
Source:         https://github.com/brailcom/speechd/releases/download/%{version}/%{name}-%{version}.tar.gz

# espeak-ng is the default/free speech engine; flip with --without espeak if
# espeak-ng-devel is unavailable in the target repo (e.g. EPEL 10).
%bcond_without espeak
%bcond_without pulse
%bcond_without alsa

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  gettext
BuildRequires:  intltool
BuildRequires:  help2man
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  pkgconfig(dotconf)
BuildRequires:  pkgconfig(sndfile)
BuildRequires:  pkgconfig(libltdl)
BuildRequires:  python3-devel
BuildRequires:  python3-pyxdg
BuildRequires:  systemd-rpm-macros
%if %{with espeak}
BuildRequires:  pkgconfig(espeak-ng)
%endif
%if %{with pulse}
BuildRequires:  pkgconfig(libpulse)
%endif
%if %{with alsa}
BuildRequires:  pkgconfig(alsa)
%endif

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       python3-speechd = %{version}-%{release}
%if %{with espeak}
Recommends:     espeak-ng
%endif

%description
Speech Dispatcher is a device independent layer for speech synthesis, developed
with the goal of making the usage of speech synthesis easier for application
programmers. It takes care of most of the tasks necessary to solve in
speech-enabled applications.

%package libs
Summary:        Shared libraries for %{name}
License:        LGPL-2.1-or-later

%description libs
This package contains the shared libraries (libspeechd, libspeechd_module)
used by the %{name} daemon and its output modules.

%package -n python3-speechd
Summary:        Python bindings for %{name}
Requires:       python3-pyxdg
# The python client talks to the daemon over a socket; pull the server in
# so that `spd-conf` and the bindings are usable out of the box.
Requires:       %{name} = %{version}-%{release}

%description -n python3-speechd
This package contains the Python 3 bindings for %{name}, including the
`speechd` client library and the `spd-conf` configuration helper.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(glib-2.0)

%description devel
This package contains the header files, libraries and pkg-config file needed
for developing applications that use %{name}.

%prep
%autosetup

%build
%configure \
    --disable-static \
%if %{with espeak}
    --with-espeak-ng \
%else
    --without-espeak-ng \
%endif
%if %{with pulse}
    --with-pulse \
%else
    --without-pulse \
%endif
%if %{with alsa}
    --with-alsa \
%else
    --without-alsa \
%endif
    --without-flite \
    --without-ibmtts \
    --without-voxin \
    --without-pico \
    --without-baratinoo \
    --without-kali \
    --with-systemdsystemunitdir=%{_unitdir} \
    --with-systemduserunitdir=%{_userunitdir}

%make_build

%install
%make_install
find %{buildroot} -name '*.la' -delete
%find_lang %{name}

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%systemd_user_post speech-dispatcher.service speech-dispatcher.socket
%systemd_user_preun speech-dispatcher.service speech-dispatcher.socket
%systemd_post speech-dispatcherd.service
%systemd_preun speech-dispatcherd.service
%systemd_postun_with_restart speech-dispatcherd.service

%files -f %{name}.lang
%license COPYING.GPL-2 COPYING.GPL-3 COPYING.LGPL
%doc ANNOUNCE AUTHORS BUGS NEWS README TODO
%config(noreplace) %{_sysconfdir}/speech-dispatcher/speechd.conf
%config(noreplace) %{_sysconfdir}/speech-dispatcher/clients/*.conf
%config(noreplace) %{_sysconfdir}/speech-dispatcher/modules/*.conf
%{_bindir}/spd-say
%{_bindir}/spdsend
%{_bindir}/speech-dispatcher
%dir %{_libdir}/speech-dispatcher
%{_libdir}/speech-dispatcher/spd_*.so
%{_libexecdir}/speech-dispatcher-modules/sd_*
%{_datadir}/sounds/speech-dispatcher
%{_datadir}/speech-dispatcher
%{_mandir}/man1/spd-say.1*
%{_mandir}/man1/speech-dispatcher.1*
%{_userunitdir}/speech-dispatcher.service
%{_userunitdir}/speech-dispatcher.socket
%{_unitdir}/speech-dispatcherd.service

%files libs
%license COPYING.LGPL
%{_libdir}/libspeechd.so.*
%{_libdir}/libspeechd_module.so.*

%files -n python3-speechd
%{python3_sitelib}/speechd/
%{python3_sitelib}/speechd_config/
%{_bindir}/spd-conf
%{_mandir}/man1/spd-conf.1*

%files devel
%{_includedir}/speech-dispatcher/
%{_libdir}/libspeechd.so
%{_libdir}/libspeechd_module.so
%{_libdir}/pkgconfig/speech-dispatcher.pc

%changelog
* Thu Aug 14 2026 Inga Vesnova <inga.vesnova@gmail.com> - 0.12.1-1
- 0.12.1 for EPEL 10
- Split into speech-dispatcher (daemon + configs + modules + audio plugins),
  speech-dispatcher-libs (libspeechd), python3-speechd (bindings + spd-conf),
  and speech-dispatcher-devel
- Build espeak-ng output module + PulseAudio/ALSA audio by default
- Ship systemd user service + socket and system service
