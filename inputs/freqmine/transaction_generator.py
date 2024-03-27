import os
import random
from random import randint

def generate_transactions(number_of_inputs):
    output_directory = f'./inputs/freqmine'
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for file in os.listdir(output_directory):
        os.remove(f'{output_directory}/{file}')

    # Generate the transactions
    options = {
        'min_items': list(range(2, 601, 4)),
        'max_items': list(range(6000, 7501, 250)),
        'num_items': list(range(20, 51, 5)),
        'num_transactions': list(range(10000, 100001, 5000))
    }

    for file_number in range(number_of_inputs):
        transactions = []
        for _ in range(random.randint(1000, random.choice(options['num_transactions']))):
            items = set()
            while len(items) < randint(1, random.choice(options['num_items'])):
                items.add(randint(random.choice(options['min_items']), random.choice(options['max_items'])))
            transactions.append(list(items))

        support = random.randint(2, 18)

        # Write the transactions to a file (i.e., build directory)
        with open(f'{output_directory}/input_{file_number}_{support}.dat', "w") as f:
            for items in transactions:
                line = " ".join(str(i) for i in items)
                f.write(line + "\n")

if __name__ == '__main__':
    number_of_inputs = 25000
    generate_transactions(number_of_inputs)