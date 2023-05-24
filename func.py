from functools import reduce


def text(param):
    output = {
        0: {
            0: 'Бесплатно',
            1: 'до 300₽',
            2: '300₽ - 700₽',
            3: '700₽ - 1000₽',
            4: '1000₽+'
            },
        1: {
            0: 'до 5',
            1: '5 - 10',
            2: '11 - 20',
            3: '21 - 30',
            4: '30+'
            },
        2: {
            0: 'Помещение',
            1: 'Улица'
        }
    }
    if sum(param) == -3:
        return None
    return reduce(lambda x, y: x + '\n' + y, [['Цена: ', 'Число людей: ', 'Тип места: '][i] + output[i][param[i]] for i in range(3) if param[i] != -1])
