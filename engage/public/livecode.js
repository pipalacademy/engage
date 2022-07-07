

LIVECODE_CODEMIRROR_OPTIONS = {
  common: {
    lineNumbers: true,
    keyMap: "sublime",
    matchBrackets: true,
    indentWithTabs: false,
    tabSize: 4,
    indentUnit: 4,
    extraKeys: {
      Tab: (cm) => {
        cm.somethingSelected()
          ? cm.execCommand('indentMore')
          : cm.execCommand('insertSoftTab');
      }
    }
  },
  python: {
    mode: "python"
  }
}

class WriterInterface {
  constructor() {
  }

  beforeRun() {
  }

  afterRun(output) {
  }

  beforeRunTests() {
  }

  afterRunTests(result) {
  }
}

class DefaultWriter extends WriterInterface {
  constructor(element) {
    super();

    this.elementOutput = element.querySelector(".output");
    this.elementResults = element.querySelector(".output");
  }

  beforeRun() {
    this.reset();
  }

  afterRun(output) {
    this.writeOutput(output);
  }

  beforeRunTests() {
    this.reset();
  }

  afterRunTests(result) {
    this.writeResult(result);
  }

  // privately used methods
  reset() {
    this.clearOutput();
    this.clearResults();
  }

  clearOutput() {
    if (this.elementOutput) {
      this.elementOutput.innerHTML = "";
    }
  }

  clearResults() {
    if (this.elementResults) {
      this.elementResults.innerHTML = "";
    }
  }

  writeOutput(data) {
    // escape HTML
    var html = new Option(data).innerHTML;

    if (this.elementOutput) {
      this.elementOutput.innerHTML += html;
    }
  }

  writeResult(d) {
    var result = this.elementResults;
    function print(text) {
      $(result).append(text + "\n");
    }

    print(`Test Status: ${d.outcome} (${d.stats.passed} passed and ${d.stats.failed} failed)`)
    d.testcases.forEach((t, i) => {
      print(`\n${i + 1}. ${t.name} ... ${t.outcome}`);
      if (t.outcome == "failed") {
        print("")
        print(t.error_detail.replaceAll(/^/mg, "    "));
      }
    })
  }
}

// Initialized the editor and all controls.
// It is expected that the given element is a parent element
// with textarea, div.output, button.run optionally canvas.canvas
// elements in it.
class LiveCodeEditor {
  constructor(element, options) {
    this.options = options;
    this.parent = element;

    this.base_url = options.base_url;
    this.runtime = options.runtime;

    this.problem = options.problem;

    this.elementCode = options.elementCode || this.parent.querySelector(".code");
    this.elementRun = options.elementRun || this.parent.querySelector(".run");
    this.elementRunTests = options.elementRunTests || this.parent.querySelector(".run-tests");
    this.elementClear = options.elementClear || this.parent.querySelector(".clear");
    this.elementReset = options.elementReset || this.parent.querySelector(".reset");
    this.elementArguments = options.elementArguments || this.parent.querySelector(".arguments");

    let defaultWriter = new DefaultWriter(this.parent);
    this.writer = options.writer || defaultWriter; // implements WriterInterface

    this.codemirror = null;
    this.setupActions()
  }
  run() {
    this.triggerEvent("beforeRun");
    this.writer.beforeRun();

    var args = $(this.elementArguments).val().trim();
    frappe.call('engage.livecode.execute', {
      problem: this.problem,
      code: this.getCode(),
      args: args
    })
      .then(r => {
        var msg = r.message;
        this.writer.afterRun(msg.output);
      })
  }
  runTests() {
    this.writer.beforeRunTests();

    frappe.call('engage.livecode.run_tests', {
      problem: this.problem,
      code: this.getCode(),
    })
      .then(r => {
        var msg = r.message;
        this.writer.afterRunTests(msg);
      })
  }
  triggerEvent(name) {
    var events = this.options.events;
    if (events && events[name]) {
      events[name](this);
    }
  }
  setupActions() {
    this.elementRun.onclick = () => this.run();
    if (this.elementClear) {
      this.elementClear.onclick = () => this.triggerEvent("clear");
    }
    if (this.elementReset) {
      this.elementReset.onclick = () => this.triggerEvent("reset");
    }

    if (this.options.codemirror) {
      const options = {
        ...LIVECODE_CODEMIRROR_OPTIONS.common,
        ...LIVECODE_CODEMIRROR_OPTIONS[this.runtime]
      }
      if (this.options.codemirror instanceof Object) {
        options = { ...options, ...this.options.codemirror }
      }
      options.extraKeys['Cmd-Enter'] = () => this.run()
      options.extraKeys['Ctrl-Enter'] = () => this.run()

      this.codemirror = CodeMirror.fromTextArea(this.elementCode, options)
    }

    $(this.elementRunTests).click(() => {
      this.runTests();
    });
  }

  getCode() {
    if (this.codemirror) {
      var code = this.codemirror.doc.getValue()
      return code.replaceAll("\t", " ".repeat(this.codemirror.options.indentUnit))
    }
    else {
      return this.elementCode.value;
    }
  }

}
