MPIRUN WRAPPER
==============
This script generates a command line for MPIRUN and executes this command line. Optionally, the script is able to just perform a dry-run printing the generated command line. Other solutions may generate host files describing the execution to be performed by MPIRUN. However, this script generates a command line to be executed on the login/head node of the cluster. There are various flags to adjust and tune the behavior.

The main purpose of this work is to ease tuning the execution on systems with Intel Xeon Phi coprocessors (an instance of the Intel Many Integrated Core Architecture "MIC"). The script supports both major usage models of Intel Xeon Phi: (1) running MPI ranks directly on the coprocessors a.k.a. symmetric usage model, and (2) running MPI ranks only on the host systems where the ranks may offload work to the attached coprocessors.

Example
=======
You should be able to successfully run `mpirun.sh -h`. If this is not the case, please have a look at the "Troubleshooting" section (see below). The MPIRUN script is independent of a particular application but for the matter of a specific example, one may run [Quantum Espresso](http://quantum-espresso.org/) (see also [here](https://github.com/cdahnken/libxphi)) using four ranks per socket:

```sh
mpirun.sh -p4 \
  -w /path/to/xphilibwrapper.sh \
  -x /path/to/pw.x \
  -z -i input-file.in
```

The above assumes 'mpirun.sh' and 'mpirun.py' to be reachable as well as the runtime environment ready for execution (compiler runtime, and other dependencies). The Shell script further relies on the 'micinfo' tool to introspect the system hardware. The latter allows for example to avoid using multiple host sockets in case there is only one coprocessor attached to a dual-socket node (avoids to perform data transfers from/to a “remote” coprocessor). Any default provided by the launcher script “mpirun.sh” can be overridden on the command line (still being able to leverage all the other defaults).

Instructions
============
To receive the command line help of the script:

```sh
mpirun.sh -h
```

In fact, there are currently two scripts 'mpirun.sh' and 'mpirun.py' where the Shell script provides defaults for the many options of 'mpirun.py'. Here is the detailed command line help:

```
usage: mpirun.py [-h] [-n NODELIST] [-p CPUPROCS] [-q MICPROCS] [-s NSOCKETS]
                 [-d NDEVICES] [-e CPUCORES] [-t NTHREADS] [-m MICCORES]
                 [-r RESERVED] [-u MTHREADS] [-a CPUAFFINITY] [-b MICAFFINITY]
                 [-c SCHEDULE] [-w WRAPPER] [-g DEBUGGER] [-i INPUTFILE]
                 [-0 HR0] [-x HRI] [-y MRI] [-z] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -n NODELIST, --nodelist NODELIST
                        list of comma separated node names
  -p CPUPROCS, --cpuprocs CPUPROCS
                        number of processes per socket (host)
  -q MICPROCS, --micprocs MICPROCS
                        number of processes per mic (native)
  -s NSOCKETS, --nsockets NSOCKETS
                        number of sockets per node
  -d NDEVICES, --ndevices NDEVICES
                        number of devices per node
  -e CPUCORES, --cpucores CPUCORES
                        number of CPU cores per socket
  -t NTHREADS, --nthreads NTHREADS
                        number of CPU threads per core
  -m MICCORES, --miccores MICCORES
                        number of MIC cores per device
  -r RESERVED, --reserved RESERVED
                        number of MIC cores reserved
  -u MTHREADS, --mthreads MTHREADS
                        number of MIC threads per core
  -a CPUAFFINITY, --cpuaffinity CPUAFFINITY
                        affinity (CPU) e.g., compact
  -b MICAFFINITY, --micaffinity MICAFFINITY
                        affinity (MIC) e.g., balanced
  -c SCHEDULE, --schedule SCHEDULE
                        schedule, e.g. dynamic
  -w WRAPPER, --wrapper WRAPPER
                        wrapper
  -g DEBUGGER, --debugger DEBUGGER
                        debugger
  -i INPUTFILE, --inputfile INPUTFILE
                        inputfile (<)
  -0 HR0, --hr0 HR0     executable (rank-0)
  -x HRI, --hri HRI     executable (host)
  -y MRI, --mri MRI     executable (mic)
  -z, --micpre          prefixed mic name
  -v, --dryrun          dryrun
```

Any argument passed at the end of the command line is simply forwarded to the next underlying mechanism if not consumed by the option processing. If it is needed to pass arguments to the executable using '<', one can use the script’s '-i' option, otherwise options for the executable can be simply appended to the command line.

More Details
============
In case of using the offload model, each coprocessor is partitioned according to the host ranks driving that coprocessor. Partitioning the coprocessors leverages the advantages of multi-processing vs. multi-threading even when using the offload model. It is somewhat similar to running MPI ranks on the coprocessor (a.k.a. symmetric usage model) although the MPI ranks are only on the host.

Partitioning the set of threads on each coprocessor into independent sets of threads is achieved by using Intel's KMP_PLACE_THREADS environment variable; an explicit PROCLIST may serve a similar purpose. In addition, the environment variable OFFLOAD_DEVICES allows to utilize multiple coprocessors within the same system.

The script allows to leverage MPI ranks on the host even for the offload model by trading (implicit) barriers at the end of OpenMP* parallel regions against independent executions.

Troubleshooting
===============
This section provides an assorted collection of issues and the typical resolution.

* By default, Python 2.6 does not provide the "argparse" module. To install the necessary bits as an ordinary user with no Internet access a.k.a. offline installation, download [ez_setup.py](https://bootstrap.pypa.io/ez_setup.py) ("easy_install") as well as the [argparse module](https://pypi.python.org/packages/source/a/argparse/) to a system with Internet access. Copy the files into a directory accessible for the cluster, and run `/path/to/ez_setup.py --download-base=/path/to/setuptools-7.0.zip --user` followed by `~/.local/bin/easy_install /path/to/argparse-x.y.z.tar.gz`.
* In a cluster environment, the coprocessors are typically named using the host's host name as a prefix e.g., 'hostname-mic0' (rather than 'mic0'). This naming convention makes absolutely sense in order to address each of the coprocessors as an individual cluster node (symmetric usage model), and with the script's '-z' option this behavior can be easily reproduced. Of course, using the offload model in such a cluster installation still requires the prefixed coprocessor names.
