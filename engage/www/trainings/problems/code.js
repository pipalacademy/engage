const editors = {};
const submissions = {};

const sidebarBtnClass = "btn-sidebar-header";
const sidebarBtnSelector = `.${sidebarBtnClass}`;

var globalData = {};

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

function loadGlobalData() {
    globalData = $("#data").data();
}

function setSidebarContent(content) {
    $("#sidebar-content").html(content);
}

function onSidebarInstructions() {
    setSidebarContent(globalData.problemDescription);
}

function onSidebarOutput() {
    setSidebarContent("output here");
}

function onSidebarResults() {
    setSidebarContent("results here");
}

function activateDefaultSidebarTab() {
    let defaultSidebarTab = "#sidebar-tab-instructions";
    activateSidebarTab(defaultSidebarTab);
}

function activateSidebarTab(el) {
    let handlers = {
        "sidebar-tab-instructions": onSidebarInstructions,
        "sidebar-tab-output": onSidebarOutput,
        "sidebar-tab-results": onSidebarResults,
    };

    let $el = $(el);
    let handler = handlers[$el.attr("id")];

    $(sidebarBtnSelector).removeClass("active");
    $el.addClass("active");

    handler();
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

$(function () {
    loadGlobalData();

    refreshTabs();
    setCodeFile(globalData.defaultFilepath);

    activateDefaultSidebarTab();

    $(".tab-item").click(function (e) {
        let data = $(this).data();

        setCodeFile(data.filepath);
        setActiveTab(this);
    });

    $(sidebarBtnSelector).click(function () {
        activateSidebarTab(this);
    });

    $(".code-editor").each(function (_i, el) {
        let data = $(el).data();

        let editor = new LiveCodeEditor(el, {
            runtime: "python",
            codemirror: true,
            problem: globalData.problem,
        });
        let cm = editor.codemirror;
        cm.setSize(null, "500");

        editors[data.filepath] = editor;

        let lastSubmission = globalData.submission;
        if (lastSubmission && lastSubmission != "null") {
            showTestResult(".output", lastSubmission);
        }

        $(el).find(".submit").click(function () {
            makeSubmission(editor, {
                ...globalData,
                author: frappe.session.user
            });
        })
    });
});
