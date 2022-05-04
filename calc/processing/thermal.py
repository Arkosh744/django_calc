'''Универсальный код'''


# Исходные данные
from calc.models import ThermalProps

temp_ini = 30  # начальная температура
k1 = [300, 300]  # Коэффициент теплоотдачи слева
temp_e1 = [500, 500]  # Тепловой поток слева
k2 = [100, 100]  # Коэффициент теплоотдачи справа
temp_e2 = [500, 500]  # Температура ОС Справа

thick = 0.1  # ширина тела, м

materials = '09G2S'

form = 1  # Форма тела - 0-пластина, 1 цилиндр, 2- шар

points = 51  # число промежутков
time_in_zones = [10, 60]  # время процесса
time_step = 0.1  # шаг по времени, секунда


# Функции
def prop(T: float, list1: list) -> float:
    '''функция для определения свойств материала от температуры'''
    # функция на вход получает список величин и Температуру

    # Проверка вхождения в массив, если не входит, то возвращает крайние значения
    if T >= list1[0][0]:
        return list1[0][1]
    if T <= list1[len(list1) - 1][0]:
        return list1[len(list1) - 1][1]

    # Поиск нужного значения

    # Иницианизация начальных значений индекса
    index_begin = 0
    index_end = len(list1) - 1

    while True:
        search_index = (index_end + index_begin) // 2
        if list1[search_index][0] < T:
            index_end = search_index
        elif list1[search_index + 1][0] > T:
            index_begin = search_index
        elif list1[search_index + 1][0] == T:
            return list1[search_index][1]
        else:
            dT = list1[search_index][0] - list1[search_index + 1][0]
            dF = list1[search_index][1] - list1[search_index + 1][1]
            return list1[search_index][1] + (T - list1[search_index][0]) * dF / dT


def value_prop(T: float, material_data: ThermalProps):
    '''возвращает кортеж из плотности, теплопроводности и теплоемкости при данной температуре'''
    dens = prop(T, material_data.density)
    cond = prop(T, material_data.conductivity)
    cp = prop(T, material_data.specific_heat)
    return dens, cond, cp


def iteration(tau, current_zone_time, temp, material_data, form, h, r_pos, r_posn, r_posp, k2, temp_e2, k1=0, temp_e1=0):
    '''функция итерирует, на вход шаг по времени, общее время, температура по ячейкам, материал, коэффициент формы, размер ячейки, координаты, координаты со сдвигом минус,
    координаты со сдвигом плюс, коэффициент теплоотдачи и температура снаружи, коэффициент теплоотдачи и температуры внутри'''
    timer = 0
    alpha = [0 for i in range(0, points)]
    beta = alpha[:]
    conduct = alpha[:]
    denssph = alpha[:]
    res_temp = [['0', str(temp_ini), '0']]  # результирующий массив время - температура - скорость охлаждения

    while timer < current_zone_time:
        timer += tau
        temp_pred = temp[:]

        for iterometer in range(0, 10):
            temp_s = temp[:]
            for count, i in enumerate(temp):
                dens, cond, cp = value_prop(i, material_data)
                conduct[count] = cond
                denssph[count] = dens * cp

            # Форма тела - 1-пластина, 2 цилиндр, 3- шар
            if form > 1:
                alpha[0] = (tau / denssph[0] * (1 + form) * (conduct[0] + conduct[1])) / (
                            h ** 2 + tau / denssph[0] * (1 + form) * (conduct[0] + conduct[1]))
                beta[0] = (h ** 2 * temp_pred[0]) / (h ** 2 + tau / denssph[0] * (1 + form) * (conduct[0] + conduct[1]))

            else:  # граничные условия для пластины
                alpha[0] = (conduct[0] + conduct[1]) * tau / denssph[0] * conduct[0] / (
                            conduct[0] * h ** 2 + (conduct[0] + conduct[1]) * tau / denssph[0] * (conduct[0] + h * k1))
                beta[0] = (h ** 2 * temp_pred[0] * conduct[0] + (conduct[0] + conduct[1]) * tau / denssph[
                    0] * h * k1 * temp_e1) / (conduct[0] * h ** 2 + (conduct[0] + conduct[1]) * tau / denssph[0] * (
                            conduct[0] + h * k1))

            for i in range(1, points - 1):
                ai = tau / denssph[i] / r_pos[i] ** form / h ** 2 * r_posp[i] ** form * (
                            conduct[i] + conduct[i + 1]) / 2
                ci = tau / denssph[i] / r_pos[i] ** form / h ** 2 * r_posn[i] ** form * (
                            conduct[i] + conduct[i - 1]) / 2
                bi = ai + ci + 1
                fi = -temp_pred[i]
                alpha[i] = ai / (bi - ci * alpha[i - 1])
                beta[i] = (ci * beta[i - 1] - fi) / (bi - ci * alpha[i - 1])

            multi_a = (conduct[-2] + conduct[-1]) * tau / denssph[-1]
            temp[-1] = (conduct[-1] * h ** 2 * temp_pred[-1] + multi_a * (
                        conduct[-1] * beta[-2] + h * k2 * temp_e2)) / (
                                   conduct[-1] * h ** 2 + multi_a * (h * k2 + conduct[-1] * (1 - alpha[-2])))
            for i in range(points - 2, -1, -1):
                temp[i] = alpha[i] * temp[i + 1] + beta[i]

            delta = max([abs(temp[i] - temp_s[i]) for i in range(0, points)]) / max(temp)

            if delta < 0.001:
                break

            temp_medium1 = temp[0] * (r_posp[0]) ** (form + 1) + temp[-1] * (
                        r_pos[-1] ** (form + 1) - (r_posn[-1] ** (form + 1)))
            temp_medium2 = sum(
                [temp[i] * (r_posp[i] ** (form + 1) - r_posn[i] ** (form + 1)) for i in range(1, points - 1)])
            temp_medium = (temp_medium2 + temp_medium1) / thick ** (form + 1)
            vel_temp = (temp_medium - float(res_temp[-1][1])) / tau

            res_temp.append([str(timer), str(temp_medium), str(vel_temp)])
        return temp, res_temp


def main(thickness, point_layers, temp_ini, material_data, form, time_in_zones, time_step, k2, temp_e2, k1=0, temp_e1=0):

    h = thickness / (point_layers - 1)  # Шаг по сетке

    r_pos = [h * i for i in range(0, point_layers)]
    r_posn = [i - h / 2 for i in r_pos]
    r_posp = [i + h / 2 for i in r_pos]

    temp = [temp_ini for _ in range(0, point_layers)]
    for current_zone, current_zone_time in enumerate(time_in_zones):
        nn = current_zone_time // time_step  # Сколько итераций
        tau = time_in_zones / nn  # Временной шаг
        # temp, res = iteration(temp, r_pos, r_posn, r_posp, tau, h, form, k2, temp_e2, k1, temp_e1)
        if k1 == 0 and temp_e1 == 0:
            temp, res = iteration(tau, current_zone_time, temp, material_data, form, h,
                                  r_pos, r_posn, r_posp, k2[current_zone], temp_e2[current_zone], k1, temp_e1)

        elif type(k1) == list and type(temp_e1) == list:
            temp, res = iteration(tau, current_zone_time, temp, material_data, form, h,
                                  r_pos, r_posn, r_posp, k2[current_zone], temp_e2[current_zone],
                                  k1[current_zone], temp_e1[current_zone])
        # И это искомые результаты. их куда то выводить.
        print(temp)
        print(res)

for time1 in time_in_zones:
    print(time1)