const STATE_VISIBLE = true
const STATE_HIDDEN = false

class Toggle {
    constructor(selector) {
        let el = $(selector)
        let data = el.data()

        this.$element = $(selector)
        this.$target = $(data.target)
        this.showText = data.showText
        this.hideText = data.hideText
        this.state = STATE_HIDDEN

        this.setup()
    }

    setup() {
        this.$element.html(this.showText)

        var toggle = this

        this.$element.click(function () {
            toggle.state == STATE_HIDDEN ? toggle.show() : toggle.hide()
        })
    }

    hide() {
        this.$target.hide()
        this.$element.html(this.showText)
        this.state = STATE_HIDDEN
    }

    show() {
        this.$target.show()
        this.$element.html(this.hideText)
        this.state = STATE_VISIBLE
    }
}

$(function () {
    let _archivedTrainingsToggle = new Toggle("#archived-trainings-toggle")
})

