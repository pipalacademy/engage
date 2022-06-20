var firstProblem;
var activeProblem = null;

function showProblem(selector) {
    var data = $(selector).data();
    $("#problem-title").html(data.title);
    $("#problem-description").html(data.description);
    $("#problem-code").html("");
    $("#problem-code").html(data.code !== null ? JSON.parse(data.code) : "<em>Not solved</em>");

    updateParticipantNav(data.problemName);
    updateProblemNav(data.prev, data.prevTitle, data.next, data.nextTitle);

    $("#problem-review-section").html(data.latestSubmissionReview);
    // this is needed to trigger the javascript in discussions template 
    frappe.trigger_ready();

}

function getProblemLink(problemName) {
    if (problemName) {
        let loc = new URL(window.location);
        loc.hash = problemName;
        return loc.toString();
    } else {
        return null;
    }
};

function getNavigationButtonsHTML(previousLink, previousText, middleText, nextLink, nextText) {
    return `
	<ul class="pagination pagination-sm justify-content-center">
	    <li class="page-item ${previousLink ? '' : 'disabled'} w-100">
		<a class="page-link problem-nav-link" id="prev-problem-nav" href="${previousLink ? previousLink : '#'}" tabindex="-1">
		    <i class="fa-solid fa-arrow-left"></i> ${truncate(previousText, 24)}
		</a>
	    </li>
	    <li class="page-item active">
		<a class="page-link">${middleText}</a>
	    </li>
	    <li class="page-item ${nextLink ? '' : 'disabled'} w-100 text-right">
		<a class="page-link problem-nav-link" id="next-problem-nav" href="${nextLink ? nextLink : '#'}">
		    ${truncate(nextText, 24)} <i class="fa-solid fa-arrow-right"></i>
		</a>
	    </li>
	</ul>
    `;
}

function beforeShowProblem(selector) {
    $(".problem-link").removeClass("active");
    $(selector).addClass("active");
}

function loadProblemFromURL() {
    if (document.location.hash) {
        let link = $(`#problem-${window.location.hash.slice(1)}`.replace("/", "\\/"))[0];

        beforeShowProblem(link);
        showProblem(link);
    }
}

function updateParticipantNav(problemName) {
    ($("#nav-participant").find("#prev-link")[0] || {}).hash = problemName;
    ($("#nav-participant").find("#next-link")[0] || {}).hash = problemName;

    $(".participant-review-link").each(function () {
        this.hash = problemName;
    });
}

function updateProblemNav(prev, prevText, next, nextText) {
    if (!(prev || next) && !window.location.hash) {
        next = firstProblem;
    }

    $("#nav-problem").html(getNavigationButtonsHTML(getProblemLink(prev), prevText, "Problem", getProblemLink(next), nextText));
}

function truncate(text, limit) {
    if (text.length > limit) {
        return text.slice(0, limit - 3) + "...";
    }

    return text;
}

$(function () {
    firstProblem = $("#nav-problem").data().firstProblem;
    loadProblemFromURL();

    $(".problem-link").on('click', function () {
        document.location = getProblemLink(this.id.slice("problem-".length));

        beforeShowProblem(this);
        showProblem(this);

        return false;
    });

    $("#nav-problem").on('click', ".problem-nav-link", function () {
        document.location = this.href;
        loadProblemFromURL();

        return false;
    });
});
