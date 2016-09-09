%{!?__python3: %global __python3 %__python}
%{!?python3_sitelib: %global python3_sitelib %(%{__python3} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}

%if 0%{?fedora}
%bcond_without python3
%else
%bcond_with python3
%endif

Name:           fileobj
Version:        0.7.34
Release:        1%{?dist}
Summary:        Hex Editor
Group:          Applications/Editors
License:        BSD
URL:            https://sourceforge.net/projects/%{name}/
Source0:        https://downloads.sourceforge.net/project/%{name}/%{name}-%{version}.tar.gz

# Upstream v0.7 branch runs on Python 2.6, 2.7 and 3.x, with the same functionality.
# Fedora RPM is packaged only for Python 3.x, based on what's written in
# https://fedoraproject.org/wiki/Packaging:Python#Avoiding_collisions_between_the_python_2_and_python_3_stacks

BuildArch:      noarch
BuildRequires:  python3-devel python3-setuptools

%description
%{name} is a portable hex editor with vi like interface.

%prep
%setup -q -n %{name}-%{version}

%build
%py3_build

%install
rm -rf $RPM_BUILD_ROOT
%py3_install
install -Dpm 644 script/%{name}.1 $RPM_BUILD_ROOT%{_mandir}/man1/%{name}.1

%files
%license COPYING
%doc CHANGES CONTRIBUTORS PKG-INFO README.md
%{python3_sitelib}/%{name}*
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1.gz

%changelog
* Tue May 24 2016 Tomohiro Kusumi <tkusumi@fedoraproject.org> - 0.7.34-1
- Initial build
