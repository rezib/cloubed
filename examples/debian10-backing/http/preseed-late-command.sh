#!/bin/bash

# add console parameters to linux kernel
sed -i 's/GRUB_CMDLINE_LINUX=""/GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,9600n8"/' /etc/default/grub
update-grub

# root ssh pubkey
mkdir -p --mode=0750 /root/.ssh
cat <<EOF >/root/.ssh/authorized_keys
<put your own pub key here>
EOF
chmod 0640 /root/.ssh/authorized_keys

# These steps are needed in backing image in order to let other VM to set their
# hostnames with DHCP client
echo localhost >/etc/hostname
#echo unset old_host_name >/etc/dhcp/dhclient-enter-hooks.d/unset_old_hostname

# sources:
#  http://askubuntu.com/questions/104918/how-to-get-hostname-from-dhcp-server
#  http://nullcore.wordpress.com/2011/12/09/setting-the-system-hostname-from-dhcp-in-ubuntu-11-10/

cat <<EOF >/etc/dhcp/dhclient-exit-hooks.d/hostname
#!/bin/sh
# Filename:     /etc/dhcp/dhclient-exit-hooks.d/hostname
# Purpose:      Used by dhclient-script to set the hostname of the system
#               to match the DNS information for the host as provided by
#               DHCP.
#


# Do not update hostname for virtual machine IP assignments
if [ "\$interface" != "eth0" ] && [ "\$interface" != "wlan0" ]
then
    return
fi


if [ "\$reason" != BOUND ] && [ "\$reason" != RENEW ] \
   && [ "\$reason" != REBIND ] && [ "\$reason" != REBOOT ]
then
        return
fi

echo dhclient-exit-hooks.d/hostname: Dynamic IP address = \$new_ip_address
hostname=\$(host \$new_ip_address | cut -d ' ' -f 5)
echo \$hostname > /etc/hostname
hostname \$hostname
echo dhclient-exit-hooks.d/hostname: Dynamic Hostname = \$hostname
EOF

chmod a+r /etc/dhcp/dhclient-exit-hooks.d/hostname

