import string
from concurrent.futures import ProcessPoolExecutor
from hashlib import md5
from itertools import islice, product
from multiprocessing import Value, RLock
from time import time
from tqdm import tqdm

PROCESSES = 6
CHARS = string.ascii_lowercase + string.digits
PASSWORD_LENGHT = 6


def hashing_pass(word):
    hashed_word = md5(word.encode()).hexdigest()
    return hashed_word


def generate_pass(chars, start, end):
    return ("".join(i) for i in islice(product(chars, repeat=6), start, end))


def brute_force(hashes_list, chars, start, end):
    global shared_int
    pbar = tqdm(total=shared_int.value, dynamic_ncols=True)

    gen_pass = generate_pass(chars, start, end)
    for i in range(start, end):
        try:
            password = next(gen_pass)
        except StopIteration:
            return
        brute_pass = hashing_pass(password)
        if brute_pass in hashes_list:
            result = hashes_list.pop(hashes_list.index(brute_pass))
            with shared_int.get_lock():
                shared_int.value -= 1 
            print(f'password:{password}, hash: {result}')
        # это условие нужно, что бы скрипт не проверял расшаренную переменную 
        # при каждом проходе, т.к. иначе скорость работы сильно снижается
        if i % 1000000 == 0:
            if shared_int.value == 0:
                return
        pbar.update(1)


if __name__ == '__main__':
    batch_size = (len(CHARS)**PASSWORD_LENGHT)//PROCESSES

    hashes_list = ['3bd0a32f99a0185c8a8f4af9ccff90ae',
                   '8bad66e16b191a1f779f4c9f9f0955ea',
                   '6467b3d4f0176029b582280342c83d33']

    shared_int = Value('i', len(hashes_list))
    with ProcessPoolExecutor(max_workers=PROCESSES) as executor:
        dataset = [[hashes_list, CHARS, x*batch_size,
                    (x+1)*batch_size] for x in range(PROCESSES)]
        futures = [executor.submit(brute_force, *params) for params in dataset]
        result_list = [future.result() for future in futures]