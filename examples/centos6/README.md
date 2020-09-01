Minimal CentOS example
======================

## Description

This directory contains the minimal set of files for a simple « ClouBed » with
CentOS 6.4 amd64.

It uses a kickstart file for a fully automatic installation of CentOS by PXE and
an iPXE profile to launch the setup in the VM. The content of the kickstart file
is rather minimal, you should probably have a deeper look through it for better
settings. The documentation in the Fedora wiki is a good starting point:
https://fedoraproject.org/wiki/Anaconda/Kickstart

## Adapt and Use

You really SHOULD adapt the following settings in file `templates/centos.ks`:

* a geographically closer mirror of CentOS ;
* the root password.

Before launching the installation, you will need to follow these steps:

### Create necessary directories

Create directories that will respectively store the virtual disk image of the
virtual machine and all the files downloaded by HTTP:

```sh
mkdir pool http
```
### Download CentOS PXE environment

Download both the kernel and initrd provided by CentOS for PXE boot:

```sh
wget http://mirror.centos.org/centos/6/os/x86_64/images/pxeboot/initrd.img -O http/initrd.img
wget http://mirror.centos.org/centos/6/os/x86_64/images/pxeboot/vmlinuz -O http/vmlinuz
```

### Launch installation

Then, launch the ClouBed python script that will sequentially:

1. boot your VM on PXE
2. wait for the CentOS installation to finish and the VM to shutdown
3. reboot your VM on the freshly installed CentOS system

```sh
python install.py
```

### Profit!

You're done! You can now connect with SSH to your newly created VM:

```sh
ssh root@10.6.0.10
```
