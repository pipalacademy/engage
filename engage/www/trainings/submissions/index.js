const submissionsDivSelector = "#submissions"
const loadingDivSelector = "#loading"

function refreshSubmissions(training, problemSet, reviewPending, testOutcome) {
    setLoading("Refreshing submissions...")

    getSubmissions(training, problemSet, reviewPending, testOutcome)
        .then(submissions => {
            setSubmissions(submissions)
        })
        .catch(error => {
            console.error(error)
            frappe.msgprint({ title: "Error", indicator: "red", message: error.toString() })
        })
        .finally(() => {
            unsetLoading()
        })
}

function setLoading(text) {
    let $submissions = $(submissionsDivSelector)
    let $loading = $(loadingDivSelector)

    $submissions.hide()
    $loading.show()

    // NOTE: maybe an icon or animation would be better, as reading takes effort/time
    $loading.html(`<em>${text}</em>`)
}

function unsetLoading() {
    let $submissions = $(submissionsDivSelector)
    let $loading = $(loadingDivSelector)

    $loading.hide()
    $submissions.show()

    $loading.html('')
}

async function getSubmissions(training, problemSet, reviewPending, testOutcome) {
    let method = "engage.api.get_submissions"
    let args = {
        training: training,
        ...(problemSet !== undefined && { problem_set: problemSet }),
        ...(reviewPending !== undefined && { for_review: reviewPending }),
        ...(testOutcome !== undefined && { test_outcome: testOutcome })
    }

    let response = await frappe.call({ method: method, args: args })

    if (!response.exc) {
        let msg = response.message;
        return msg.submissions
    } else {
        throw response.exc.join(",\n")
    }
}

function setSubmissions(submissions) {
    let $submissions = $(submissionsDivSelector)

    function enclose(inner) {
        return `<div class="col-12 col-md-6 col-xl-4">${inner}</div>`
    }

    function append(card) {
        $submissions.append(enclose(card));
    }

    function clear() {
        $submissions.html('');
    }

    clear()
    submissions.forEach(function (submission) {
        let cardHTML = getSubmissionCard(submission)
        append(cardHTML);
    })

    hljs.highlightAll()
}

function reviewPendingIcon() {
    return `<i class="fa-solid fa-circle for-review submission-icon"></i>`
}

function testsPassingIcon() {
    return `<i class="fa-solid fa-circle-check tests-passed-icon submission-icon"></i>`
}

function testsFailingIcon() {
    return `<i class="fa-solid fa-circle-xmark tests-failed-icon submission-icon"></i>`
}

function escapeHTML(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getSubmissionCard(submission) {
    let submissionURL = `/trainings/${submission.training}/submissions/${submission.name}`

    return `\
<a class="text-decoration-none color-inherit" href="${submissionURL}">
    <div class="submission-card p-4 my-4">
        <div class="submission-card-header mb-4 d-flex justify-content-between">
            <div>
                <div><strong>${escapeHTML(submission.author_full_name)}'s solution</strong></div>
                <div class="text-muted">to ${escapeHTML(submission.problem_title)} in ${escapeHTML(submission.problem_set_title)}
                </div>
            </div>
            <div class="d-flex mt-1 align-items-center submission-status">
                ${submission.for_review ? `<span class="mr-2">` + reviewPendingIcon() + `</span>` : ''}
                <span>
                    ${submission.test_outcome == 'passed' ? testsPassingIcon() : testsFailingIcon()}
                </span>
            </div>
        </div>
        <div class="submission-card-body">
            <pre><code class="language-python">${escapeHTML(submission.code)}</code></pre>
        </div>
        <div class="submission-card-footer d-flex justify-content-between align-items-center">
            <div>
                ${false ? "Published {{ published_ago }} ago" : submission.submitted_at}
            </div>

            <div class="d-flex align-items-center">
                <i class="comment-count-icon mt-half mr-2 font-lg fa-regular fa-message"></i> ${submission.comment_count}
            </div>
        </div>
    </div>
</a>
    `
}
