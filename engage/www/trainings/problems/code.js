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

function setCode(code) {
    console.log("code: ", code);
}

function setActiveTab(selector) {
    $(".tab-item.active").removeClass("active");
    $(selector).addClass("active");

    refreshTabs();
}

function loadGlobalData() {
    return $("#data").data();
}

$(function () {
    var globalData = loadGlobalData();

    refreshTabs();

    $(".tab-item").click(function (e) {
        let data = $(this).data();
        let code = data.code;

        setCode(code ? JSON.parse(code) : "");
        setActiveTab(this);
    });

    $(".code-editor").each(function (_i, el) {
        let data = $(el).data();

        let editor = new LiveCodeEditor(el, {
            runtime: "python",
            codemirror: true,
            problem: globalData.problem,
        });

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

        var submitted_result = data.submission;
        if (submitted_result && submitted_result != "null") {
            showTestResult(".output", submitted_result);
        }

        $(el).find(".submit").click(function () {
            var problem = globalData.problem;
            var training = globalData.training;
            var problem_set = globalData.problemSet;

            var code = editor.getCode();

            var payload = {
                problem_set: problem_set,
                problem: problem,
                code: code,
                author: frappe.session.user,
                training: training,
            };
            frappe.call({
                method: "engage.api.submit_practice_problem",
                args: payload,
                btn: $(".submit"),
                freeze: true,
                freeze_message: "Submitting",
                callback: function (r) {
                    var doc = r.message;
                    var submission = doc.test_result ? JSON.parse(doc.test_result) : {};
                    showTestResult(".output", submission);

                    frappe.msgprint("Successfully submitted solution for problem " + problem);
                    submissions[problem] = { problem: problem, code: code };
                    updateSubmissionStatus(problem);
                }
            });
        })
    });
});
