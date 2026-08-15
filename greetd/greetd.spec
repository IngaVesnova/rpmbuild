%global debug_package %{nil}

Name:           greetd
Version:        0.10.3
Release:        1%{?dist}
Summary:        Minimal and flexible login manager daemon

License:        GPL-3.0-only
URL:            https://git.sr.ht/~kennylevinsen/greetd
Source0:        https://git.sr.ht/~kennylevinsen/greetd/archive/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        greetd.sysusers
Source2:        greetd.pam

BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  pam-devel
BuildRequires:  systemd-rpm-macros

Requires:       pam

%description
greetd is a minimal, agnostic and flexible login manager daemon.

%prep
%autosetup -n %{name}-%{version}

%build
cargo build --release --locked

%install
install -D -m 0755 target/release/greetd %{buildroot}%{_sbindir}/greetd
install -D -m 0755 target/release/agreety %{buildroot}%{_bindir}/agreety

# Config file and PAM
install -D -m 0644 config.toml %{buildroot}%{_sysconfdir}/greetd/config.toml
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pam.d/greetd

# Systemd unit
install -D -m 0644 greetd.service %{buildroot}%{_unitdir}/greetd.service

# Sysusers declaration
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysusersdir}/greetd.conf

# Home for greetd user
install -d -m 0755 %{buildroot}%{_sharedstatedir}/greetd

%post
%systemd_post greetd.service

%preun
%systemd_preun greetd.service

%postun
%systemd_postun_with_restart greetd.service

%files
%license LICENSE
%{_sbindir}/greetd
%{_bindir}/agreety
%dir %attr(0755, root, greetd) %{_sysconfdir}/greetd
%config(noreplace) %{_sysconfdir}/greetd/config.toml
%config(noreplace) %{_sysconfdir}/pam.d/greetd
%{_unitdir}/greetd.service
%{_sysusersdir}/greetd.conf
%attr(0755, greetd, greetd) %dir %{_sharedstatedir}/greetd

%changelog
* Tue Aug 04 2026 Custom Distro Maintainer - 0.10.3-1
- Initial release for custom distro
