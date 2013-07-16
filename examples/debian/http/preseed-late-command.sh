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
