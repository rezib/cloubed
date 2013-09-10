#!/bin/sh

set -e # exit as soon as error happen

OPTS="--debug"
VM="vmtest"

echo "generating template files"
cloubed $OPTS gen --domain=$VM --filename=ipxe
cloubed $OPTS gen --domain=$VM --filename=preseed
echo "booting VM $VM and waiting for shutdown"
cloubed $OPTS boot --domain=$VM --bootdev=network --overwrite-disks=yes --recreate-networks=yes --wait-event=stopped:shutdown
echo "re-booting VM $VM"
cloubed $OPTS boot --domain=$VM
