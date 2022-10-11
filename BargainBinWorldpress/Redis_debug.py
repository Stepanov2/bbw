# redis-10989.c135.eu-central-1-1.ec2.cloud.redislabs.com


import redis
import json

with redis.Redis(
    host='redis-10989.c135.eu-central-1-1.ec2.cloud.redislabs.com',
    port=10989,
    password='LrTgACYU5LM7G73cmILlm8gboTS2bwD2'
) as red:
    #red.set('vasya_pupkin_', '89261234567')  # записываем в кеш строку "value1"
    #red.set('petya_zalupkin_', '89261230567')
    # red.set('var1', 'value1')  # записываем в кеш строку "value1"
    # red.set('var2', 'value2')
    # print(red.keys())
    # print(red.delete(red.keys()[0]))  # считываем из кеша данные

    #quit()
    while True:
        commands=['sto', 'retr', 'quit', 'list', 'del']
        inputstring = input("Enter your command")
        inputs = inputstring.split(' ')
        inputs[0] = inputs[0].lower()
        if not inputs[0] in commands:
            print(f'Valid commands are {commands}')
            continue

        if inputs[0] == 'quit':
            print('Bye!')
            break

        if inputs[0] == 'list':
            if not red.keys():
                print('Forever alone!')
                continue
            for key in red.keys():
                print(f'{json.loads(red.get(key))}')
            continue

        if inputs[0] == 'retr':
            request = '_'.join(map(lambda s: s.lower(), inputs[1:]))

            person = red.get(request)
            # print(person, type(person))

            if person:
                print(json.loads(person))
            else:
                print(f'{request} is not in cache')
            continue

        if inputs[0] == 'sto':
            person = {(' '.join(inputs[1:-1])):inputs[-1]}
            result = red.set('_'.join(map(lambda s: s.lower(), inputs[1:-1])),
                             json.dumps(person))
            if result: print(f'Successfully made an entry'); print(json.dumps(person))
            else: print('Try again')
            continue
        if inputs[0] == 'del':
            result = red.delete('_'.join(map(lambda s: s.lower(), inputs[1:])))
            if result: print(f'You are no longer friends with {inputs[1:]}')
            else: print(f'No such guy!')
            continue


# retr vasya pupkin