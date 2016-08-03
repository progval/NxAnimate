"use strict";

var graph;
var S; /* Main Sigma.js object */

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

function on_socket_event(event) {
    var index = event.data.indexOf(" ");
    var event_type = event.data.substring(0, index);
    var argument = event.data.substring(index+1, event.data.length)
    console.log("Event: " + event_type);
    console.log("Argument: " + argument);
    switch (event_type) {
        case "redraw_graph":
            redraw_graph(JSON.parse(argument));
            break;
        default:
            console.log("Unknown event type: " + event_type);
    }
}

function main() {
    S = new sigma('graph-editor');
    var ws = new WebSocket(websocket_url);
    ws.onopen = function (event) { request_redraw_graph(ws); };
    ws.onmessage = on_socket_event;
}
