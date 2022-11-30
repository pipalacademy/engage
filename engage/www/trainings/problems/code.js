const editors = {};
const submissions = {};

const globalData = {};

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

function setCodeFile(filepath) {
    $(".code-editor").hide();
    $(`.code-editor[data-filepath="${filepath}"]`).show();
}

function setActiveTab(selector) {
    $(".tab-item.active").removeClass("active");
    $(selector).addClass("active");

    refreshTabs();
}

function escapeHTML(text) {
    return new Option(text).innerHTML;
}

function loadGlobalData() {
    let data = $("#data").data();
    $.extend(globalData, data);
}

// args: output element, data
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

function updateSubmissionStatus() {
    console.log("submitted");
    // editors.forEach(editor => {
    //     editor.parent.find(".submission-status").html("Submitted");
    // });
}

function makeSubmission(editor, sidebar, data) {
    let problem = data.problem;
    let training = data.training;
    let problemSet = data.problemSet;
    let author = data.author;

    let code = editor.getCode();
    let payload = {
        problem_set: problemSet,
        problem: problem,
        code: code,
        author: author,
        training: training,
    };

    frappe.call({
        method: "engage.api.submit_practice_problem",
        args: payload,
        btn: $(".submit"),
        freeze: true,
        freeze_message: "Submitting",
        callback: function (r) {
            let doc = r.message;
            let submission = doc.test_result ? JSON.parse(doc.test_result) : {};
            sidebar.afterSubmit(submission);

            frappe.msgprint("Successfully submitted solution for problem " + problem);
            submissions[problem] = { problem: problem, code: code };
            updateSubmissionStatus(problem);
        }
    });
}

class SidebarWriter extends WriterInterface {
    constructor(options) {
        super();

        // selectors
        this.instructionsTab = "#sidebar-tab-instructions";
        this.outputTab = "#sidebar-tab-output";
        this.resultsTab = "#sidebar-tab-results";

        // data
        this.state = {
            instructions: options.instructions || null,
            output: options.output || null,
            results: options.results || null,
            submitted: options.submitted || null
        };

        this.instructionsEmptyState = options.instructionsEmptyState || "<em>This problem has no description. Contact your instructor/admin if you think this is a mistake.</em>";
        this.outputEmptyState = options.outputEmptyState || "<em>Run your code to see its output here.</em>";
        this.resultsEmptyState = options.resultsEmptyState || "<em>Run tests to see its result here.</em>";

        this.handlersByID = {
            "sidebar-tab-instructions": this.onSidebarInstructions,
            "sidebar-tab-output": this.onSidebarOutput,
            "sidebar-tab-results": this.onSidebarResults,
        };

        this.sidebarBtnClass = "btn-sidebar-header";
        this.sidebarBtnSelector = `.${this.sidebarBtnClass}`;

        this.ctaButtonID = "cta-submit";
        this.codeSubmitBtnSelector = "#code-submit";

        this.init();
    }

    beforeRun() {
        this.clear();
        this.activateTab(this.outputTab);
        this.setLoading("Running code...");
    }

    afterRun(msg) {
        if (msg.ok) {
            this.setOutput(msg.output);
        } else {
            this.showError(msg.error, msg.message);
            this.setLoading(`Error: ${msg.error}`);
        }
    }

    beforeRunTests() {
        this.clear();
        this.activateTab(this.resultsTab);
        this.setLoading("Running tests...");
    }

    afterRunTests(result) {
        this.setSubmitted(false);
        this.setResults(result);
    }

    afterSubmit(submission) {
        this.setSubmitted(true);
        this.setResults(submission.test_result);
    }

    showError(error, message) {
        let html = "<p>Code execution failed due to an error. Please share the following log with your admin/instructor.</p>";
        html += `<pre class="msgprint-error-log">error: ${escapeHTML(error)}\nmessage: ${escapeHTML(message)}</pre>`
        frappe.msgprint({ title: "Error", indicator: "red", message: html });
    }

    // initialise hooks / perform init actions
    init() {
        let sidebar = this;

        $(this.sidebarBtnSelector).click(function () {
            sidebar.activateTab(this);
        });

        this.activateDefaultTab();

        if (this.state.results !== null) {
            this.setSubmitted(true);
            this.setResults();
        }
    }

    // private helpers
    clear() {
        this.setSidebarContent("");
    }

    setOutput(output) {
        if (output !== undefined) {
            this.state.output = output;
        }

        let html = this.parseOutput(this.state.output);

        this.setSidebarTab(this.outputTab);
        this.setSidebarContent(html);
    }

    setResults(results) {
        if (results !== undefined) {
            this.state.results = results;
        }

        let html = this.parseResults(this.state.results, this.state.submitted);

        this.setSidebarTab(this.resultsTab);
        this.setSidebarContent(html);

        this.setupCtaButtonHandler();
    }

    setSubmitted(value) {
        this.state.submitted = value;
    }

    setLoading(text) {
        let inner = escapeHTML(text);
        let html = `<em>${inner}</em>`

        this.setSidebarContent(html);
    }

    parseOutput(output) {
        let inner = (output === null) ? this.outputEmptyState : escapeHTML(output);
        let html = `<pre class="output">${inner}</pre>`;

        return html;
    }

    parseResults(result, submitted) {
        submitted = submitted || false;

        if (result === null) {
            return this.resultsEmptyState;
        }

        var html = "";

        function print(text) {
            html += text + "\n";
        }

        print(this.renderTestSummary(result.outcome, result.stats));
        result.testcases.forEach((t, i) => {
            print(this.renderTestCase(t));
        })
        print(this.renderTestResultCta(result.outcome, submitted));

        return `<div class="test-result">${html}</div>`;
    }

    setupCtaButtonHandler() {
        let ctaBtnSelector = "#" + this.ctaButtonID;

        let $codeSubmitBtn = $(this.codeSubmitBtnSelector);
        let $ctaSubmitBtn = $("#sidebar").find(ctaBtnSelector);

        $ctaSubmitBtn.click(function (e) {
            e.preventDefault();
            $(this).addClass('disabled');
            $codeSubmitBtn.click();
            $(this).removeClass('disabled');
            return false;
        });
    }

    /**
     * Returns presentable HTML for test summary
     * 
     * @param outcome 'passed' or 'failed'
     * @param stats Stats information about the tests run
     * @param stats.passed Number of test cases that passed
     * @param stats.failed Number of test cases that failed
     */
    renderTestSummary(outcome, stats) {
        let className = outcome == 'passed' ? 'passed' : 'failed';
        return `\
        <div class="test-result-summary ${className}">
            <pre class="status ${className}"><i class="font-sm fa-solid fa-circle"></i> ${outcome == 'passed' ? 'Passed' : 'Failed'}</pre>
            <span>${stats.passed} passed, ${stats.failed} failed</span>
        </div>`;
    }

    /**
     * Returns presentable HTML for a test case
     * 
     * @param testCase Information about the test case and its outcome
     * @param testCase.name Name of the test case
     * @param testCase.outcome Whether the testcase was cleared, can be 'passed' or 'failed'
     * @param testCase.error_detail [optional] Present if `outcome` is 'failed'
     */
    renderTestCase(testCase) {
        var escapeHTML = this.escapeHTML;

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

    renderTestResultCta(outcome, submitted) {
        function enclose(inner) {
            return `<div class="test-result-cta">${inner}</div>`;
        }

        let text = "";
        let ctaButtonText = "";
        if (!submitted && outcome == 'passed') {
            text = `\
            <p>Congratulations!</p>
            <p>All tests are passing! You are ready to submit.</p>`;
            ctaButtonText = "Submit solution";
        } else if (!submitted) {
            text = `\
            <p>Tests failed.</p>
            <p>
                You need to get the tests to pass to submit the solution.
                However, you can submit a draft now for the instructor to review.
            </p>
            `;
            ctaButtonText = "Submit draft";
        } else if (submitted && outcome == 'passed') {
            text = `\
            <p>Congrats! You have submitted a working solution to the problem.</p>
            <p>Any comments your instructor writes to this problem will be visible in the section below.</p>
            `;
        } else {
            text = `\
            <p>Your solution has been submitted as draft and is visible to the instructor.</p>
            <p>Their comments will be visible in the section below.</p>
            `;
        }

        let ctaButtonHTML = ctaButtonText && `\
            <div class="flex justify-content-center">
                <button id="${this.ctaButtonID}" class="btn btn-primary">${ctaButtonText}</button>
            </div>`;

        return enclose(text + "\n" + ctaButtonHTML);
    }

    escapeHTML(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // other modification methods
    setSidebarContent(content) {
        $("#sidebar-content").html(content);
    }

    setSidebarTab(el) {
        let $el = $(el);

        // make tab active
        $(this.sidebarBtnSelector).removeClass("active");
        $el.addClass("active");
    }

    activateTab(el) {
        // set content
        let elementID = $(el).attr("id");
        let handler = this.handlersByID[elementID].bind(this);
        handler();
    }

    activateDefaultTab() {
        let defaultSidebarTab = "#sidebar-tab-instructions";
        this.activateTab(defaultSidebarTab);
    }

    onSidebarInstructions() {
        this.setSidebarTab(this.instructionsTab);
        this.setSidebarContent(this.state.instructions);
    }

    onSidebarOutput() {
        this.setOutput(this.state.output);
    }

    onSidebarResults() {
        this.setResults(this.state.results);
    }
}

$(function () {
    loadGlobalData();

    refreshTabs();
    setCodeFile(globalData.defaultFilepath);

    var sidebar = new SidebarWriter({
        instructions: globalData.problemDescription || null,
        results: globalData.submission || null,
    });

    $(".tab-item").click(function (e) {
        let data = $(this).data();

        setCodeFile(data.filepath);
        setActiveTab(this);
    });

    $(".code-editor").each(function (_i, el) {
        let data = $(el).data();

        let editor = new LiveCodeEditor(el, {
            runtime: globalData.runtime,
            codemirror: true,
            problem: globalData.problem,
            writer: sidebar,
        });
        let cm = editor.codemirror;
        cm.setSize(null, "500");

        editors[data.filepath] = editor;

        $(el).find(".submit").click(function () {
            makeSubmission(editor, sidebar, {
                ...globalData,
                author: frappe.session.user
            });
        })
    });
});
