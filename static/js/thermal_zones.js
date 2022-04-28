let zones_select = document.getElementById("id_number_of_zones");

function clear(tr1, tr2) {
    $('#table-zones-time tbody').empty().append(tr1)
    $('#table-zones-coef tbody').empty().append(tr2)
}

function check_len() {
    return $('#table-zones-time tbody').children().length
}

zones_select.onchange = function () {
    let initial = $('tr.td-zone_1')
    let t1 = initial[0]
    let t2 = initial[1]

    if (zones_select.value === '1') {
        clear(t1, t2)
    } else {
        clear(t1, t2)

        // while (current_row.toString() !== zones_select.value.toString()) {
        //     console.log(current_row)
        //     $('#table-zones-time tbody').append(t1)
        //     $('#table-zones-coef tbody').append(t2)
        //     current_row = check_len()
        // }

        for (let current_row = 1; current_row < Math.floor(zones_select.value); current_row++) {
            console.log(current_row)
            let t_time = initial[0].cloneNode(true)
            let t_coef = initial[1].cloneNode(true)

            t_time.classList = 'td-zone_' + (current_row + 1)
            t_time.children[0].innerHTML = current_row + 1
            t_time.children[1].children[0].id = 'id_zone_time_' + (current_row + 1)
            t_time.children[1].children[0].name = 'zone_time_' + (current_row + 1)
            t_time.children[1].children[0].value = 1
            t_time.children[2].children[0].id = 'id_zone_temp_air_' + (current_row + 1)
            t_time.children[2].children[0].name = 'zone_temp_air_' + (current_row + 1)
            t_time.children[2].children[0].value = 600
            t_time.children[3].children[0].id = 'id_zone_temp_bottom_' + (current_row + 1)
            t_time.children[3].children[0].name = 'zone_temp_bottom_' + (current_row + 1)
            t_time.children[3].children[0].value = 30

            t_coef.classList = 'td-zone_' + (current_row + 1)
            t_coef.children[0].innerHTML = current_row + 1
            t_coef.children[1].children[0].id = 'id_zone_coef_' + (current_row + 1)
            t_coef.children[1].children[0].name = 'zone_coef_' + (current_row + 1)
            t_coef.children[1].children[0].name = 150
            t_coef.children[2].children[0].id = 'id_zone_coef_' + (current_row + 1)
            t_coef.children[2].children[0].name = 'zone_coef_' + (current_row + 1)
            t_coef.children[2].children[0].name = 150

            $('#table-zones-time tbody').append(t_time)
            $('#table-zones-coef tbody').append(t_coef)
        }
        // let t_time = t1.cloneNode(true)
        // console.log(t_time)
        // let t_coef = t2.cloneNode(true)
        // $('#table-zones-time tbody').append(t_time)
        // $('#table-zones-coef tbody').append(t_coef)
    }
}
