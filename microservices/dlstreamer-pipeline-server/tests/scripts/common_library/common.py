import os
import subprocess

current_dir = os.getcwd()

RUNNING_STATUS = "running"
#if open_edge_Repo true 
repo_path = current_dir + "/../../../../../"

hostIP = subprocess.check_output("ip route get 1 | awk '{print $7}'|head -1", shell=True)
hostip = str(str(hostIP, 'utf-8').split("\n")[0])
