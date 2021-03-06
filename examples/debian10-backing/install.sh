#!/bin/sh

set -e # exit as soon as error happen

OPTS="--debug"
VM="base"

echo "generating template files"
cloubed $OPTS gen --domain=$VM --filename=ipxe
cloubed $OPTS gen --domain=$VM --filename=preseed
echo "booting VM $VM"
cloubed $OPTS boot --domain=$VM --bootdev=network --overwrite-disks=yes --recreate-networks=yes
echo "waiting VM $VM for shutdown"
cloubed $OPTS wait --domain=$VM --event=stopped:shutdown --enable-http

VM="test"
echo "booting VM $VM (with volume backing)"
cloubed $OPTS boot --domain=$VM --overwrite-disks yes
