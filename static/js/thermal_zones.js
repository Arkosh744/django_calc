const zones_select = document.getElementById("id_number_of_zones");

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

$(function () {
    geometry_select_change();
    zone_select_change();
});

zones_select.onchange = function() {
    zone_select_change()
};

$('#id_geometry input:radio').click(function() {
    geometry_select_change()
});
