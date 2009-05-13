%define cvs cvs15

Name:           xdtv
Version:        2.4.1
Release:        0.5%{?cvs}%{?dist}
Summary:        Video4Linux Stream Capture Viewer & Recorder

Group:          Applications/Multimedia
License:        GPLv2+
URL:            http://xawdecode.sourceforge.net/
Source0:        http://downloads.sourceforge.net/xawdecode/xdtv-%{version}%{?cvs}.tar.gz
Source1:        xdtv_v4l-conf.pam
Source2:        xdtv.desktop
Source3:        xdtv_wizard.desktop
Patch0:         xdtv-2.4.1cvs15-noldffmpeg.patch
Patch1:         xdtv-2.4.1cvs15-libv4l2.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)


BuildRequires:  desktop-file-utils
BuildRequires:  xorg-x11-font-utils
BuildRequires:  xorg-x11-server-utils
BuildRequires:  yasm xterm
BuildRequires:  libtool automake17

BuildRequires:  a52dec-devel
BuildRequires:  faac-devel
BuildRequires:  ffmpeg-devel
BuildRequires:  lame-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  lirc-devel
BuildRequires:  libpng-devel
BuildRequires:  libv4l-devel
BuildRequires:  libvorbis-devel
BuildRequires:  xvidcore-devel
BuildRequires:  zvbi-devel

BuildRequires:  alsa-lib-devel
BuildRequires:  neXtaw-devel
BuildRequires:  SDL-devel
BuildRequires:  curl-devel
BuildRequires:  dbus-devel
BuildRequires:  dbus-glib-devel

BuildRequires:  libXxf86dga-devel libXxf86vm-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXmu-devel
BuildRequires:  libXt-devel
BuildRequires:  libXpm-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libXv-devel



#Needed for consolehelper
Requires: usermode


%description
XdTV is a software that allows you to to record & watch TV.
It interacts with AleVT for Teletext and Nxtvepg for NextView,
and uses the video4linux API. It can use some deinterlacing filters
and can record video files in various containers (AVI, MPEG, OGG, etc.) 
with many codecs (FFMpeg(>=0.4.6), XviD(0.9 & 1.x),
Ogg Theora (>=1.0alpha5) & Vorbis and DivX4/5).
It has also some plugin capabilities.

%package        devel
Summary:        Developpement files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}
Requires:       neXtaw-devel
Requires:       libXt-devel


%description    devel
Developpement files for %{name}

%package        OSD-font
Summary:        Font used by %{name} OSD function
Group:          User Interface/X
Requires:       %{name} = %{version}-%{release}

%description    OSD-font
Font used by %{name} OSD function.

# -----------------------------------------------------------------------------

%prep
%setup -q -n %{name}-%{version}%{?cvs}

# fix flags
sed -i -e 's|PERF_FLAGS=|#PERF_FLAGS=|' src/Makefile.am src/Makefile.in

# Fix plugdir for lib64
sed -i -e  's|lib/xdtv-plugins|%{_lib}/xdtv-plugins|' src/plugin.c

# Convert not UTF-8 files
mkdir -p __temp
for f in README.ffmpeg README.lirc README.xvid FAQfr-xdtv ;do
cp -p $f __temp/$f
iconv -f ISO-8859-1 -t UTF-8 __temp/$f > $f
touch -r __temp/$f $f
done
rm -rf __temp

#Fix for alevtparams_ui.c
sed -i.neXtaw -e 's|X11/Xaw|X11/neXtaw|g' src/*.{c,h} src/devicemanager/devicemanager_ui.c

#Patching to remove doubfully support for oldish ffmpeg
%patch0 -p1 -b .noldffmpeg
%patch1 -p1 -b .libv4l2

#Prevent internal ffmpeg to be used.
rm -rf libav* libpostproc libswscale

#hack xvidAPI - added in patch1
#sed -i.xvid42 -e 's/4, 0/4, 2/' configure.in configure
autoreconf -vif


# -----------------------------------------------------------------------------

%build
export CFLAGS="$RPM_OPT_FLAGS $(pkg-config --cflags libavformat libavcodec)"
export CPPFLAGS="$RPM_OPT_FLAGS $(pkg-config --cflags libavformat libavcodec)"
%configure --disable-divx4linux \
  --enable-arch-detection \
  --enable-cpu-options \
  --disable-static \
  --with-fontdir=%{_datadir}/X11/fonts/misc --enable-smallfont \
  --enable-pixmaps \
  --with-external-ffmpeg \
  --with-dbus
  

make %{?_smp_mflags}

# -----------------------------------------------------------------------------

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR="$RPM_BUILD_ROOT" INSTALL="install -p " install
find $RPM_BUILD_ROOT -type f -name "*.la" -exec rm -f {} ';'

# Make xdtv owns the plugin dir
mkdir -p $RPM_BUILD_ROOT%{_libdir}/xdtv-plugins

# Make xdtv owns the locales dir
mkdir -p $RPM_BUILD_ROOT%{_libdir}/xdtv

# remove the setuid root of this file (need to be root to use it)
chmod 0755 $RPM_BUILD_ROOT%{_bindir}/xdtv_v4l-conf

# xdtv_v4l-conf  stuff - inspired from xawtv

mkdir -p $RPM_BUILD_ROOT%{_sbindir} \
  $RPM_BUILD_ROOT%{_sysconfdir}/pam.d \
  $RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps \

install -pm 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/xdtv_v4l-conf

cat >xdtv_v4l-conf.apps <<!
SESSION=true
USER=root
PROGRAM=%{_sbindir}/xdtv_v4l-conf
!
install -m 0644 xdtv_v4l-conf.apps $RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps/xdtv_v4l-conf

mv $RPM_BUILD_ROOT%{_bindir}/xdtv_v4l-conf $RPM_BUILD_ROOT%{_sbindir}/
ln -s consolehelper $RPM_BUILD_ROOT%{_bindir}/xdtv_v4l-conf

# Deprecated
rm -rf $RPM_BUILD_ROOT%{_datadir}/X11/fonts/misc/fonts.dir
rm -rf $RPM_BUILD_ROOT%{_datadir}/X11/fonts/misc/fonts.scale

#Icons
for i in 16 32 48 ; do
  mkdir -p $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps
  install -pm 0644 %{name}-${i}.png \
    $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done

#Desktop
mkdir -p $RPM_BUILD_ROOT%{_datadir}/applications

desktop-file-install \
  --vendor "" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --mode 0644 \
  %{SOURCE2}

desktop-file-install \
  --vendor "" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --mode 0644 \
 %{SOURCE3}



# -----------------------------------------------------------------------------

%clean
rm -rf $RPM_BUILD_ROOT

# -----------------------------------------------------------------------------

%post
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi 
%{_bindir}/update-desktop-database %{_datadir}/applications || :

%postun
%{_bindir}/update-desktop-database %{_datadir}/applications
touch --no-create %{_datadir}/icons/hicolor
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor
fi || :


%post OSD-font
if [ -x %{_bindir}/fc-cache ]; then
   %{_bindir}/fc-cache %{_datadir}/X11/fonts/misc
fi

%postun OSD-font
if [ "$1" = "0" ]; then
   if [ -x %{_bindir}/fc-cache ]; then
      %{_bindir}/fc-cache %{_datadir}/X11/fonts/misc
   fi
fi

%files
%defattr(-,root,root,-)
%doc AUTHORS COPYING INSTALL FAQfr-xdtv TODO
%doc README README.dvb README.record README.bs README.ffmpeg README.streaming
%doc README.bsd README.gentoo README.xvid README.buildme README.lirc
%doc README.deinterlace README.plugins ChangeLog lisez-moi xdtvrc.sample
%doc lircrc.miro.sample lircrc.hauppauge.sample lircrc.animax.sample
%doc lircrc.WinfastTV2000.sample
%{_sbindir}/xdtv_v4l-conf
%{_bindir}/xdtv*
%{_datadir}/X11/app-defaults/XdTV
%config %{_sysconfdir}/pam.d/xdtv_v4l-conf
%config %{_sysconfdir}/security/console.apps/xdtv_v4l-conf
%config %{_sysconfdir}/xdtv/%{name}_wizard-en.conf
%config %{_sysconfdir}/xdtv/%{name}_wizard-en-UTF8.conf
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_datadir}/xdtv/
%{_datadir}/applications/*xdtv.desktop
%{_datadir}/applications/*xdtv_wizard.desktop
%{_mandir}/man1/*.1.gz
# Directory for plugins
%dir %{_libdir}/xdtv-plugins
# Directory for locales
%dir %{_libdir}/xdtv

%files devel
%defattr(-,root,root,-)
%{_includedir}/%{name}/

%files OSD-font
%defattr(-,root,root,-)
%{_datadir}/X11/fonts/misc/*.pcf.gz


%changelog
* Wed Apr  8 2009 kwizart < kwizart at gmail.com > - 2.4.1-0.5cvs15
- Add libv4l2 support
- Fix xvidcore API 4.2
- Remove hardcoded PERF_FLAGS
- Add desktop files in SOURCE

* Mon Apr  6 2009 kwizart < kwizart at gmail.com > - 2.4.1-0.4cvs15
- Update to 2.4.1cvs15

* Mon Jan  5 2009 kwizart < kwizart at gmail.com > - 2.4.1-0.3cvs14
- Update to 2.4.1cvs14

* Mon Oct 14 2008 kwizart < kwizart at gmail.com > - 2.4.1-0.2cvs13
- Add PAM support - picked from xawtv
  (instead of having xdtv_v4l-conf to be setuid root)
- Re-order configure options
- Only use neXtaw instead of Xaw

* Mon Sep 29 2008 kwizart < kwizart at gmail.com > - 2.4.1-0.1cvs13
- Update to 2.4.1cvs13

* Thu Aug 28 2008 kwizart < kwizart at gmail.com > - 2.4.1-0.1cvs12
- Update to 2.4.1cvs12

* Tue Mar 25 2008 kwizart < kwizart at gmail.com > - 2.4.1-0.1cvs8
- Update to 2.4.1cvs8

* Sat Jan 12 2008 kwizart < kwizart at gmail.com > - 2.4.1-0.1cvs5
- Update to 2.4.1cvs5

* Thu Dec  6 2007 kwizart < kwizart at gmail.com > - 2.4.1-0.1cvs4
- Update to 2.4.1cvs4

* Wed Nov  7 2007 kwizart < kwizart at gmail.com > - 2.4.1-0.1cvs3
- Update to 2.4.1cvs3

* Thu Oct 25 2007 kwizart < kwizart at gmail.com > - 2.4.1-0.1cvs2
- Update to pre 2.4.1 cvs2
- Fix the plugin directory on lib64
- Remove info post postun

* Mon Feb 27 2007 kwizart < kwizart at gmail.com > - 2.4.0-1
- Update to final 2.4.0
- remove desktop file vendor and add category

* Mon Feb 05 2007 kwizart < kwizart at gmail.com > - 2.4.0-0.10.pre0
- Fix compile flags

* Wed Jan  3 2007 kwizart < kwizart at gmail.com > - 2.4.0-0.9.pre0
- ffmpeg-rebuild
- some patches from gentoo
- conform to versioning guidelines
- tweak some includes in divx.h
- Enabled Optimization

* Sun Dec 17 2006 kwizart < kwizart at gmail.com > 2.4.0pre0-8.kwizart.fc6
- Try to use ffmpeg-amr-devel with static lib with xdtv

* Sun Dec 10 2006 kwizart < kwizart at gmail.com > 0:2.4.0pre0-7.kwizart.fc6
- Cleaned spec file.

* Sat Nov 11 2006 kwizart < kwizart at gmail.com > 0:2.4.0pre0-6.kwizart.fc6
- libdir in configure.
- cleaned spec file for livna.org.
- Now use updated ffmpeg tarball from livna 20061030 src.rpm.
- Re-use x264 from livna.

* Wed Nov 06 2006 kwizart < kwizart at gmail.com > - 0:2.4.0pre0-5.kwizart.fc6
- New release for fc6

* Tue Oct 17 2006 kwizart < kwizart at gmail.com > - 0:2.4.0pre0-4.kwizart.FC5
- dropped x264 - recent x264 version won't build with xdtv
- man files are in correct place.

* Sat Sep 22 2006 kwizart < kwizart at gmail.com > - 0:2.4.0pre0-3.kwizart.FC5
- amr support (amrnb_float amrwb_float).

* Sun Sep 16 2006 kwizart < kwizart at gmail.com > - 0:2.4.0pre0-2.kwizart.FC5
- Cleaned $RPM_BUILD_ROOT tags / 
- Problem with application cache / fixed?

* Fri Aug 04 2006 kwizart < kwizart at gmail.com >
- switch to livna release

* Sat Mar 25 2006 Sir Pingus <pingus_77@yahoo.fr> 2.3.2-1fc5
- 2.3.2 on FC5
- The system app-defaults/ directory for X resources is now /usr/share/X11/app-defaults/ 
  on Fedora Core 5 and for future Red Hat Enterprise Linux systems.
- FC5 has modular X. All the libraries that were in xorg-x11-devel now have their own packages 
  and you need to include the -devel packages for the libraries your project is actually using.
- all infos here: http://fedora.redhat.com/docs/release-notes/fc5/
- new paths for desktop icons & TV misc fonts & font utils

* Sun Mar 19 2006 Sir Pingus <pingus_77@yahoo.fr> 2.3.2-1fc4
- 2.3.2
- fix error with the instalation of the TV fonts (need chkfontpath).
- fix error with the path of the ressource file (not the same path than in a Mandriva distro).
- fix error with the menu update (the menu was not updated).
- fix error with the path of the man files (return back to the old method).

* Fri Feb 24 2006 Sir Pingus <pingus_77@yahoo.fr> 2.3.1-1fc4
- 2.3.1
- FFmpeg inside XdTV
- Add the possibility to compile with amr_nb & amr_wb

* Fri Dec 23 2005 Sir Pingus <pingus_77@yahoo.fr> - 2.3.0-1
- 2.3.0
- Compiled with --disable-divx4linux & neXtaw
- Spec file updated

* Sun Jul 03 2005 Sir Pingus <pingus_77@yahoo.fr> - 2.2.0-2
- add the xdtv_wizard menu entry

* Fri Jul 01 2005 Sir Pingus <pingus_77@yahoo.fr> - 2.2.0-1
- Upgrade to 2.2.0
- Compiled with --disable-divx4linux
- Spec file cleanup 

* Sun Apr 03 2005 Emmanuel Seyman <seyman@wanadoo.fr> - 2.1.1-1
- Upgrade to 2.1.1

* Sun Jan 02 2005 Emmanuel Seyman <seyman@wanadoo.fr> - 2.0.1-1
- Upgrade to 2.0.1
- Obsolete xawdecode
- Clean up installation instructions

* Fri Nov 28 2003 Emmanuel Seyman <seyman@wanadoo.fr> - 1.8.2-1
- Upgrade to 1.8.2

* Sat Oct 04 2003 Emmanuel Seyman <seyman@wanadoo.fr> - 1.8.1-1
- Upgrade to 1.8.1

* Tue Sep 02 2003 Emmanuel Seyman <seyman@wanadoo.fr> - 1.8.0-1
- Initial RPM release.
