var activeProblem = null;

function showProblem(selector) {
    var data = $(selector).data();
    $("#problem-title").html(data.title);
    $("#problem-description").html(data.description);
    $("#problem-code").html("");
    $("#problem-code").html(data.code);

    $("#problem-review-section").html(data.latestSubmissionReview);

    // this is needed to trigger the javascript in discussions template 
    frappe.trigger_ready();

    // $("#problem-code").html(data.solution.code);
}

$(function() {
    $(".problem-link").on('click', function () {
        $(".problem-link").removeClass("active");
        $(this).addClass("active");
        showProblem(this);
    });
});
