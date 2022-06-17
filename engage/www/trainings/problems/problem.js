$(function() {
  const data = $("#data").data();
  console.log("data", data);
  const problem_set = data.problemSet;
  var submissions = {};
  var editors = {};

  function updateSubmissions() {
    for (var problem in submissions) {
        if (editors[problem]) {
            editors[problem].codemirror.doc.setValue(submissions[problem].code);
            updateSubmissionStatus(problem)
        }
    }
  }
  function updateSubmissionStatus(problem) {
    $(editors[problem].parent).find(".submission-status").text("Submitted")
  }

  function getCodeFiles(problem) {
    return problem.files.filter(f => f.kind == "code");
  }

  function getDataFiles(problem) {
    return problem.files.filter(f => f.kind == "data");
  }

  function getTestFiles(problem) {
    return problem.files.filter(f => f.kind == "test");
  }
  
  $(".code-editor").each(function(index, e) {
    var codeFiles = getCodeFiles(data.problem);
    var dataFiles = getDataFiles(data.problem);
    var testFiles = getTestFiles(data.problem);

    var setupCode = (codeFiles && codeFiles[0].content) || "";

    var files = codeFiles.concat(dataFiles).map(f => {
      return {
	"filename": f.relative_path,
	"contents": f.contents,
      }
    });

    var editor = new LiveCodeEditor(e, {
      base_url: "https://livecode.pipal.in",
      runtime: "python",
      codemirror: true,
      files: files,
      env: {
        "FALCON_SOURCE_FILE": codeFiles[0].relative_path,
      },
      events: {
        beforeRun: function() {
          var args = $(e).find(".arguments").val().trim().split(/\s+/);
          if (args[0] === "") {
              args = [];
          }
          editor.command = args;
        //   console.log("arguments", arguments, editor.command);
        }
      }
    });
    var problem = $(e).data("problem");
    editors[problem] = editor;
    
    $(e).find(".run-tests").click(async () => {
        var data_ = $(e).data();

        var problem = data_.problem;
        var code = editor.getCode();
        var setupCode = JSON.parse(data_.setupCode || '""');

        var tests = JSON.parse(data_.tests);
        var output = editors[problem].elementOutput;
        
        //var url = "https://falcon.pipal.in/exec";
        // var url = "http://localhost:8010/exec";
        var url = "https://falcon.mon.school/exec";
        
        var data = {
            "runtime": "python",
            "code": code,
            "files": [
                {"filename": "test_main.py", "contents": tests},
                {"filename": "_init.py", "contents": setupCode}
            ],
            "env": {
                "FALCON_MODE": "test"
            }
        }
        $(output).html("");
        
        var result = await fetch(url, {
          method: "POST",
          mode: "cors",
          cache: "no-cache",
          headers: {
            "Content-Type": "application/json"    
          },
          body: JSON.stringify(data)
        });

        if (problem == "List files in a zip file") {
            console.log("zip file");
            var text = await result.text();
            console.log("text:", text);
            return;
        }
        else {

            var d;
            try {
                d = await result.json();
            } 
            catch (e) {
                console.log("ERROR:", e)
            }
        }

        showTestResult(output, d);        
        // $(output).html(JSON.stringify(d));
    });    
    
  
    // args: output element, data
    function showTestResult(output, d) {
        if (!d) {
            return;
        }
        console.log("showTestResult", d);
        function print(text) {
            $(output).append(text + "\n");
        }

        print(`Test Status: ${d.outcome} (${d.stats.passed} passed and ${d.stats.failed} failed)`)
        d.testcases.forEach((t, i) => {
            print(`\n${i+1}. ${t.name} ... ${t.outcome}`);    
            if (t.outcome == "failed") {
                print("")
                print(t.error_detail.replaceAll(/^/mg, "    "));
            }
        })
    }
  

    var submitted_result = $("#data").data("submission");
    if (submitted_result && submitted_result != "null") {
        showTestResult(".output", submitted_result)
    }

    $(e).find(".submit").click(function() {
        var problem = $(e).data("problem")
        var code = editor.getCode();
        var training = $("#data").data("training");
        var problem_set = $("#data").data("problem-set");

        var data = {
            problem_set: problem_set,
            problem: problem,
            code: code,
            author: frappe.session.user,
            training: training,
        };
        frappe.call({
            method: "engage.api.submit_practice_problem", 
            args: data,
            callback: function (r) {
                console.log("submit callback", r);
                var doc = r.message;
                var submission = doc.test_result ? JSON.parse(doc.test_result) : {};
                //showTestResult(".output", submission);

                frappe.msgprint("Successfully submitted solution for problem " + problem);     
                submissions[problem] = {problem: problem, code: code};
                updateSubmissionStatus(problem);
            }
        });
    })
  });
  
  var urlParams = new URLSearchParams(window.location.search);
  var user = urlParams.get("user") || frappe.session.user;
  
  frappe.call({
    "method": "engage.api.get_problem_set_submissions", 
    args: {
        "problem_set": problem_set,
        "user": user 
    }, 
    callback: function(r) { 
        submissions = r.message;
        updateSubmissions();
    }
  });

    
  
  $(`.list-group-item[data-user="${user}"]`).addClass("active")

  $('a.user.list-group-item').click(function() {
      var user = $(this).data("user");
      window.location.search = `review=true&user=${user}`;
  })
  
  var review = JSON.parse($("#data").data("review") || 'null');
  if (review) {
      $(".comment-wrapper").hide();
      $(".comment-editor").show();
  }
  
  $(".save-comments").click(function() {
    var problems = [];
    $(".problem-item").each((i, p) => {
      var problem = {
        problem: $(p).data("problem"),
        comment: $(p).find(".comment-editor textarea").val(),
        correctness: $(p).find(".comment-editor .correctness").val(),
        clarity: $(p).find(".comment-editor .clarity").val()
      };
      problems.push(problem);
    }); 
    frappe.call({
        "method": "engage.api.problem_set_update_comments", 
        args: {
            problem_set: problem_set,
            user: user,
            problems: problems
        }, 
        callback: function(r) { 
            frappe.msgprint("done");
        }
    });
  });
  
  $(".next-user").click(function() {
      var user = $(".list-group-item.user.active").next().data('user');
      window.location.href = window.location.pathname + "?review=true&user=" + user
  });
});
