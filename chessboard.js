var chesspieces = {
    "Pawn": {"white" : "♙", "black":"♟", 
        "spawn_location_black" : [ ["a", 7], ["b", 7], ["c", 7], ["d", 7], ["e", 7], ["f", 7], ["g", 7], ["h", 7] ],
        "spawn_location_white" : [ ["a", 2], ["b", 2], ["c", 2], ["d", 2], ["e", 2], ["f", 2], ["g", 2], ["h", 2] ]},
    "Rook": {"white" : "♖", "black":"♜",
        "spawn_location_black" : [["a", 8], ["h", 8]],
        "spawn_location_white" : [["a", 1], ["h", 1]]},
    "Horse": {"white" : "♘", "black":"♞",
        "spawn_location_black" : [["b", 8], ["g", 8]],
        "spawn_location_white" : [["b", 1], ["g", 1]]},
    "Bishop": {"white" : "♗", "black":"♝",
        "spawn_location_black" : [["c", 8], ["f", 8]],
        "spawn_location_white" : [["c", 1], ["f", 1]]},
    "King": {"white" : "♔", "black":"♚",
        "spawn_location_black" : [["e", 8]],
        "spawn_location_white" : [["e", 1]]},
    "Queen": {"white" : "♕", "black":"♛",
        "spawn_location_black" : [["d", 8]],
        "spawn_location_white" : [["d", 1]]},
}
var alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];

function displayValidMoves( cell ) {

}

function dragstartHandler(event) {
    console.log("Picked up Piece", event.srcElement.innerHTML)
    console.log(event);
}

function dragoverHandler(event) {
ev.preventDefault();
}

function dropHandler(event) {
    console.log("hello")
}

function getIntOfAlpha( letter ) {
    for (let x = 0; x < alpha.length; x++) {
        if (letter == alpha[x]) {
            return x+1
        }
    }
    return false
}

function loadChessboard( colour ) {
    let chessTableElement = document.getElementById("ChessTable");

    for (const [key, value] of Object.entries(chesspieces)) {
        for (let x = 0; x < chesspieces[key][`spawn_location_${colour}`].length; x++) {
            let column = getIntOfAlpha( chesspieces[key][`spawn_location_${colour}`][x][0] );
            let row = chesspieces[key][`spawn_location_${colour}`][x][1];
            let icon = chesspieces[key][colour];

            row--; // offset from heading

            let cell = chessTableElement.rows[row].cells[column]
            cell.innerHTML = icon
            cell.setAttribute("draggable", true)
            cell.setAttribute("ondragstart", "dragstartHandler(event)")
            cell.setAttribute("ondrop", "dropHandler(event)")
        }
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Your JavaScript code here, executes when the DOM is ready
    console.log("DOM fully loaded and parsed!");
    loadChessboard("black");
    loadChessboard("white");
    
});