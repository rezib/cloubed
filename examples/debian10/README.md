Minimal Debian example
======================

## Description

This directory contains the minimal set of files for a simple testbed with
Debian Buster amd64.

It uses a preseed file for a fully automatic installation of Debian with PXE.

The preseed is mainly based on the reference from Debian website:
http://www.debian.org/releases/buster/example-preseed.txt

Here is the diff applied against this reference:

```diff
--- example-preseed.cfg	2020-01-12 16:42:06.000000000 +0100
+++ preseed.cfg	2020-10-02 09:33:02.584975301 +0200
@@ -96,7 +96,7 @@
 # If you select ftp, the mirror/country string does not need to be set.
 #d-i mirror/protocol string ftp
 d-i mirror/country string manual
-d-i mirror/http/hostname string http.us.debian.org
+d-i mirror/http/hostname string deb.debian.org
 d-i mirror/http/directory string /debian
 d-i mirror/http/proxy string
 
@@ -110,11 +110,11 @@
 # use sudo).
 #d-i passwd/root-login boolean false
 # Alternatively, to skip creation of a normal user account.
-#d-i passwd/make-user boolean false
+d-i passwd/make-user boolean false
 
 # Root password, either in clear text
-#d-i passwd/root-password password r00tme
-#d-i passwd/root-password-again password r00tme
+d-i passwd/root-password password rootroot
+d-i passwd/root-password-again password rootroot
 # or encrypted using a crypt(3)  hash.
 #d-i passwd/root-password-crypted password [crypt(3) hash]
 
@@ -325,7 +325,7 @@
 
 
 ### Package selection
-#tasksel tasksel/first multiselect standard, web-server, kde-desktop
+tasksel tasksel/first multiselect standard, ssh-server
 
 # Individual additional packages to install
 #d-i pkgsel/include string openssh-server build-essential
@@ -337,7 +337,7 @@
 # installed, and what software you use. The default is not to report back,
 # but sending reports helps the project determine what software is most
 # popular and include it on CDs.
-#popularity-contest popularity-contest/participate boolean false
+popularity-contest popularity-contest/participate boolean false
 
 ### Boot loader installation
 # Grub is the default boot loader (for x86). If you want lilo installed
@@ -358,7 +358,7 @@
 
 # Due notably to potential USB sticks, the location of the MBR can not be
 # determined safely in general, so this needs to be specified:
-#d-i grub-installer/bootdev  string /dev/sda
+d-i grub-installer/bootdev  string /dev/vda
 # To install to the first device (assuming it is not a USB stick):
 #d-i grub-installer/bootdev  string default
 
@@ -398,7 +398,7 @@
 # reboot into the installed system.
 #d-i debian-installer/exit/halt boolean true
 # This will power off the machine instead of just halting it.
-#d-i debian-installer/exit/poweroff boolean true
+d-i debian-installer/exit/poweroff boolean true
 
 ### Preseeding other packages
 # Depending on what software you choose to install, or if things go wrong
@@ -431,5 +431,4 @@
 # still a usable /target directory. You can chroot to /target and use it
 # directly, or use the apt-install and in-target commands to easily install
 # packages and run commands in the target system.
-#d-i preseed/late_command string apt-install zsh; in-target chsh -s /bin/zsh
-
+d-i preseed/late_command string wget ${network.net.http_server}/http/preseed-late-command.sh -O /target/opt/preseed-late-command.sh; in-target bash /opt/preseed-late-command.sh
```

The main modifications is the late command downloaded by HTTP, using the
minimal embedded HTTP server in cloubed.

The purpose of the other minors modifications is only to avoid interactions in
the installation process.

You have probably noticed that the keymap is both set in preseed and iPXE
files. It is actually a workaround for Debian bug #693956.

## Adapt and Use

You really SHOULD adapt the following settings:

* the root password in `templates/preseed.cfg`
* your SSH public key in `http/preseed-late-command.sh`

Before launching the installation, you will need to follow those steps:

### Download and extract official Debian PXE environment

```sh
wget http://http.debian.net/debian/dists/buster/main/installer-amd64/current/images/netboot/netboot.tar.gz \
    -O http/netboot.tar.gz
tar -C http -xzf http/netboot.tar.gz
```

### Initialize storage pool directory

```sh
mkdir pool
```

### Launch the installation process

Then, launch the python script that fully orchestrate the installation process:

```sh
python3 install.py
```

You can watch the magic using Spice client:

```sh
spicec -h localhost -p 5900
```

When the installation is done, the VM should shutdown itself and be
automatically restarted on its disk by ClouBed.

### Profit!

Finally, you can use and feel totally free to break your freshly installed VM
as much you'd like :)

```sh
ssh root@10.5.0.10
```
