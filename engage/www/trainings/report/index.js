function showTable(selector) {
    let $el = $(selector);

    let id = $el.attr("id");
    let data = $el.data();

    let columns = data.columns;
    let rows = data.rows;

    const datatable = new DataTable(`#${id}`, {
        columns: columns,
        data: rows,
    });
}

$(function () {
    showTable("#report-table");
})
