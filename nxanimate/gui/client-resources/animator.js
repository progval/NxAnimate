"use strict";

var graph;
var ws; /* WebSocket */
var S; /* Main Sigma.js object */
var edit_mode = false;
var selected_node = undefined; /* Candidate as edge source. */
var current_line = undefined;

/************************************************
 * Sigma events
 ************************************************/

function bind_sigma_events() {
    S.bind("clickNode", on_click_node);
    S.bind("clickStage", on_click_stage);
}

function on_click_stage(event) {
    if (!edit_mode)
        return;
    var captor = event.data.captor;
    request_add_node(captor.x, captor.y);
}

/* If a node has been clicked, select it.
 * If an other node was already selected, add an edge between the two. */
function on_click_node(event) {
    if (!edit_mode)
        return;
    var node = event.data.node;
    if (typeof selected_node == "undefined") {
        selected_node = node;
    }
    else {
        request_add_edge(selected_node.id, node.id);
        selected_node = undefined;
    }
}


/************************************************
 * Drawing and server interaction
 ************************************************/

function request_redraw_graph(ws) {
    ws.send("request_redraw_graph");
}
function redraw_graph(new_graph) {
    graph = new_graph;
    for (var node of graph.nodes) {
        S.graph.addNode(node);
    }
    for (var edge of graph.edges) {
        S.graph.addEdge(edge);
    }
    S.refresh();
}

function request_add_node(x, y) {
    ws.send("request_add_node " + JSON.stringify({"x": x, "y": y}));
    /* TODO: Create temporary node to be shown until the server
     * sends the actual edge. */
}
function add_node(node) {
    S.graph.addNode(node);
    S.refresh();
}

function request_add_edge(source, target) {
    ws.send("request_add_edge " + JSON.stringify({"source": source, "target": target}));
    /* TODO: Create temporary edge to be shown until the server
     * sends the actual edge. */
}
function add_edge(edge) {
    S.graph.addEdge(edge);
    S.refresh();
}

/************************************************
 * Debugger
 ************************************************/

function on_click_lineno() {
    /* Find which of the line numbers was clicks */
    var element = window.event.target;
    var tokens = element.id.split("-");
    var prefix=tokens[0], lineno_str=tokens[1];
    if (prefix != "lineno") {
        /* uh? */
        console.log("on_click_lineno called, but not on a lineno:")
        console.log(element)
    }
    var lineno = parseInt(lineno_str, 10);
    ws.send("flip_breakpoint " + lineno);
}

function on_add_breakpoint(arg) {
    var lineno = arg;
    var element = document.getElementById("lineno-" + lineno);
    element.classList.add("breakpoint");
}
function on_remove_breakpoint(arg) {
    var lineno = arg;
    var element = document.getElementById("lineno-" + lineno);
    element.classList.remove("breakpoint");
}

function on_click_step() {
    ws.send("step");
}

function on_click_next_breakpoint() {
    ws.send("cont");
}

function on_set_lineno(arg) {
    var lineno = arg;
    var line = document.getElementById("line-" + lineno);
    if (typeof current_line != "undefined") {
        current_line.classList.remove("highlighted-line");
    }
    line.classList.add("highlighted-line");
    current_line = line;
}

/************************************************
 * Networking
 ************************************************/

function on_socket_event(event) {
    var index = event.data.indexOf(" ");
    var event_type = event.data.substring(0, index);
    var argument = event.data.substring(index+1, event.data.length)
    console.log("Event: " + event_type);
    console.log("Argument: " + argument);
    argument = JSON.parse(argument);
    switch (event_type) {
        case "redraw_graph":
            redraw_graph(argument);
            break;
        case "add_node":
            add_node(argument);
            break;
        case "add_edge":
            add_edge(argument);
            break;
        case "set_lineno":
            on_set_lineno(argument);
            break;
        case "add_breakpoint":
            on_add_breakpoint(argument);
            break;
        case "remove_breakpoint":
            on_remove_breakpoint(argument);
            break;
        default:
            console.log("Unknown event type: " + event_type);
    }
}

function main() {
    S = new sigma({
        container: "graph-editor",
        settings: {
            autoRescale: false
            }});
    bind_sigma_events();
    ws = new WebSocket(websocket_url);
    ws.onopen = function (event) { request_redraw_graph(ws); };
    ws.onmessage = on_socket_event;
}
