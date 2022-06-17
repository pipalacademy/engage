

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

// Initialized the editor and all controls.
// It is expected that the given element is a parent element
// with textarea, div.output, button.run optionally canvas.canvas
// elements in it.
class LiveCodeEditor {
  constructor(element, options) {
    this.options = options;
    this.parent = element;

    console.log("LiveCodeEditor", this.options);

    this.base_url = options.base_url;
    this.runtime = options.runtime;

    this.problem = options.problem;

    this.elementCode = this.parent.querySelector(".code");
    this.elementOutput = this.parent.querySelector(".output");
    this.elementRun = this.parent.querySelector(".run");
    this.elementClear = this.parent.querySelector(".clear");
    this.elementReset = this.parent.querySelector(".reset");
    this.codemirror = null;
    this.setupActions()
  }
  reset() {
    this.clearOutput();
  }
  run() {
    this.triggerEvent("beforeRun");
    this.reset();

    console.log("run", this.problem, this.getCode());
    frappe.call('engage.livecode.execute', {
      problem: this.problem,
      code: this.getCode()
    })
    .then(r => {
      var msg = r.message;
      this.writeOutput(msg.output);
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
        options = {...options, ...this.options.codemirror}
      }
      options.extraKeys['Cmd-Enter'] = () => this.run()
      options.extraKeys['Ctrl-Enter'] = () => this.run()

      this.codemirror = CodeMirror.fromTextArea(this.elementCode, options)
    }
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

  clearOutput() {
    if (this.elementOutput) {
      this.elementOutput.innerHTML = "";
    }
  }

  writeOutput(data) {
    // escape HTML
    var html = new Option(data).innerHTML;

    if (this.elementOutput) {
      this.elementOutput.innerHTML += html;
    }
  }
}
