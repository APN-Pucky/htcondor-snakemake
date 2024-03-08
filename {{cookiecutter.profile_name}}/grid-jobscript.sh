#!/bin/bash
# properties = {properties}

set -e

F=/tmp/krb5cc_${{UID}}_$(cat /proc/sys/kernel/random/uuid | sed 's/[-]//g' | head -c 5)
cp .ticket $F

echo "hostname:"
hostname -f
#source /home_NFS/users/REPALCETHIS/gentoo/startprefix
source /home_NFS/users/REPALCETHIS/snakemake/snek/bin/activate

{exec_job}
