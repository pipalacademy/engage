const submissionsDivSelector = "#submissions"
const loadingDivSelector = "#loading"
const paginationDivSelector = "#pagination"

const state = {
    training: "2022/python-fundamentals",
    page: 1,
}

function loadFilters() {
    let $problemSet = $("#select-problem-set")
    let problem_set = $problemSet.find(":selected").val() || undefined

    let $problem = $("#select-problem")
    let problem = $problem.find(":selected").val() || undefined

    let $author = $("#select-author")
    let author = $author.find(":selected").val() || undefined

    let $reviewPending = $("#check-review-pending")
    let for_review = ($reviewPending.prop("checked") == true) || undefined

    let $testsPassing = $("#check-tests-passing")
    let testsPassing = ($testsPassing.prop("checked") == true) || undefined

    let $testsFailing = $("#check-tests-failing")
    let testsFailing = ($testsFailing.prop("checked") == true) || undefined

    let test_outcome
    if (testsPassing && testsFailing) {
        throw new Error("passing and failing shouldn't both be selected")
    } else if (testsPassing) {
        test_outcome = 'passed'
    } else if (testsFailing) {
        test_outcome = 'failed'
    }

    return {
        problem_set, problem, author, for_review, test_outcome
    }
}

function refreshSubmissions(opts) {
    opts = opts || {}

    setLoading("Refreshing submissions...")

    let training = state.training
    let { problemSet: problem_set, problem, author, reviewPending: for_review, testOutcome: test_outcome, page } = opts

    let filters = loadFilters()
    filters.problem_set = problem_set !== undefined ? problem_set : filters.problem_set
    filters.problem = problem !== undefined ? problem : filters.problem
    filters.author = author !== undefined ? author : filters.author
    filters.for_review = for_review !== undefined ? for_review : filters.for_review
    filters.test_outcome = test_outcome !== undefined ? test_outcome : filters.test_outcome
    filters.page = page !== undefined ? page : state.page

    getSubmissions(training, filters)
        .then(result => {
            let { submissions, total_pages: totalPages } = result
            setSubmissions(submissions)
            setPagination(getPagination(filters.page, totalPages))
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

async function getSubmissions(training, opts) {
    let method = "engage.api.get_submissions"
    let args = {
        training: training,
        ...opts,
    }

    let response = await frappe.call({ method: method, args: args })

    if (!response.exc) {
        let msg = response.message;
        return { submissions: msg.submissions, total_pages: msg.total_pages }
    } else {
        throw response.exc.join(",\n")
    }
}

function setSubmissions(submissions) {
    let $submissions = $(submissionsDivSelector)

    function print(html) {
        $submissions.append(html);
    }

    function clear() {
        $submissions.html('');
    }

    function encloseCard(inner) {
        return `<div class="col-12 col-md-6 col-xl-4">${inner}</div>`
    }

    clear()
    if (submissions.length > 0) {
        submissions.forEach(function (submission) {
            let cardHTML = getSubmissionCard(submission)
            print(encloseCard(cardHTML));
        })

        hljs.highlightAll()
    } else {
        print(`\
        <div class="col-12">
            <div class="d-block text-center border rounded-lg p-8">
                <em>No submissions found with given filters</em>
            </div>
        </div>`)
    }
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

function getSubmissionCard(submission) {
    let submissionURL = `/trainings/${submission.training}/submissions/${submission.name}`
    let now = new Date()
    let submittedAt = new Date(submission.submitted_at)

    return `\
<a class="text-decoration-none color-inherit" href="${submissionURL}">
    <div class="submission-card p-4 my-4">
        <div class="submission-card-header mb-4 d-flex justify-content-between">
            <div>
                <div><strong>${frappe.utils.escape_html(submission.author_full_name)}'s solution</strong></div>
                <div class="text-muted">to ${frappe.utils.escape_html(submission.problem_title)} in ${frappe.utils.escape_html(submission.problem_set_title)}
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
            <pre><code class="language-python">${frappe.utils.escape_html(submission.code)}</code></pre>
        </div>
        <div class="submission-card-footer d-flex justify-content-between align-items-center">
            <div>
                Submitted ${get_pretty_datetime_diff(now, submittedAt)} ago
            </div>

            <div class="d-flex align-items-center">
                <i class="comment-count-icon mt-half mr-2 font-lg fa-regular fa-message"></i> ${submission.comment_count}
            </div>
        </div>
    </div>
</a>
    `
}

function setPagination(html) {
    let $pagination = $(paginationDivSelector)

    $pagination.html(html)
}

function getPagination(currentPage, totalPages) {
    let has_next = currentPage < totalPages
    let has_prev = currentPage > 1

    return `\
    <nav>
        <ul class="pagination">
            <li class="page-item ${!has_prev ? 'disabled' : ''}">
                <button class="page-link" ${has_prev ? 'onclick="goToPrevPage()"' : ''} id="pagination-prev" data-page="${has_prev ? currentPage - 1 : 1}">Previous</a>
            </li>
            <li class="page-item ${!has_next ? 'disabled' : ''}">
                <button class="page-link" ${has_next ? 'onclick="goToNextPage()"' : ''} id="pagination-next" data-page="${has_next ? currentPage + 1 : currentPage}">Next</a>
            </li>
        </ul>
    </nav>
    `
}

function goToPrevPage() {
    let data = $("#pagination-prev").data()
    let page = data.page

    state.page = page

    refreshSubmissions({ page })
}

function goToNextPage() {
    let data = $("#pagination-next").data()
    let page = data.page

    state.page = page

    refreshSubmissions({ page })
}

function get_pretty_datetime_diff(d1, d2) {
    let milliseconds = d1 - d2
    let seconds = parseInt(milliseconds / 1000)
    let days = parseInt(seconds / (60 * 60 * 24))

    let y = parseInt(days / 360)
    let mo = parseInt((days - 360 * y) / 30)
    let d = days % 30

    let h = parseInt(seconds / (60 * 60))
    let m = parseInt((seconds - (h * 60 * 60)) / 60)
    let s = seconds % 30

    switch (true) {
        case (y !== 0):
            return `${y}y`
        case (mo !== 0):
            return `${mo}mo`
        case (d !== 0):
            return `${d}d`
        case (h !== 0):
            return `${h}h`
        case (m !== 0):
            return `${m}m`
        default:
            return `${s}s`
    }
}

$(function () {
    let $data = $("#data")
    let $selectProblemSet = $("#select-problem-set")
    let $selectProblem = $("#select-problem")
    let $selectAuthor = $("#select-author")
    let $checkReviewPending = $("#check-review-pending")
    let $checkTestsPassing = $("#check-tests-passing")
    let $checkTestsFailing = $("#check-tests-failing")

    let data = $data.data()

    state.training = data.training
    state.page = 1

    refreshSubmissions()

    $selectProblemSet.change(refreshSubmissions)
    $selectProblem.change(refreshSubmissions)
    $selectAuthor.change(refreshSubmissions)
    $checkReviewPending.change(refreshSubmissions)

    $checkTestsPassing.change(() => {
        $checkTestsFailing.prop("checked", false)
        refreshSubmissions()
    })

    $checkTestsFailing.change(() => {
        $checkTestsPassing.prop("checked", false)
        refreshSubmissions()
    })
})
