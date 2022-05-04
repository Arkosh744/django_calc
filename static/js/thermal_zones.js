let zones_select = document.getElementById("id_number_of_zones");
let thickness_input ='<input type="text" name="thickness" value="30" class="form-control form-control-sm" ' +
    'required="" id="id_thickness">'


function clear(tr1, tr2) {
    $('#table-zones-time tbody').empty().append(tr1)
    $('#table-zones-coef tbody').empty().append(tr2)
}

zones_select.onchange = function () {
    let initial = $('tr.td-zone_1')
    let t1 = initial[0]
    let t2 = initial[1]
    clear(t1, t2)

    if (zones_select.value !== '1') {
        for (let current_row = 1; current_row < Math.floor(zones_select.value); current_row++) {
            console.log(current_row)
            let t_time = initial[0].cloneNode(true)
            let t_coef = initial[1].cloneNode(true)

            t_time.classList = 'td-zone_' + (current_row + 1)
            t_time.children[0].innerHTML = current_row + 1
            t_time.children[1].children[0].id = 'id_zone_time_' + (current_row + 1)
            t_time.children[1].children[0].value = 1
            t_time.children[2].children[0].id = 'id_zone_temp_air_' + (current_row + 1)
            t_time.children[2].children[0].value = 600
            t_time.children[3].children[0].id = 'id_zone_temp_bottom_' + (current_row + 1)
            t_time.children[3].children[0].value = 30

            t_coef.classList = 'td-zone_' + (current_row + 1)
            t_coef.children[0].innerHTML = current_row + 1
            t_coef.children[1].children[0].id = 'id_zone_coef_' + (current_row + 1)
            t_coef.children[1].children[0].value = 150
            t_coef.children[2].children[0].id = 'id_zone_coef_' + (current_row + 1)
            t_coef.children[2].children[0].value = 150

            $('#table-zones-time tbody').append(t_time)
            $('#table-zones-coef tbody').append(t_coef)
        }
    }
}

$('#id_geometry input:radio').click(function () {
    if ($(this).val() === '1') {
        document.getElementsByClassName('form-thickness')[0].innerHTML =
            '<label for="id_thickness">Толщина, мм:</label>' + thickness_input
    } else {
        document.getElementsByClassName('form-thickness')[0].innerHTML =
            '<label for="id_thickness">Радиус, мм:</label>' + thickness_input
    }
});