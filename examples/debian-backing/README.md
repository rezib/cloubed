Minimal Debian example
======================

## Description

This directory contains the minimal set of files for a simple testbed with
Debian Wheezy amd64 and volume backing.

It uses a preseed file for a fully automatic installation of Debian with PXE.

The preseed is mainly based on the reference from Debian website:
http://www.debian.org/releases/wheezy/example-preseed.txt

Here is the diff applied against this reference:

```diff
--- example-preseed.txt	2013-05-04 18:14:06.000000000 +0200
+++ templates/preseed.cfg	2013-07-16 21:22:49.085779501 +0200
@@ -113,7 +113,7 @@
 # Alternatively, to skip creation of a normal user account.
-#d-i passwd/make-user boolean false
+d-i passwd/make-user boolean false

 # Root password, either in clear text
-#d-i passwd/root-password password r00tme
-#d-i passwd/root-password-again password r00tme
+d-i passwd/root-password password rootroot
+d-i passwd/root-password-again password rootroot
 # or encrypted using an MD5 hash.
@@ -317,3 +317,3 @@
 ### Package selection
-#tasksel tasksel/first multiselect standard, web-server
+tasksel tasksel/first multiselect standard, ssh-server
 # If the desktop task is selected, install the kde and xfce desktops
@@ -332,3 +332,7 @@
 # popular and include it on CDs.
-#popularity-contest popularity-contest/participate boolean false
+popularity-contest popularity-contest/participate boolean false
+
+# This is fairly safe to set, it makes grub install automatically to the MBR
+# if no other operating system is detected on the machine.
+d-i grub-installer/only_debian boolean true

@@ -351,3 +355,3 @@
 # This will power off the machine instead of just halting it.
-#d-i debian-installer/exit/poweroff boolean true
+d-i debian-installer/exit/poweroff boolean true

@@ -384,3 +388,3 @@
 # packages and run commands in the target system.
-#d-i preseed/late_command string apt-install zsh; in-target chsh -s /bin/zsh
+d-i preseed/late_command string wget http://${network.net.ip_host}:5432/http/preseed-late-command.sh -O /target/opt/preseed-late-command.sh; in-target bash /opt/preseed-late-command.sh
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
wget http://http.debian.net/debian/dists/wheezy/main/installer-amd64/current/images/netboot/netboot.tar.gz \
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
python install.py
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
ssh root@10.5.0.11
```
