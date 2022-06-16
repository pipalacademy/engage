var firstProblem;

function showProblem(selector) {
    var data = $(selector).data();
    console.log(data);
    $("#problem-title").html(data.title);
    $("#problem-description").html(data.description);
    $("#problem-code").html("");
    $("#problem-code").html(data.code || "<em>Not solved</em>");
    // $("#problem-code").html(data.solution.code);

    updateParticipantNav(data.problemName);
    updateProblemNav(data.prev, data.next);
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

function getNavigationButtonsHTML(previousLink, middleText, nextLink) {
    return `
	<ul class="pagination">
	    <li class="page-item ${ previousLink ? '' : 'disabled' }">
		<a class="page-link problem-nav-link" id="prev-problem-nav" href="${ previousLink ? previousLink : '#' }" tabindex="-1"><i class="fa-solid fa-arrow-left"></i></a>
	    <li>
	    <li class="page-item active">
		<a class="page-link">${ middleText }</a>
	    <li>
	    <li class="page-item ${ nextLink ? '' : 'disabled' }">
		<a class="page-link problem-nav-link" id="next-problem-nav" href="${ nextLink ? nextLink : '#' }"><i class="fa-solid fa-arrow-right"></i></a>
	    <li>
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
}

function updateProblemNav(prev, next) {
    if (!(prev || next) && !window.location.hash) {
	next = firstProblem;
    }

    $("#nav-problem").html(getNavigationButtonsHTML(getProblemLink(prev), "Problem", getProblemLink(next)));
}

$(function () {
    firstProblem = $("#nav-problem").data().firstProblem;
    loadProblemFromURL();
    updateProblemNav();

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
