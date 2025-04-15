import time
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor

def get_process_ids(keyword):
    """Get PID of processes that contains target keyword"""
    try:
        ps_output = subprocess.check_output(['jps']).decode('utf-8')
        
        process_lines = [line for line in ps_output.splitlines() if keyword in line]
        
        process_ids = [line.split()[0] for line in process_lines]
        
        return process_ids
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while getting process IDs: {e}")
        return []

def run_asprof(asprof_bin, outdir, process_id, duration=30, event='cpu'):
    """Use asprof tool to sample. Check https://github.com/async-profiler/async-profiler """
    try:
        output_file = outdir + f"/flamegraph_{process_id}.html"
        command = [asprof_bin, 'start', '-e', event, '--all-user', '--cstack', 'dwarf', process_id]
        stop_command = [asprof_bin, 'stop', '-f', output_file, process_id]
        
        
        subprocess.run(command, check=True)
        print(f"Sampling started for process {process_id}. Output will be saved to {output_file}")
        time.sleep(duration)
        
        # 停止采样
        subprocess.run(stop_command, check=True)
        print(f"Sampling completed for process {process_id}. Output saved to {output_file}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running asprof for process {process_id}: {e}")

def main(keyword):    
    process_ids = get_process_ids(keyword)
    
    if not process_ids:
        print(f"No processes found containing the keyword '{keyword}'")
        return
    
    max_processes = 1
    selected_process_ids = process_ids[:max_processes]
    asprof_bin='/root/setup-flash-task/async-profiler-3.0-linux-x64/bin/asprof'
    with ThreadPoolExecutor(max_workers=max_processes) as executor:
        futures = [executor.submit(run_asprof, asprof_bin, "/mnt/disk2/corefile", pid) for pid in selected_process_ids]
        
        for future in futures:
            future.result()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python profile_processes_concurrent.py <keyword>")
        sys.exit(1)
    
    keyword = sys.argv[1]
    main(keyword)
 # type: ignore