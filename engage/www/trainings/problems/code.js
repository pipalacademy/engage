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

function makeSubmission(editor, data) {
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
            showTestResult(".output", submission);

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
            results: options.results || null
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

        this.init();
    }

    beforeRun() {
        this.clear();
        this.activateTab(this.outputTab);
        this.setLoading("Running code...");
    }

    afterRun(output) {
        this.setOutput(output);
    }

    beforeRunTests() {
        this.clear();
        this.activateTab(this.resultsTab);
        this.setLoading("Running tests...");
    }

    afterRunTests(result) {
        this.setResults(result);
    }

    showTestResult(result) {
    }

    // initialise hooks / perform init actions
    init() {
        let sidebar = this;

        $(this.sidebarBtnSelector).click(function () {
            sidebar.activateTab(this);
        });

        this.activateDefaultTab();
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

        let html = this.parseResults(this.state.results);

        this.setSidebarTab(this.resultsTab);
        this.setSidebarContent(html);
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

    parseResults(result) {
        // TODO: implement parseResults
        if (result === null) {
            return this.resultsEmptyState;
        }

        var html = "";

        function print(text) {
            html += text + "\n";
        }

        print(`Test Status: ${result.outcome} (${result.stats.passed} passed and ${result.stats.failed} failed)`)
        result.testcases.forEach((t, i) => {
            print(`\n${i + 1}. ${t.name} ... ${t.outcome}`);
            if (t.outcome == "failed") {
                print("")
                print(t.error_detail.replaceAll(/^/mg, "    "));
            }
        })

        return `<pre class="test-result">${html}</pre>`;
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
            runtime: "python",
            codemirror: true,
            problem: globalData.problem,
            writer: sidebar,
        });
        let cm = editor.codemirror;
        cm.setSize(null, "500");

        editors[data.filepath] = editor;

        $(el).find(".submit").click(function () {
            makeSubmission(editor, {
                ...globalData,
                author: frappe.session.user
            });
        })
    });
});
