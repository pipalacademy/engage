var activeProblem = null;

function showProblem(selector) {
    var data = $(selector).data();
    $("#problem-title").html(data.title);
    $("#problem-description").html(data.description);
    $("#problem-code").html("");
    $("#problem-code").html(data.code);

    renderReviewSection(data.latestSubmissionReview, data.submissionNames);

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

    $("#select-submission").on("change", function() {
	let submissionName = this.value;

	if (submissionName == "latest") {
	}

	submissionHTML
    })
});

async function getSubmissionReviewHTML(submissionName) {
    let response = await frappe.call({
	"method": "engage.api.get_submission_review_section_as_html",
	"type": "GET",
	"args": {
	    "submission_name": submissionName,
	},
    });

    return r.message;
}

function renderReviewSection(discussionSection, submissionNames) {
    $("#problem-review-section").html(discussionSection);

    function getOptionTag(value, index, arr) {
	return `<option value=${value}>Submission ${arr.length - index}</option>`;
    }

    $(".discussions-header").html(`
        <span class="discussion-heading">
          Review Comments
        </span>

	<select class="select-submission custom-select" id="select-submission">
	    <option selected value="latest">Latest Submission</option>
	    ${submissionNames.map(getOptionTag).join('\n')}
	</select>`
    );
}
