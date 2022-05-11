let zones_select = document.getElementById("id_number_of_zones");
let thickness_input = '<input type="text" name="thickness" value="30" class="form-control form-control-small" ' +
    'required="" id="id_thickness">'
let initial = $('tr.td-zone_1')
let t1 = initial[0]
let t2 = initial[1]
let temp_bottom = $('#table-zones-time thead tr th:nth-child(4)')
let temp_bottom_input = $('#table-zones-time tbody tr td:nth-child(4)')
let temp_bottom_clone = temp_bottom[0].cloneNode(true)
let temp_bottom_input_clone = temp_bottom_input[0].cloneNode(true)

let coef_bottom = $('#table-zones-coef thead tr th:nth-child(3)')
let coef_bottom_input = $('#table-zones-coef tbody tr td:nth-child(3)')
let coef_bottom_clone = coef_bottom[0].cloneNode(true)
let coef_bottom_input_clone = coef_bottom_input[0].cloneNode(true)

function clear(tr1, tr2) {
    $('#table-zones-time tbody').empty().append(tr1)
    $('#table-zones-coef tbody').empty().append(tr2)
}

zones_select.onchange = function zone_select_change() {
    clear(t1, t2)

    if (zones_select.value !== '1') {
        for (let current_row = 1; current_row < Math.floor(zones_select.value); current_row++) {
            let t_time = initial[0].cloneNode(true)
            let t_coef = initial[1].cloneNode(true)

            t_time.classList = 'td-zone_' + (current_row + 1)
            t_time.children[0].innerHTML = current_row + 1
            t_time.children[1].children[0].id = 'id_zone_time_' + (current_row + 1)
            t_time.children[1].children[0].value = 10
            t_time.children[2].children[0].id = 'id_zone_temp_air_' + (current_row + 1)
            t_time.children[2].children[0].value = 150
            if (t_time.length > 3) {
                t_time.children[3].children[0].id = 'id_zone_temp_bottom_' + (current_row + 1)
                t_time.children[3].children[0].value = 30
            }

            t_coef.classList = 'td-zone_' + (current_row + 1)
            t_coef.children[0].innerHTML = current_row + 1
            t_coef.children[1].children[0].id = 'id_zone_coef_' + (current_row + 1)
            t_coef.children[1].children[0].value = 1500
            if (t_coef.length > 2) {
                t_coef.children[2].children[0].id = 'id_zone_coef_' + (current_row + 1)
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

        if ($('#table-zones-time thead tr')[0].children.length < 4) {
            $('#table-zones-time thead tr').append(temp_bottom_clone)
            $('#table-zones-time tbody tr').append(temp_bottom_input_clone)
        }

        if ($('#table-zones-coef thead tr')[0].children.length < 3) {
            $('#table-zones-coef thead tr').append(coef_bottom_clone)
            $('#table-zones-coef tbody tr').append(coef_bottom_input_clone)
        }

    } else {
        document.getElementsByClassName('form-thickness')[0].innerHTML =
            '<label for="id_thickness">Радиус, мм:</label>' + thickness_input

        if ($('#table-zones-time thead tr')[0].children.length >= 4) {
            $('#table-zones-time thead tr th:nth-child(4)').remove();
            $('#table-zones-time tbody tr td:nth-child(4)').remove()
        }

        if ($('#table-zones-coef thead tr')[0].children.length >= 3) {
            $('#table-zones-coef thead tr th:nth-child(3)').remove()
            $('#table-zones-coef tbody tr td:nth-child(3)').remove()
        }
    }
});