import os
from pathlib import Path
       
def save_metadata(file, line):
    '''
    This function will save all metadata about the process in txt file
    :param  filename: name of txt file
            line: all content
    :return none        
    '''

    if not os.path.exists(os.path.dirname(file)):
        Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True) 

    try:
        if not os.path.isfile(file):
            f = open(file, 'w')
    except OSError as error:
        print(error)     
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n')
        f.write('------------------------------------------------------' + '\n' + content)
        f.close()   