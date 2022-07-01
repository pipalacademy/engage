function truncateFilepath(filepath) {
    let parts = filepath.split("/");

    let parents = parts.slice(0, parts.length - 1);
    let filename = parts[parts.length - 1];

    let truncatedParts = parents.map(s => s[0]);
    truncatedParts.push(filename);

    return truncatedParts.join("/");
}

function refreshTabs() {
    $(".tab-item").each(function (_i, el) {
        let isActive = $(el).hasClass("active");

        let data = $(el).data();
        let filepath = data.filepath;

        $(el).text(isActive ? filepath : truncateFilepath(filepath));
    });
}

function setCode(code) {
    console.log("code: ", code);
}

function setActiveTab(selector) {
    $(".tab-item.active").removeClass("active");
    $(selector).addClass("active");

    refreshTabs();
}

$(function () {
    refreshTabs();

    $(".tab-item").click(function (e) {
        let data = $(this).data();
        let code = data.code;

        setCode(code ? JSON.parse(code) : "");
        setActiveTab(this);
    });
});
