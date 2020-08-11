%global name sentry

Name:            %{name}
Version:         8.21.0
Release:         5%{?dist}
Summary:         A realtime logging and aggregation server

License:         BSD
URL:             https://pypi.python.org/pypi/sentry
Source0:         %{name}.service
Source1:         supervisord.conf
Source2:         00001-fix-wsgi-crash.patch
BuildArch:       x86_64

BuildRequires:   libjpeg-devel
BuildRequires:   libpq-devel
BuildRequires:   libtool-ltdl-devel
BuildRequires:   python2-devel
BuildRequires:   python2-pip
BuildRequires:   python2-virtualenv
BuildRequires:   xmlsec1-devel
BuildRequires:   zlib-devel

Requires:        postgresql-contrib
Requires:        postgresql-server
Requires:        redis
Requires:        supervisor

Requires(pre):   shadow-utils
Requires(post):  systemd
Requires(preun): systemd


# Do not include debuginfo symlinks from /usr/lib/.build-id because they
# conflict with python2 package:
%define _build_id_links none


%description
Sentry is a modern error logging and aggregation platform.


%build
virtualenv-2 %{name}-%{version}
cd %{name}-%{version}
source bin/activate

# Build with gcc (not clang), https://github.com/getsentry/libsourcemap/pull/8
export LIBSOURCEMAP_MANYLINUX=1 SYMSYND_MANYLINUX=1
pip2 install \
  psycopg2 \
  'sentry[postgres]==%{version}' \
  sentry-plugins==8.21.0 \
  https://github.com/getsentry/sentry-auth-google/archive/52020f5.zip

patch -p1 -i %SOURCE2

virtualenv-2 --relocatable .


%install
mkdir -p %{buildroot}/opt
cp -r %{name}-%{version} %{buildroot}/opt/%{name}

mkdir -p %{buildroot}%{_bindir}
ln -s /opt/%{name}/bin/sentry %{buildroot}%{_bindir}/%{name}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
%{buildroot}/opt/%{name}/bin/sentry init %{buildroot}%{_sysconfdir}/%{name}/
cp %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}

install -D -m 644 %{SOURCE0} %{buildroot}%{_unitdir}/%{name}.service

mkdir -p %{buildroot}/run/%{name}
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}

sed -i 's|/builddir/build/BUILD/%{name}-%{version}|/opt/%{name}|g' \
  $(grep -lrIE '/builddir/build/BUILD/%{name}-%{version}' %{buildroot}/opt)

sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/env python2.7|g' \
  $(grep -lrIE '^#!/usr/bin/env python$' %{buildroot}/opt)


%files
/opt/%{name}

%{_bindir}/%{name}

%dir %{_sysconfdir}/%{name}
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/sentry.conf.py
%config(noreplace) %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/config.yml
%config %attr(0644, %{name}, %{name}) %{_sysconfdir}/%{name}/supervisord.conf

%attr(0755, -, -) %{_unitdir}/%{name}.service

%attr(0755, %{name}, %{name}) %dir /run/%{name}

%attr(0755, %{name}, %{name}) %dir %{_localstatedir}/log/%{name}


%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
  useradd -r -g %{name} -d /opt/%{name} -s /sbin/nologin %{name}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service


%changelog
* Tue Aug 11 2020 Adrien Vergé <adrienverge@gmail.com> - 8.21.0-5
- Add a patch to fix a WSGI crash when fetching assets

* Tue Aug 11 2020 Adrien Vergé <adrienverge@gmail.com> - 8.21.0-4
- Remove sentry-auth-github, that causes error logs

* Mon Aug 10 2020 Adrien Vergé <adrienverge@gmail.com> - 8.21.0-3
- Adapt and rebuild for CentOS 8

* Mon Nov 13 2017 Adrien Vergé <adrienverge@gmail.com> - 8.21.0-2
- Add postgresql-contrib requirement, see https://github.com/getsentry/sentry/issues/6098

* Mon Nov 13 2017 Adrien Vergé <adrienverge@gmail.com> - 8.21.0-1
- Update to new upstream version

* Mon Nov 13 2017 Adrien Vergé <adrienverge@gmail.com> - 8.17.0-3
- Tell systemd to create /run/sentry (otherwise supervisord crashes)

* Fri Jun 30 2017 Adrien Vergé <adrienverge@gmail.com> - 8.17.0-2
- Add Sentry plugins

* Fri Jun 30 2017 Adrien Vergé <adrienverge@gmail.com> - 8.17.0-1
- Update to new upstream version
- Add SSO providers for Google and GitHub

* Fri Sep 16 2016 Adrien Vergé <adrienverge@gmail.com> - 8.8.0-1
- Initial RPM release
