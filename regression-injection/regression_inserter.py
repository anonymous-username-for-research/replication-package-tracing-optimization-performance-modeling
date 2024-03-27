import argparse
import re
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
import json
import os

from utils import get_element_texts

base_path = Path(__file__).parent.resolve()

blocks_specs = {
    'io': {'srand': True},
    'const_delay': {'srand': False},
    'calculations': {'srand': False},

    'const_delay_cpp': {'srand': False},
    'calculations_cpp': {'srand': False}
}

valid_blocks = list(blocks_specs.keys())

def get_code_blocks():
    blocks = {}
    for ext in ['*.cpp', '*.cxx', '*.cc', '*.c']:
        for p in Path((base_path / './code_blocks').resolve()).rglob(ext):
            with open(p) as f:
                lines = f.readlines()

            if len(lines) == 0 or (p.stem not in valid_blocks and p.stem != 'srand'):
                continue

            libraries = [re.search('<(.*)>', line).group(1)
                        for line in lines if line.startswith('#include')]
            codes = [line for line in lines if not line.startswith(
                '#include') and not line.strip() == '']

            path = (base_path / str('./code_blocks/temp_code' + p.suffix)).resolve()
            try:
                with open(path, 'w') as tmp:
                    tmp.write(''.join(codes))
                    tmp.flush()

                    process = subprocess.run(['srcml', path], capture_output=True)
                    xml = re.sub('xmlns="[^"]+"', '',
                                process.stdout.decode('utf-8'), count=1)
            finally:
                os.remove(path)

            blocks[p.stem + '_' + p.suffix[1:]] = {
                'libraries': libraries,
                'code': xml
            }

    return blocks

def run_program(program, skip_build=False):
    print('-' * 50)
    
    if not skip_build:
        if program.startswith('6'):
            subprocess.run(['SPEC_PATH_HERE/bin/runcpu',
                    '--config=custom-gcc.cfg', '--action=clobber', '-tune=base',
                    '--size=test', program], capture_output=True)
        
        if 'freqmine' in program:
            subprocess.run(['PARSEC_PATH_HERE/bin/parsecmgmt',
                    '-a', 'uninstall', '-p', program], capture_output=True)
            
        if 'su2' in program:
            subprocess.run(['./ninja', '-C', 'build', 'clean'],
                           cwd='SU2_PATH_HERE',capture_output=True)
        
        print('Finished clobbering')
        
        if program.startswith('6'):
            subprocess.run(['SPEC_PATH_HERE/bin/runcpu',
                            '--config=custom-gcc.cfg', '--action=build',
                            '--size=test', '--iterations=1', '--noreportable', '-output_format=text',
                            program], capture_output=True)
        
        if 'freqmine' in program:
            subprocess.run(['PARSEC_PATH_HERE/bin/parsecmgmt',
                        '-a', 'build', '-p', program], capture_output=True)
            
        if 'su2' in program:
            subprocess.run(['./ninja', '-C', 'build', 'install'],
                           cwd='SU2_PATH_HERE',capture_output=False)
        
        print('Finished building')

    print('SUCCESS')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('blocks', type=str, help='Comma separated list of blocks')
    parser.add_argument('program_name', type=str, help='Program name')
    parser.add_argument('input_directory', type=str, help='Input directory')
    parser.add_argument('--range', type=str, help='Range of function to insert')
    parser.add_argument('--reset', action=argparse.BooleanOptionalAction, help='Reset the source code to the original version')
    parser.add_argument('--no_build', action=argparse.BooleanOptionalAction, help='Do not build the program after inserting the blocks')
    args = parser.parse_args()

    designated_blocks = args.blocks.split(',')
    if any([block not in valid_blocks for block in designated_blocks]):
        print("Invalid block. You should choose from: " + ', '.join(valid_blocks))
        exit(1)

    input_directory = args.input_directory
    if not Path(input_directory).is_dir():
        print("Input directory does not exist")
        exit(1)

    code_blocks = get_code_blocks()
    library_base = re.sub('xmlns="[^"]+"', '', '<unit xmlns="http://www.srcML.org/srcML/src" xmlns:cpp="http://www.srcML.org/srcML/cpp" revision="1.0.0" language="C" filename="c.c"><cpp:include>#<cpp:directive>include</cpp:directive> <cpp:file>&lt;PUT_HERE&gt;</cpp:file></cpp:include>\n</unit>\n', count=1)

    for backup_ext in ['*.backup.cpp', '*.backup.cxx', '*.backup.cc', '*.backup.c']:
        for p in Path(input_directory).rglob(backup_ext):
            os.remove(str(p).replace('.backup.' + p.suffix[1:], ''))
            os.rename(p, str(p).replace('.backup.' + p.suffix[1:], ''))

    # Check if --no-build is provided
    skip_build = args.no_build

    # Read target functions json (absolute path)
    with open((base_path / 'target_functions.json').resolve()) as f:
        target_functions = json.load(f)

    # Read program's regression specifications
    with open((base_path / 'regression_specs.json').resolve()) as f:
        regression_specs = json.load(f)

    # Check whether the program name is valid
    if args.program_name not in list(target_functions.keys()):
        print("Invalid program name. You should choose from: " + ', '.join(list(target_functions.keys())))
        exit(1)

    # Check whether the range provided and is valid
    if args.range is None:
        print("Invalid range. You should choose from: " + ', '.join(list(target_functions[args.program_name].keys())))
        exit(1)

    target_function = target_functions[args.program_name][args.range.split('-')[0]][int(args.range.split('-')[1])]['function']
    target_function_calls = target_functions[args.program_name][args.range.split('-')[0]][int(args.range.split('-')[1])]['calls']

    # Check if arg --reset is provided
    if args.reset:
        run_program(program=args.program_name, skip_build=skip_build)
        exit(0)

    affected = False
    for ext in ['*.cpp', '*.c']:
        if affected == True:
            break

        for p in Path(input_directory).rglob(ext):
            process = subprocess.run(
                ['srcml', p], capture_output=True)  # Run srcml on file
            xml = process.stdout.decode('utf-8')
            xml = re.sub('xmlns="[^"]+"', '', xml, count=1)  # Remove namespace

            root = ET.fromstring(xml)
            added_libraries = []
            for block in designated_blocks:
                for library in code_blocks[f'{block}_{p.suffix[1:]}']['libraries']:
                    if f'<{library}>' not in get_element_texts(root) and library not in added_libraries:
                        root.insert(0, ET.fromstring(library_base.replace('PUT_HERE', library)).find(
                            '{http://www.srcML.org/srcML/cpp}include'))
                        added_libraries.append(library)

            for function in root.findall('.//function'):
                function_name = get_element_texts(function.find('name'))

                if function_name != target_function:
                    continue

                print(f'Processing {function_name} in {p.stem}')

                # Get the first block element in the function
                if function.find('block') is None or function.find('block').find('block_content') is None:
                    continue

                block = function.find('block').find('block_content')

                # Designated bocks = ['io', 'const_delay', 'calculations']
                for designated_block in designated_blocks:
                    if function_name == target_function:
                        # Code block = code of the designated block, e.g. io
                        code_block = code_blocks[f'{designated_block}_{p.suffix[1:]}']['code']
                        
                        value_to_add = regression_specs[args.program_name][designated_block][args.range.split('-')[0]]
                        code_block = code_block.replace('VALUE_TO_ADD_HERE', str(value_to_add))
                        xml_block = ET.fromstring(code_block)
                        items = xml_block.findall('*')
                        # Reverse the items
                        items.reverse()
                        # Insert the items before the first block element
                        for item in items:
                            block.insert(0, item)

                affected = True
                break

            if affected:
                ET.ElementTree(root).write('output.xml')
                os.rename(p, str(p) + '.backup.' + p.suffix[1:])
                subprocess.run(['srcml', 'output.xml', '-o', str(p)])
                break

    # Remove output.xml
    if Path('output.xml').is_file():
        os.remove('output.xml')

    run_program(program=args.program_name, skip_build=skip_build)