HTMLElement.prototype.get_value = function () {
    if (this instanceof HTMLTextAreaElement) {
        return this.value;
    }
    if (this instanceof HTMLInputElement) {
        const type = this.getAttribute("type");
        if (type === "checkbox") {
            return this.checked;
        } else if (type === "number") {
            return this.valueAsNumber;
        } else {
            return ""+this.value;
        }
    }
    if (this instanceof HTMLSelectElement) {
        return this.value;
    }
    return "";
}

HTMLElement.prototype.set_value = function (x) {
    if (this instanceof HTMLTextAreaElement) {
        this.value = x;
    }
    if (this instanceof HTMLInputElement) {
        if (this.getAttribute("type") === "checkbox") {
            this.checked = x;
        } else {
            this.value = x;
        }
    }
    if (this instanceof HTMLSelectElement) {
        this.value = x;
    }
}