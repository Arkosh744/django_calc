const zones_select = document.getElementById("id_number_of_zones");
const material_select = document.getElementById("id_material_select");

function geometry_select_change() {
    if ($('#id_geometry input:radio:checked').val() === '1') {
        $('.form-thickness label').text('Толщина, мм:')
        $('#table-zones-time thead tr th:nth-child(4)').show();
        $('#table-zones-time tbody tr td:nth-child(4)').show()
        $('#table-zones-coef thead tr th:nth-child(3)').show()
        $('#table-zones-coef tbody tr td:nth-child(3)').show()

    } else {
        $('.form-thickness label').text('Радиус, мм:')
        $('#table-zones-time thead tr th:nth-child(4)').hide();
        $('#table-zones-time tbody tr td:nth-child(4)').hide()
        $('#table-zones-coef thead tr th:nth-child(3)').hide()
        $('#table-zones-coef tbody tr td:nth-child(3)').hide()
    }
}

function zone_select_change() {
    let table_1 = $(`#table-zones-time tbody tr`).hide()
    let table_2 = $(`#table-zones-coef tbody tr`).hide()
    for (let current_row = 1; current_row <= Math.floor(zones_select.value); current_row++) {
        table_1.eq(current_row - 1).show()
        table_2.eq(current_row - 1).show()
    }
}

function get_material_elements() {
    let material = material_select.value;
    $.get(`./api/v1/get/material-elements/${material}`, function (data) {
        $.each(data, function (key, value) {
            console.log(key, value)
            let tableElement = document.getElementById('element-' + key)
            tableElement.innerText = value
        });
    }, 'json');
}

zones_select.onchange = function () {
    zone_select_change()
};

$('#id_geometry input:radio').click(function () {
    geometry_select_change()
});

let table_1_data = $(`#resultData tbody tr`)
let table_1_length = table_1_data.length
let table_2_data = $(`#resultData_temp_change tbody tr`)
let table_2_length = table_2_data.length

for (let current_row = 1; current_row <= table_1_length; current_row++) {
    if (current_row > 11 && current_row !== table_1_length) {
        table_1_data.eq(current_row).hide()
    }
    if (current_row > 11 && current_row + 1 === table_1_length) {
        table_1_data.eq(current_row).show()
    }
}

for (let current_row = 1; current_row <= table_2_length; current_row++) {
    if (current_row > 10 && current_row !== table_2_length) {
        table_2_data.eq(current_row).hide()
    }
    if (current_row > 10 && current_row + 1 === table_2_length) {
        table_2_data.eq(current_row).show()
    }
}


material_select.onchange = function () {
    get_material_elements()
}

// doc ready
$(function () {
    get_material_elements();
    geometry_select_change();
    zone_select_change();
});