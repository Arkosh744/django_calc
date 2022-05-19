from ..models import PreparedData

'''Универсальный код'''

# Исходные данные
from calc.models import ThermalProps


# temp_ini = 30  # начальная температура
# k1 = [300, 300]  # Коэффициент теплоотдачи слева
# temp_e1 = [500, 500]  # Тепловой поток слева
# k2 = [100, 100]  # Коэффициент теплоотдачи справа
# temp_e2 = [500, 500]  # Температура ОС Справа
#
# thick = 0.1  # ширина тела, м
#
# materials = '09G2S'
#
# form = 1  # Форма тела - 0-пластина, 1 цилиндр, 2- шар
#
# points = 51  # число промежутков
# time_in_zones = [10, 60]  # время процесса
# time_step = 0.1  # шаг по времени, секунда


# Функции
def prop(T: float, list1: list) -> float:
    """Функция для определения свойств материала от температуры"""
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
    """возвращает кортеж из плотности, теплопроводности и теплоемкости при данной температуре"""
    dens = prop(T, material_data.density)
    cond = prop(T, material_data.conductivity)
    cp = prop(T, material_data.specific_heat)
    return dens, cond, cp


def iteration(tau, current_zone_time, temp, prepared_data, h, r_pos, r_posn, r_posp, current_zone, result_list):
    """Функция итерирует, на вход шаг по времени, общее время, температура по ячейкам, материал, коэффициент формы,
    размер ячейки, координаты, координаты со сдвигом минус, координаты со сдвигом плюс, коэффициент теплоотдачи и
    температура снаружи, коэффициент теплоотдачи и температуры внутри """
    point_layers = prepared_data.point_layers
    alpha = [0 for _ in range(0, prepared_data.point_layers)]
    beta = alpha[:]
    conduct = alpha[:]
    denssph = alpha[:]
    if current_zone == 0:
        res_temp = [[0, prepared_data.temp_ini, 0]]
    else:
        res_temp = [[0, result_list[-1][-1][1], result_list[-1][-1]][2]]

    timer = 0 if current_zone == 0 else result_list[-1][-1][0]

    while timer < sum(current_zone_time[:current_zone+1]):
        temp_pred = temp[:]

        delta = 1
        iterometer = 0
        timer = round((timer + tau), 2)

        while iterometer < 10 and delta > 0.001:
            iterometer += 1
            temp_s = temp[:]
            for count, i in enumerate(temp):
                dens, cond, cp = value_prop(i, prepared_data.material_data)
                conduct[count] = cond
                denssph[count] = dens * cp

            # Форма тела - 0-пластина, 1 цилиндр, 2- шар
            form = prepared_data.form
            k2 = prepared_data.k2[current_zone]
            temp_e2 = prepared_data.temp_e2[current_zone]
            if form > 0:
                alpha[0] = (tau / denssph[0] * (1 + form) * (conduct[0] + conduct[1])) / (
                        h ** 2 + tau / denssph[0] * (1 + form) * (conduct[0] + conduct[1]))
                beta[0] = (h ** 2 * temp_pred[0]) / (h ** 2 + tau / denssph[0] * (1 + form) * (conduct[0] + conduct[1]))

            else:  # граничные условия для пластины
                k1 = prepared_data.k1[current_zone]
                temp_e1 = prepared_data.temp_e1[current_zone]
                alpha[0] = (conduct[0] + conduct[1]) * tau / denssph[0] * conduct[0] / (
                        conduct[0] * h ** 2 + (conduct[0] + conduct[1]) * tau / denssph[0] * (conduct[0] + h * k1))
                beta[0] = (h ** 2 * temp_pred[0] * conduct[0] + (conduct[0] + conduct[1]) * tau / denssph[
                    0] * h * k1 * temp_e1) / (conduct[0] * h ** 2 + (conduct[0] + conduct[1]) * tau / denssph[0] * (
                        conduct[0] + h * k1))

            for i in range(1, point_layers - 1):
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

            for i in range(point_layers - 2, -1, -1):
                temp[i] = alpha[i] * temp[i + 1] + beta[i]

            delta = max([abs(temp[i] - temp_s[i]) for i in range(0, point_layers)]) / max(temp)
        temp_medium1 = temp[0] * (r_posp[0]) ** (form + 1) + temp[-1] * \
                       (r_pos[-1] ** (form + 1) - (r_posn[-1] ** (form + 1)))

        temp_medium2 = sum([temp[i] * (r_posp[i] ** (form + 1) - r_posn[i] ** (form + 1))
                            for i in range(1, point_layers - 1)])
        temp_medium = (temp_medium2 + temp_medium1) / (prepared_data.thickness /1000) ** (form + 1)
        vel_temp = (temp_medium - float(res_temp[-1][1])) / tau
        res_temp.append([timer, temp_medium, vel_temp])

    return temp, res_temp


def main(prepared_data: PreparedData):
    h = (prepared_data.thickness / 1000) / (prepared_data.point_layers - 1)  # Шаг по сетке
    r_pos = [h * i for i in range(0, prepared_data.point_layers)]
    r_posn = [i - h / 2 for i in r_pos]
    r_posp = [i + h / 2 for i in r_pos]
    result_temp = list()
    result_list = list()
    temp = [prepared_data.temp_ini for _ in range(0, prepared_data.point_layers)]
    for current_zone, current_zone_time in enumerate(prepared_data.time_in_zones):
        nn = current_zone_time // prepared_data.time_step  # Сколько итераций
        tau = current_zone_time / nn  # Временной шаг
        temp, res = iteration(tau, prepared_data.time_in_zones, temp, prepared_data,
                              h, r_pos, r_posn, r_posp, current_zone, result_list)
        # И это искомые результаты. их куда то выводить.
        result_temp += [temp[:]]
        result_list += [res[:]]
    return {'result_temp': result_temp, 'result_list': result_list, 'thickness_points': r_pos}
