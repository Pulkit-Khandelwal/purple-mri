import sys
import subprocess

arg1 = sys.argv[1]
arg2 = sys.argv[2]
arg3 = sys.argv[3]
arg4 = sys.argv[4]
arg5 = sys.argv[5]
arg6 = int(sys.argv[6])
arg7 = sys.argv[7]

subprocess.run("bash run_surface_pipeline.sh %s %s %s %s %s %s %s" \
                      % (arg1, arg2, arg3, arg4, arg5, arg6, arg7), shell=True)
