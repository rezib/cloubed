install
#nfs --server=${network.centosnet.ip_host} --dir=${domain.vmtest.tpl.nfs_ks_dir}
#url --url=http://mirror.centos.org/centos/6.4/os/x86_64/ --proxy=http://myprox.bull.fr:80
url --url=http://ftp.ciril.fr/pub/linux/centos/6.4/os/x86_64
lang en_US.UTF-8
keyboard us
network --hostname=vmtest --onboot yes --device eth0 --bootproto=static --noipv6 --ip=${domain.vmtest.tpl.ip_vm} --netmask=${network.centosnet.netmask} --gateway=${network.centosnet.ip_host} --nameserver=${network.centosnet.ip_host}
rootpw rootroot
firewall --service=ssh
authconfig --enableshadow --passalgo=sha512
selinux --enforcing
timezone --utc US/Eastern
zerombr yes
bootloader --location=mbr --driveorder=vda --append="crashkernel=auto rhgb quiet"
clearpart --all --drives=vda
autopart

poweroff

%packages
@base
@core

%end
