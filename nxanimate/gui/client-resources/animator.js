"use strict";

var graph;
var ws; /* WebSocket */
var network; /* Main vis-network object */
var edit_mode = false;
var selected_node = undefined; /* Candidate as edge source. */
var current_line = undefined;

/************************************************
 * vis.js events
 ************************************************/

function bind_vis_events() {
    network.on("click", on_click);
    network.on("stabilized", on_stabilized);
}

function on_click(event) {
    if (!edit_mode)
        return;
    if (event.nodes.length == 1) {
        on_click_node(event.nodes[0]);
    }
    else if (event.nodes.length > 1) {
        console.log("Clicked multiple nodes, what should I do?"); // TODO
    }
    else if (event.edges.length) {
        console.log("Clicks on edges not handled yet."); // TODO
    }
    else {
        request_add_node(event.pointer.canvas.x, event.pointer.canvas.y);
    }

}

/* If a node has been clicked, select it.
 * If an other node was already selected, add an edge between the two. */
function on_click_node(node) {
    if (typeof selected_node == "undefined") {
        selected_node = node;
    }
    else {
        request_add_edge(selected_node, node);
        selected_node = undefined;
    }
}

function on_stabilized(event) {
    var coordinates = network.getPositions();
    ws.send("move_nodes " + JSON.stringify(coordinates));
}


/************************************************
 * Drawing and server interaction
 ************************************************/

function request_redraw_graph(ws) {
    ws.send("request_redraw_graph");
}
function redraw_graph(new_graph) {
    graph = {
        nodes: new vis.DataSet(new_graph.nodes),
        edges: new vis.DataSet(new_graph.edges),
    };
    var options = {};
    network = new vis.Network(
            document.getElementById("graph-editor"),
            graph,
            options);
    bind_vis_events();
}

function request_add_node(x, y) {
    ws.send("request_add_node " + JSON.stringify({"x": x, "y": y}));
    /* TODO: Create temporary node to be shown until the server
     * sends the actual edge. */
}
function add_node(node) {
    graph.nodes.add(node);
}
function update_node(nodes) {
    graph.nodes.update(nodes);
}
function remove_node(node) {
    graph.nodes.remove(node);
}

function request_add_edge(from, to) {
    ws.send("request_add_edge " + JSON.stringify({"from": from, "to": to}));
    /* TODO: Create temporary edge to be shown until the server
     * sends the actual edge. */
}
function add_edge(edge) {
    graph.edges.add(edge);
}
function remove_edge(edge) {
    graph.edges.remove(edge);
}

/************************************************
 * Debugger
 ************************************************/

function on_click_lineno(event) {
    /* Find which of the line numbers was clicks */
    var element = event.target;
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
        case "update_node":
            update_node(argument);
            break;
        case "remove_node":
            remove_node(argument);
            break;
        case "add_edge":
            add_edge(argument);
            break;
        case "remove_edge":
            remove_edge(argument);
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
    ws = new WebSocket(websocket_url);
    ws.onopen = function (event) { request_redraw_graph(ws); };
    ws.onmessage = on_socket_event;
    document.getElementById("linenos").addEventListener("click", on_click_lineno);
}
