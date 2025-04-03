import os

def play(file_name):
    '''audio play'''
    os.system(f'ffplay -autoexit {file_name}')