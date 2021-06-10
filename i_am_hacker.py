import string
from concurrent.futures import ProcessPoolExecutor
from hashlib import md5
from itertools import islice, product
from multiprocessing import Value
from tqdm import tqdm

#самый оптимальный вариант 4 процесса при четырёх ядерном компьютере
PROCESSES = 10
CHARS = string.ascii_lowercase + string.digits
PASSWORD_LENGHT = 6
hast_set = {'3bd0a32f99a0185c8a8f4af9ccff90ae',
                '8bad66e16b191a1f779f4c9f9f0955ea',
                '6467b3d4f0176029b582280342c83d33'}


def hashing_pass(word):
    hashed_word = md5(word.encode()).hexdigest()
    return hashed_word


def generate_pass(chars, start, end):
    return (''.join(i) for i in islice(product(chars, repeat=6), start, end))


def brute_force(hast_set, chars, start, end):
    pbar = tqdm(total=shared_int.value, dynamic_ncols=True)

    gen_pass = generate_pass(chars, start, end)
    for i in range(start, end):
        try:
            password = next(gen_pass)
        except StopIteration:
            return
        brute_pass = hashing_pass(password)
        if brute_pass in hast_set:
            
            with shared_int.get_lock():
                shared_int.value -= 1
                progress.value += 1
                pbar.update(progress.value)
            print(f'password:{password}, hash: {brute_pass}')
        # это условие нужно, что бы скрипт не проверял расшаренную переменную 
        # при каждом проходе, т.к. иначе скорость работы сильно снижается
        if i % 10000000 == 0:
            if shared_int.value == 0:
                return

def init(arg1, arg2):
    global shared_int, progress
    shared_int = arg1
    progress = arg2
    

if __name__ == '__main__':
    batch_size = (len(CHARS)**PASSWORD_LENGHT)//PROCESSES
    shared_int = Value('i', len(hast_set))
    progress = Value('i', 0)
    with ProcessPoolExecutor(max_workers=PROCESSES, initializer=init, initargs=(shared_int, progress)) as executor:
        dataset = [[hast_set, CHARS, x*batch_size,
                    (x+1)*batch_size] for x in range(PROCESSES)]
        futures = [executor.submit(brute_force, *params) for params in dataset]
        result_list = [future.result() for future in futures]