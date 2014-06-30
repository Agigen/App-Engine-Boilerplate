(function(agigen) {
"use strict";

var Example, debug;

debug = (function(doDebug) {
    return doDebug ? console.log.bind(console) : function() {};
})(false);

Example = (function() {
    function Example (argument) {
        this.argument = argument;
    }

    Example.prototype.printLine = function(line) {
        debug('Printing line', line);
        console.log(line);
    };

    return Example;
}());

agigen.Example = Example;

}(window.agigen || (window.agigen = {})));
