install
#nfs --server=${network.net.ip_host} --dir=${domain.vmtest.tpl.nfs_ks_dir}
#url --url=http://mirror.centos.org/centos-7/7/os/x86_64 --proxy=http://proxy:3128
url --url=http://mirror.centos.org/centos-7/7/os/x86_64
lang en_US.UTF-8
keyboard us
network --hostname=vmtest --onboot yes --device eth0 --bootproto=dhcp --noipv6
rootpw rootroot
firewall --service=ssh
authconfig --enableshadow --passalgo=sha512
selinux --enforcing
timezone --utc Europe/Paris
zerombr
bootloader --location=mbr --driveorder=vda --append="crashkernel=auto rhgb quiet"
clearpart --all --drives=vda
autopart

poweroff

%packages
@base
@core

%end
