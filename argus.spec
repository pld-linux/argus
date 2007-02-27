# TODO
# - configure without options not working
# - useradd -o should not be allowed! (also kill other unneccessary opts)
#
# Conditional build:
%bcond_without	tcp_wrappers	# build with tcp_wrappers support
%bcond_without	sasl		# build with sasl support
#
%define		_ver_major	3.0
%define		_ver_minor	0
%define		_rc		rc.40
%define		_rel	0.2
Summary:	Real time network flow monitor
Summary(pl.UTF-8):	Monitor obciążenia sieci czasu rzeczywistego
Name:		argus
Version:	%{_ver_major}.%{_ver_minor}
Release:	0.%{_rc}.%{_rel}
License:	GPL v2
Group:		Applications/Networking
Source0:	ftp://qosient.com/dev/argus-%{_ver_major}/%{name}-%{version}.%{_rc}.tar.gz
# Source0-md5:	49047be6450c6255cceb3fb9bfe3caed
Source1:	%{name}.conf
Source2:	%{name}.init
Source3:	%{name}.sysconfig
Source4:	%{name}.logrotate
URL:		http://www.qosient.com/argus/
BuildRequires:	bison
%{?with_tcp_wrappers:BuildRequires:	cyrus-sasl-devel}
BuildRequires:	libpcap-devel
%{?with_tcp_wrappers:BuildRequires:	libwrap-devel}
BuildRequires:	rpmbuild(macros) >= 1.268
Requires(post,preun):	/sbin/chkconfig
Requires:	rc-scripts
Provides:	group(argus)
Provides:	user(argus)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Argus is a Real Time Flow Monitor designed to track and report on the
status and performance of all network transactions seen in a data
network traffic stream. It is similiar to Cisco NetFlow, however more
powerful and with different data format.

%description -l pl.UTF-8
Argus jest monitorem sieci czasu rzeczywistego zaprojektowanym do
śledzenia i raportowania stanu sieci oraz wszelkiego typu transakcji
strumieni danych. Jest bardzo podobny do NetFlow z Cisco, jednak
bardziej rozbudowany i posiada inny format danych.

%prep
%setup -q -n %{name}-%{version}.%{_rc}

%build
%configure \
	--with%{!?with_tcp_wrappers:out}-libwrap \
	--with%{!?with_sasl:out}-sasl
%{__make}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -d $RPM_BUILD_ROOT/etc/{logrotate.d,rc.d/init.d,sysconfig}
install -d $RPM_BUILD_ROOT%{_var}/log/%{name}

install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/%{name}
install %{SOURCE4} $RPM_BUILD_ROOT/etc/logrotate.d/%{name}

touch $RPM_BUILD_ROOT%{_var}/log/%{name}/%{name}.log

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 214 -r argus
%useradd -M -o -r -u 214 -d /usr/share/empty -s /bin/sh -g argus -c "argus daemon" argus

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc CREDITS ChangeLog README doc/{CHANGES,FAQ,HOW-TO}
%attr(755,root,root) %{_bindir}/argusbug
%attr(755,root,root) %{_sbindir}/argus
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/logrotate.d/%{name}
%dir %{_var}/log/%{name}
%attr(640,argus,root,) %ghost %{_var}/log/%{name}/%{name}.log
%{_mandir}/man5/argus.conf.5*
%{_mandir}/man8/argus.8*
