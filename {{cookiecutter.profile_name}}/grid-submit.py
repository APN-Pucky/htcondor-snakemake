#!/usr/bin/env python3

import sys
import htcondor
from os import makedirs
from os.path import join
from uuid import uuid4

from snakemake.utils import read_job_properties

import os
import shutil
import glob

# Find the latest file matching the pattern /tmp/krb5cc_$UID*
kt_files = sorted(glob.glob(f'/tmp/krb5cc_{os.getuid()}*'), key=os.path.getctime, reverse=True)
if kt_files:
    latest_kt = kt_files[0]
    shutil.copy(latest_kt, ".ticket")
else:
    print("No Kerberos ticket cache found.")

jobscript = sys.argv[1]
job_properties = read_job_properties(jobscript)

UUID = uuid4()  # random UUID
jobDir = "/home/users/REPLACETHIS/.condor_jobs/{}_{}".format(job_properties["jobid"], UUID)
makedirs(jobDir, exist_ok=True)


sub = htcondor.Submit(
    {
        "executable": jobscript,
#        "executable": "/bin/bash",
#        "arguments": jobscript,
        "transfer_input_files" : '.ticket',
#        "transfer_input_files" : '.ticket '.join(job_properties['input']),
#        "transfer_output_files" : ' '.join(job_properties['output']),
#        "should_transfer_files" : True,
#        "preserve_relative_paths" : True,
        "Requirements" : "OpSysMajorVer == 11",
        "max_retries": "5",
        "log": join(jobDir, "condor.log"),
        "output": join(jobDir, "condor.out"),
        "error": join(jobDir, "condor.err"),
        "getenv": "True",
        "request_cpus": str(job_properties["threads"]),
    }
)


request_memory = job_properties["resources"].get("mem_mb", None)
if request_memory is not None:
    sub["request_memory"] = str(request_memory)

request_disk = job_properties["resources"].get("disk_mb", None)
if request_disk is not None:
    sub["request_disk"] = str(request_disk)

schedd = htcondor.Schedd()
clusterID = schedd.submit(sub)

# print jobid for use in Snakemake
print("{}_{}_{}".format(job_properties["jobid"], UUID, clusterID))
