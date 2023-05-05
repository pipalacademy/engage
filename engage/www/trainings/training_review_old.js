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

// $(function () {
//     firstProblem = $("#nav-problem").data().firstProblem;
//     loadProblemFromURL();
//
//     $(".problem-link").on('click', function () {
//         document.location = getProblemLink(this.id.slice("problem-".length));
//
//         beforeShowProblem(this);
//         showProblem(this);
//
//         return false;
//     });
//
//     $("#nav-problem").on('click', ".problem-nav-link", function () {
//         document.location = this.href;
//         loadProblemFromURL();
//
//         return false;
//     });
// });
//

function showTestResult(output, d) {
    if (!d) {
        return;
    }

    function clear() {
        $(output).text("");
    }

    function print(text) {
        $(output).append(text + "\n");
    }

    clear();

    print(`Test Status: ${d.outcome} (${d.stats.passed} passed and ${d.stats.failed} failed)`)
    d.testcases.forEach((t, i) => {
        print(`\n${i + 1}. ${t.name} ... ${t.outcome}`);
        if (t.outcome == "failed") {
            print("")
            print(t.error_detail.replaceAll(/^/mg, "    "));
        }
    })
}

$(function () {
    // var submission = $(".test-result").data("submission");

    //$(".test-result").html($(".test-result"))
    console.log(["Test Result:", submission])

    if (submission) {
        renderResults($(".test-result"), JSON.parse(submission.test_result));
    }
});

function renderResults(element, result) {
    var html = "";

    function print(text) {
        html += text + "\n";
    }

    print(renderTestSummary(result.outcome, result.stats));
    result.testcases.forEach((t, i) => {
        print(renderTestCase(t));
    })

    console.log("renderResults", html);

    $(element).html(html);
}

function renderTestSummary(outcome, stats) {
    let className = outcome == 'passed' ? 'passed' : 'failed';
    return `\
    <div class="test-result-summary ${className}">
        <pre class="status ${className}"><i class="font-sm fa-solid fa-circle"></i> ${outcome == 'passed' ? 'Passed' : 'Failed'}</pre>
        <span>${stats.passed} passed, ${stats.failed} failed</span>
    </div>`;
}

function escapeHTML(text) {
    return new Option(text).innerHTML;
}


function renderTestCase(testCase) {
    function passedCase() {
        return `\
        <div class="testcase-result-passed">
            <i class="fa-solid fa-circle-check"></i> ${escapeHTML(testCase.name)}
        </div>`;
    }

    function failedCase() {
        return `\
        <div class="testcase-result-failed">
            <i class="fa-solid fa-circle-xmark"></i> ${escapeHTML(testCase.name)}
        </div>
        <pre class="testcase-result-error-detail">${escapeHTML(testCase.error_detail)}</pre>
        `
    }

    function enclose(inner) {
        return `\
        <div class="testcase-result">
            ${inner}
        </div>`
    }

    if (testCase.outcome == 'passed') {
        return enclose(passedCase())
    } else {
        return enclose(failedCase())
    }
}
