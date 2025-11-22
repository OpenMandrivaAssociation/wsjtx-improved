%define	_disable_ld_no_undefined 1
%define sourcedate 251101
%define version_no_date 3.0.0
%define oname wsjtx

Name:		wsjtx-improved
Summary:	Provides all popular modes for Weak Signal digital Amateur Radio
Version:	3.0.0.%{sourcedate}
Release:	1
License:	GPL-3.0-or-later
URL:		https://sourceforge.net/projects/wsjt-x-improved/
Group:		Communications/Radio
Source0:	https://sourceforge.net/projects/wsjt-x-improved/files/WSJT-X_v%{version_no_date}/Source%%20code/Qt6/wsjtx-%{version_no_date}_improved_PLUS_%{sourcedate}_qt6.tgz

BuildRequires:	a2x
BuildRequires:	asciidoc
BuildRequires:	cmake
BuildRequires:	boost-devel
BuildRequires:	desktop-file-utils
BuildRequires:	dos2unix
BuildRequires:	gcc-gfortran
BuildRequires:	glibc-devel
BuildRequires:	gomp-devel
BuildRequires:	kwin-aurorae
BuildRequires:	hamlib-utils
BuildRequires:	hamlib++-devel
BuildRequires:	ninja
BuildRequires:	pkgconfig
BuildRequires:	pkgconfig(fftw3)
BuildRequires:	pkgconfig(fftw3f)
BuildRequires:	pkgconfig(hamlib)
BuildRequires:	pkgconfig(libxslt)
BuildRequires:	pkgconfig(libusb-1.0)
BuildRequires:	pkgconfig(Qt6Core)
BuildRequires:	pkgconfig(Qt6Concurrent)
BuildRequires:	pkgconfig(Qt6Gui)
BuildRequires:	pkgconfig(Qt6Linguist)
BuildRequires:	pkgconfig(Qt6Multimedia)
BuildRequires:	pkgconfig(Qt6Network)
BuildRequires:	pkgconfig(Qt6OpenGL)
BuildRequires:	pkgconfig(Qt6PrintSupport)
BuildRequires:	pkgconfig(Qt6SerialPort)
BuildRequires:	pkgconfig(Qt6Sql)
BuildRequires:	pkgconfig(Qt6Svg)
BuildRequires:	pkgconfig(Qt6Test)
BuildRequires:	pkgconfig(Qt6UiPlugin)
BuildRequires:	pkgconfig(Qt6WebSockets)
BuildRequires:	pkgconfig(Qt6Widgets)
BuildRequires:	pkgconfig(udev)
BuildRequires:	qmake-qt6
BuildRequires:	qt6-qtmultimedia-gstreamer
BuildRequires:	qt6-qtbase-sql-firebird
BuildRequires:	qt6-qtbase-sql-mariadb
BuildRequires:	qt6-qtbase-sql-odbc
BuildRequires:	qt6-qtbase-sql-postgresql
BuildRequires:	qt6-qtbase-theme-gtk3
BuildRequires:	qt6-qttools-linguist-tools
BuildRequires:	qt6-qttranslations
BuildRequires:	vulkan-headers

# Obsoletes the old  wsjtx qt5-based package as this package
# replaces it and they would also have file conflicts.
Obsoletes:	wsjtx < 3.0.0

%description
%{name} is a Qt6 fork of wsjtx which is a program designed to facilitate
basic amateur radio communication using very weak signals.

WSJT-X_IMPROVED is published by Uwe Risse, DG2YCB.
It is an enhanced edition of the excellent WSJT-X software by
Joe Taylor K1JT, Steve Franke K9AN, Bill Somerville G4WJS,
Uwe Risse DG2YCB and others that provides several additional features
and improvements, as well as more frequent updates and bug fixes.

The first four letters in the program name stand for
“Weak Signal communication by K1JT,” while the suffix “-X” indicates that
WSJT-X started as an extended (and experimental) branch of the program WSJT.

This package is aimed primarily at the LF, MF, and HF bands and now includes
the following modes:

FST4, FST4W, FT4, FT8, JT4, JT9, JT65, Q65, MSK144, WSPR and Echo.

%prep
%autosetup -n %{oname}-%{version_no_date} -p1
# remove bundled hamlib
rm -f src/hamlib*.tgz* src/hamlib*.tar.gz*
# Extract wsjtx source and clean up
tar -xzf src/%{oname}.tgz
rm -f src/wsjtx.tgz*
find ./ -type f -exec chmod -x {} \;
cd %{oname}
# convert CR + LF to LF
dos2unix *.ui *.iss *.txt
dos2unix AUTHORS
dos2unix BUGS
dos2unix NEWS
dos2unix README
dos2unix THANKS
dos2unix example_log_configurations/*
# fix .desktop file line endings
dos2unix *.desktop

# We have to sed the following after extraction because the wsjtx CMakeLists.txt
# is inside a tgz within the source tarball archive.

# Fix install targets, re-add message_aggregator
sed -i -e 's@#install (TARGETS udp_daemon message_aggregator wsjtx_app_version@install (TARGETS udp_daemon message_aggregator wsjtx_app_version@g' CMakeLists.txt
sed -i -e '/install (TARGETS udp_daemon wsjtx_app_version/d' CMakeLists.txt

# Fixup CMakeLists - move sounds into CMAKE_INSTALL_DATADIR/%%{oname}/sounds
sed -i -z -e 's@install (DIRECTORY\n  ${PROJECT_SOURCE_DIR}/sounds\n  DESTINATION ${CMAKE_INSTALL_BINDIR}\n  #COMPONENT runtime\n  )@install (DIRECTORY\n  ${PROJECT_SOURCE_DIR}/sounds\n  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME}\n  #COMPONENT runtime\n  )@g' CMakeLists.txt

# Fixup CMakeLists - move ALLCALL7.txt into CMAKE_INSTALL_DATADIR/%%{oname}
sed -i -z -e 's@install (FILES\n  ALLCALL7.TXT\n  DESTINATION ${CMAKE_INSTALL_BINDIR}\n  #COMPONENT runtime\n  )@install (FILES\n  ALLCALL7.TXT\n  DESTINATION ${CMAKE_INSTALL_DATADIR}/${CMAKE_PROJECT_NAME}\n  #COMPONENT runtime\n  )@g' CMakeLists.txt

%build
# The fortran code in this package is not type safe and will thus not work
# with LTO.  Additionally there are numerous bogus strncat calls that also
# need to be fixed for this package to work with LTO
#define _lto_cflags %{nil}

export CFLAGS="%{optflags} -fno-lto -Wno-error=deprecated-declarations -Wno-error=unused-result"
export CXXFLAGS="%{optflags} -fno-lto -Wno-error=deprecated-declarations -Wno-error=unused-result"
export LDFLAGS="-Wl,--as-needed"
# suppress fortran warning log spam
export FFLAGS="-fallow-argument-mismatch"
export CC=/usr/bin/gcc
export CXX=/usr/bin/g++
export FC=/usr/bin/gfortran
# workaround for hamlib check, i.e. for hamlib_LIBRARY_DIRS not to be empty
export PKG_CONFIG_ALLOW_SYSTEM_LIBS=1

cd %{oname}

mkdir -p %{oname}/build
%cmake -Dhamlib_STATIC=FALSE \
	-DWSJT_GENERATE_DOCS=OFF \
	-DBoost_NO_SYSTEM_PATHS=FALSE \
	-DBOOST_INCLUDEDIR=%{_includedir}/boost \
	-DBOOST_LIBRARYDIR=%{_libdir} \
	-G Ninja

%ninja_build

%install
cd %{oname}
%ninja_install -C build

# Make sure the right style is used.
desktop-file-edit --set-key=Exec --set-value="wsjtx --style=fusion" \
    %{buildroot}/%{_datadir}/applications/%{oname}.desktop
# desktop files
desktop-file-validate %{buildroot}%{_datadir}/applications/wsjtx.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/message_aggregator.desktop

# fix docs
rm -f %{buildroot}%{_datadir}/doc/WSJT-X/{INSTALL,COPYING,copyright,changelog.Debian.gz}
install -p -m 0644 -t %{buildroot}%{_datadir}/doc/%{oname} GUIcontrols.txt jt9.txt \
  Release_Notes.txt v1.7_Features.txt wsjtx_changelog.txt

%files
%license COPYING
%doc %{_datadir}/doc/%{oname}
%{_bindir}/cablog
%{_bindir}/EchoCallSim
%{_bindir}/echosim
%{_bindir}/fcal
%{_bindir}/fmeasure
%{_bindir}/fmtave
%{_bindir}/fst4sim
%{_bindir}/hash22calc
%{_bindir}/jt4code
%{_bindir}/jt65code
%{_bindir}/jt9
%{_bindir}/jt9code
%{_bindir}/ft8code
%{_bindir}/message_aggregator
%{_bindir}/msk144code
%{_bindir}/q65code
%{_bindir}/q65sim
%{_bindir}/rigctl-wsjtx
%{_bindir}/rigctlcom-wsjtx
%{_bindir}/rigctld-wsjtx
%{_bindir}/testEchoCall
%{_bindir}/udp_daemon
%{_bindir}/wsjtx
%{_bindir}/wsjtx_app_version
%{_bindir}/wsprd
%{_mandir}/man1/*.1.*
%{_datadir}/applications/wsjtx.desktop
%{_datadir}/applications/message_aggregator.desktop
%{_datadir}/pixmaps/wsjtx_icon.png
%{_datadir}/%{oname}
