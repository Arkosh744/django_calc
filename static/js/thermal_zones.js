const zones_select = document.getElementById("id_number_of_zones");
const thickness_input = '<input type="text" name="thickness" value="30" class="form-control form-control-small" ' +
    'required="" id="id_thickness">'

const initial_time = $('#table-zones-time tbody tr:first-child')
const t1 = initial_time[0]
const initial_coef = $('#table-zones-coef tbody tr:first-child')
const t2 = initial_coef[0]

const temp_bottom = '<th class="td-zone">Температура поверхности, сек</th>'
const temp_bottom_input = '<td><input type="text" name="zone_temp_bottom" value="150" class="form-control form-control-small" required="" id="id_zone_temp_bottom"></td>'

const coef_bottom = '<th class="td-zone">Коэф. теплопередачи с поверхностью, Вт/м²К</th>'
const coef_bottom_input = '<td><input type="text" name="zone_thermal_coef_bottom" value="1500" class="form-control form-control-small" required="" id="id_zone_thermal_coef_bottom"></td>'

function clear(tr1, tr2) {
    $('#table-zones-time tbody').empty().append(tr1)
    $('#table-zones-coef tbody').empty().append(tr2)
}

zones_select.onchange = function zone_select_change() {
    clear(t1, t2)
    $('#id_form-TOTAL_FORMS').val(zones_select.value);

    if (zones_select.value !== '1') {
        for (let current_row = 1; current_row < Math.floor(zones_select.value); current_row++) {
            let t_time = initial_time[0].cloneNode(true)
            let t_coef = initial_coef[0].cloneNode(true)

            t_time.classList = 'td-zone_' + (current_row + 1)
            t_time.children[0].innerHTML = current_row + 1
            t_time.children[1].children[0].id = 'id_form-'+(current_row)+'-zone_time'
            t_time.children[1].children[0].name = 'form-' + (current_row) + '-zone_time'
            t_time.children[1].children[0].value = 10
            t_time.children[2].children[0].id = 'id_form-' + (current_row) + '-zone_temp_air'
            t_time.children[2].children[0].name = 'form-' + (current_row) + '-zone_temp_air'
            t_time.children[2].children[0].value = 150
            if ($('#table-zones-time tbody tr:first-child td').length > 3) {
                t_time.children[3].children[0].id = 'id_form-' + (current_row) + '-zone_temp_bottom'
                t_time.children[3].children[0].name = 'form-' + (current_row) + '-zone_temp_bottom'
                t_time.children[3].children[0].value = 150
            }

            t_coef.classList = 'td-zone_' + (current_row + 1)
            t_coef.children[0].innerHTML = current_row + 1
            t_coef.children[1].children[0].id = 'id_form-' + (current_row) + '-zone_thermal_coef'
            t_coef.children[1].children[0].name = 'form-' + (current_row) + '-zone_thermal_coef'
            t_coef.children[1].children[0].value = 1500
            if ($('#table-zones-coef tbody tr:first-child td').length > 2) {
                t_coef.children[2].children[0].id = 'id_form-' + (current_row) + '-zone_thermal_coef_bottom'
                t_coef.children[2].children[0].name = 'form-' + (current_row) + '-zone_thermal_coef_bottom'
                t_coef.children[2].children[0].value = 1500
            }

            $('#table-zones-time tbody').append(t_time)
            $('#table-zones-coef tbody').append(t_coef)
        }
    }
}

$('#id_geometry input:radio').click(function () {
    zones_select.value = 1
    clear(t1, t2)
    if ($(this).val() === '1') {
        document.getElementsByClassName('form-thickness')[0].innerHTML =
            '<label for="id_thickness">Толщина, мм:</label>' + thickness_input
            $('#table-zones-time thead tr th:nth-child(4)').show();
            $('#table-zones-time tbody tr td:nth-child(4)').show()
            $('#table-zones-coef thead tr th:nth-child(3)').show()
            $('#table-zones-coef tbody tr td:nth-child(3)').show()

    } else {
        document.getElementsByClassName('form-thickness')[0].innerHTML =
            '<label for="id_thickness">Радиус, мм:</label>' + thickness_input
            $('#table-zones-time thead tr th:nth-child(4)').hide();
            $('#table-zones-time tbody tr td:nth-child(4)').hide()
            $('#table-zones-coef thead tr th:nth-child(3)').hide()
            $('#table-zones-coef tbody tr td:nth-child(3)').hide()
    }
});