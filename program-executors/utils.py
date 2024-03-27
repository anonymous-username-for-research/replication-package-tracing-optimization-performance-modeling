import re

def convert_file_size(size_in_kb):
    for unit in ['KB', 'MB', 'GB', 'TB']:
        if size_in_kb < 1024 or unit == 'TB':
            return f"{size_in_kb:.2f} {unit}"
        size_in_kb /= 1024

def get_element_texts(element):
    if element is None:
        return ''
    return re.sub(' +', ' ', ''.join(element.itertext()).strip().replace('\n', '').replace('\t', ''))