import re
import subprocess
import time
import psutil

from db import insert_to_db

def trace(vanilla_command, full_command, parameters, table_name, build, cwd=None, processor_number=None, skip_vanilla = False, only_vanilla = False, not_insert=False):
    if not only_vanilla:    
        # Run program and instrument it
        if not skip_vanilla:
            vanilla_process = subprocess.run(vanilla_command, capture_output=True, cwd=cwd, timeout=300)

        psutil.cpu_percent()
        full_process = subprocess.run(full_command, capture_output=True, cwd=cwd, timeout=400)
        cpu_utilization = psutil.cpu_percent(percpu=True)

        if 'child terminated' in full_process.stderr.decode('utf-8') or 'child terminated' in full_process.stdout.decode('utf-8'):
            # Throw an exception to skip this iteration
            raise Exception('Child terminated')

        full_size_process = subprocess.run(['du', 'uftrace.data'], capture_output=True, cwd=cwd, timeout=10)
        full_report_process = subprocess.run(['uftrace', 'report', '--output-fields=self,self-min,self-max,call'], capture_output=True, cwd=cwd, timeout=450)

        report = full_report_process.stdout.decode('utf-8').splitlines()[2:]
        report = [re.sub(' +', ' ', line.strip()) for line in report]

        if not skip_vanilla:
            vanilla_time = vanilla_process.stdout.decode('utf-8').rstrip().splitlines()[-3].split(":")[1].split()[0]
        full_time = full_process.stdout.decode('utf-8').rstrip().splitlines()[-3].split(":")[1].split()[0]

        print(full_process.stdout.decode('utf-8').rstrip().splitlines()[-3], build['type'], build['range'])
        full_size = int(full_size_process.stdout.decode('utf-8').split()[0])

        if 'MemoryAllocationFailed' in full_process.stderr.decode('utf-8') or 'MemoryAllocationFailed' in full_process.stdout.decode('utf-8'):
            # Throw an exception to skip this iteration
            raise Exception('MemoryAllocationFailed')

        document = {
            'build':{
                'type': build['type'],
                'range': build['range']
            },
            'stats':{
                'cpu_utilization': cpu_utilization,
                'core': processor_number
            },
            'times': {
                'vanilla': float(vanilla_time) if not skip_vanilla else None, 
                'full': float(full_time)
            },
            'sizes': {
                'full': full_size
            },
            'parameters': parameters, 
            'functions': {}
        }
        
        for r in report:
            self, _, self_min, _, self_max, _, calls, *name = r.split(' ')
            f_name = ' '.join(name)
            # if '.cpp' in f_name or 'std::' in f_name:
            #     continue

            document['functions'][f_name] = {
                'self': float(self),
                'self_min': float(self_min),
                'self_max': float(self_max),
                'calls': int(calls)
            }

        if not not_insert:
            insert_to_db(table_name, document)

    else:
        start_time = time.time()
        subprocess.run(vanilla_command, capture_output=True, cwd=cwd, timeout=20)
        end_time = time.time()

        # Calculate the elapsed time in seconds
        elapsed_time = end_time - start_time
        document = {
            'build':{
                'type': build['type'],
                'range': build['range']
            },
            'times': {
                'vanilla': elapsed_time, 
            },
            'parameters': parameters
        }

        print(elapsed_time)

        if not not_insert:
            insert_to_db(table_name, document)