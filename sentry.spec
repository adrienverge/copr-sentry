%global name sentry

# Turn off the brp-python-bytecompile script because it compiles
# /etc/sentry/sentry.conf.py. Compile manually with % py_byte_compile.
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Name:            %{name}
Version:         8.17.0
Release:         1%{?dist}
Summary:         A realtime logging and aggregation server

License:         BSD
URL:             https://pypi.python.org/pypi/sentry
Source0:         %{name}.service
Source1:         supervisord.conf
BuildArch:       x86_64

BuildRequires:   libffi-devel
BuildRequires:   libjpeg-devel
BuildRequires:   libpqxx-devel
BuildRequires:   libxml2-devel
BuildRequires:   libxslt-devel
BuildRequires:   libyaml-devel
BuildRequires:   openssl-devel
BuildRequires:   postgresql-devel
BuildRequires:   python2-devel
BuildRequires:   python-pip
BuildRequires:   python-virtualenv
BuildRequires:   systemd
BuildRequires:   zlib-devel

Requires:        postgresql-server
Requires:        python-psycopg2
Requires:        redis
Requires:        supervisor

Requires(pre):   shadow-utils
Requires(post):  systemd
Requires(preun): systemd


%description
Sentry is a modern error logging and aggregation platform.


%build
virtualenv %{name}-%{version}
cd %{name}-%{version}
source bin/activate

# Needs pip >= 9
pip --version
pip install --upgrade pip
pip --version

# Build with gcc (not clang), https://github.com/getsentry/libsourcemap/pull/8
export LIBSOURCEMAP_MANYLINUX=1 SYMSYND_MANYLINUX=1
pip install 'sentry[postgres]==%{version}'
pip install https://github.com/getsentry/sentry-auth-google/archive/master.zip
pip install https://github.com/getsentry/sentry-auth-github/archive/master.zip

virtualenv --relocatable .


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

# Problem with this macro, it is not expanded, like it doesn't exist...
#% py_byte_compile %{__python2} %{buildroot}/opt/%{name}/lib

# For some reason this lib is not readable
chmod a+r \
  %{buildroot}/opt/%{name}/lib/python2.7/site-packages/httplib2/* \
  %{buildroot}/opt/%{name}/lib/python2.7/site-packages/httplib2-*.egg-info/*

sed -i 's|/builddir/build/BUILD/%{name}-%{version}|/opt/%{name}|g' \
  $(grep -lrIE '/builddir/build/BUILD/%{name}-%{version}' %{buildroot}/opt)


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
* Fri Jun 30 2017 Adrien Vergé <adrienverge@gmail.com> - 8.17.0-1
- Update to new upstream version
- Add SSO providers for Google and GitHub

* Fri Sep 16 2016 Adrien Vergé <adrienverge@gmail.com> - 8.8.0-1
- Initial RPM release
