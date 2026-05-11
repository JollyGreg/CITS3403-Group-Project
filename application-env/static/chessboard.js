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
let dragged = null;

function getValidMoves( cell ) {
    var validMoves = []
    let chessTableElement = document.getElementById("ChessTable");
    if ( cell.innerHTML == "♙"  || cell.innerHTML == "♟" ) {
        validMoves.push( getPositionFromCell( cell.cellIndex, cell.parentNode.rowIndex - 1) );
        if (cell.getAttribute("moved") == "false") {
            validMoves.push( getPositionFromCell( cell.cellIndex, cell.parentNode.rowIndex - 2) );
        }
    }
    return validMoves;
}

function showValidMoves( validMoves ) {
    let chessTableElement = document.getElementById("ChessTable");

    for (const move of validMoves) {
        console.log( "show move:", move );
        let cell_pos = getCellFromPosition(move);
        let cell = chessTableElement.rows[ cell_pos[1] ].cells[ cell_pos[0] ];
        cell.setAttribute(`style`, `background-color : green`);
    }
}

function isValidMove( piece, move_pos ) {
    return true // placeholder, validation needs to be added
}

// function that runs when a piece is picked up
function dragstartHandler(event) {
    var cell = event.srcElement;
    console.log("Player picked up piece:", cell.innerHTML, "At", getPositionFromCell( cell.cellIndex, cell.parentNode.rowIndex ));
    dragged = event.target;
}

function mouseEnter( event ) {
    var cell = event.srcElement;
    
    console.log("Showing valid moves for:", cell.innerHTML);

    let validMoves = getValidMoves(cell);
    console.log( "Valid Moves: ", validMoves);
    showValidMoves(validMoves);
} 

function mouseLeave( event ) {
        // reset background
    let chessTableElement = document.getElementById("ChessTable");
    setAlternatingBackground(chessTableElement, "white", "grey");
}

function dragoverHandler(event) {
}

function dropHandler(event) {
    console.log("drop event");
}

// The location of the cell in the table will be different from its visual coordinate because of the reverse nature of the y axis and the offset because of the headings
function getPositionFromCell( cellIndex, rowIndex ) {
    // Position is the visual location like "f2" or "e4" for example
    return [ alpha[cellIndex - 1], ( -1 * ( rowIndex - 8) ) ]
}

// The location of the cell in the table will be different from its visual coordinate because of the reverse nature of the y axis and the offset because of the headings
function getCellFromPosition( position ) {
    // cell here refers to cell position like "5, 6" or "3, 2"
    return [ getIntOfAlpha(position[0]), ( -1 * ( position[1] - 8) ) ]
}

// gets the integer equivalent of the letter in the alphabet, only up to `h`
function getIntOfAlpha( letter ) {
    for (let x = 0; x < alpha.length; x++) {
        if (letter == alpha[x]) {
            return x+1
        }
    }
    return false
}

// creates an alternating background on the chessboard, for use when loading, uses inline css
function setAlternatingBackground( table, colour1, colour2) {
    let alternating_value = true;
    Array.from(table.rows).forEach(row => {
        Array.from(row.cells).forEach(cell => {
            const classesAsString = cell.className;

            let colour = 0;
            if (alternating_value) 
                { colour = colour1; alternating_value = false;} 
            else 
                { colour = colour2; alternating_value = true; }

            if (classesAsString != "axis") {
                cell.setAttribute(`style`, `background-color : ${colour}`);
            }
        });
    });
}

function addDragFunctionality( table ) {
    Array.from(table.rows).forEach(row => {
        Array.from(row.cells).forEach(cell => {
            cell.addEventListener("dragover", (event) => { event.preventDefault();  dragoverHandler( event ); });
            cell.addEventListener("drop", (event) => { event.preventDefault();  dropHandler( event ); });
        });
    });
}

function loadChessboard( colour ) {
    let chessTableElement = document.getElementById("ChessTable");

    // adds the chess pieces to the board
    for (const [key, value] of Object.entries(chesspieces)) {
        for (let x = 0; x < chesspieces[key][`spawn_location_${colour}`].length; x++) {
            let column = getIntOfAlpha( chesspieces[key][`spawn_location_${colour}`][x][0] );
            let row = chesspieces[key][`spawn_location_${colour}`][x][1];
            let icon = chesspieces[key][colour];

            row--; // offset from heading

            let cell = chessTableElement.rows[row].cells[column];
            cell.innerHTML = icon;
            cell.setAttribute("draggable", true);
            cell.addEventListener('mouseenter', (event) => { mouseEnter(event); });
            cell.addEventListener('mouseleave', (event) => { mouseLeave(event); });
            cell.setAttribute(`ondragstart`, `dragstartHandler( event )`);
            cell.setAttribute("moved",false);
        }
    }

    setAlternatingBackground(chessTableElement, "white", "grey");
    addDragFunctionality(chessTableElement);
}

document.addEventListener('DOMContentLoaded', function() {
    // Your JavaScript code here, executes when the DOM is ready
    console.log("DOM fully loaded and parsed!");
    loadChessboard("black");
    loadChessboard("white");
});