function showProblem(selector) {
    var data = $(selector).data();
    console.log(data);
    $("#problem-title").html(data.title);
    $("#problem-description").html(data.description);
    $("#problem-code").html("");
    $("#problem-code").html(data.code);
    // $("#problem-code").html(data.solution.code);
}

$(function () {
    $(".problem-link").on('click', function () {
        $(".problem-link").removeClass("active");
        $(this).addClass("active");
        showProblem(this);
    });
});
