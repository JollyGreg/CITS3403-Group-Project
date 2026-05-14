var chesspieces = {
    "Pawn": {
        "white": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Chess_plt45.svg/60px-Chess_plt45.svg.png",
        "black": "https://upload.wikimedia.org/wikipedia/commons/c/c7/Chess_pdt45.svg",
        "spawn_location_black": [["a", 7], ["b", 7], ["c", 7], ["d", 7], ["e", 7], ["f", 7], ["g", 7], ["h", 7]],
        "spawn_location_white": [["a", 2], ["b", 2], ["c", 2], ["d", 2], ["e", 2], ["f", 2], ["g", 2], ["h", 2]]
    },
    "Rook": {
        "white": "https://upload.wikimedia.org/wikipedia/commons/7/72/Chess_rlt45.svg",
        "black": "https://upload.wikimedia.org/wikipedia/commons/f/ff/Chess_rdt45.svg",
        "spawn_location_black": [["a", 8], ["h", 8]],
        "spawn_location_white": [["a", 1], ["h", 1]]
    },
    "Horse": {
        "white": "https://upload.wikimedia.org/wikipedia/commons/7/70/Chess_nlt45.svg",
        "black": "https://upload.wikimedia.org/wikipedia/commons/e/ef/Chess_ndt45.svg",
        "spawn_location_black": [["b", 8], ["g", 8]],
        "spawn_location_white": [["b", 1], ["g", 1]]
    },
    "Bishop": {
        "white": "https://upload.wikimedia.org/wikipedia/commons/b/b1/Chess_blt45.svg",
        "black": "https://upload.wikimedia.org/wikipedia/commons/9/98/Chess_bdt45.svg",
        "spawn_location_black": [["c", 8], ["f", 8]],
        "spawn_location_white": [["c", 1], ["f", 1]]
    },
    "King": {
        "white": "https://upload.wikimedia.org/wikipedia/commons/4/42/Chess_klt45.svg",
        "black": "https://upload.wikimedia.org/wikipedia/commons/f/f0/Chess_kdt45.svg",
        "spawn_location_black": [["e", 8]],
        "spawn_location_white": [["e", 1]]
    },
    "Queen": {
        "white": "https://upload.wikimedia.org/wikipedia/commons/1/15/Chess_qlt45.svg",
        "black": "https://upload.wikimedia.org/wikipedia/commons/4/47/Chess_qdt45.svg",
        "spawn_location_black": [["d", 8]],
        "spawn_location_white": [["d", 1]]
    },
};

var alpha = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
let dragged = null; // Will hold the <img> element being dragged
let currentTurn = "white";

// ─── Coordinate helpers ───────────────────────────────────────────────────────

// Returns chess position e.g. ["f", 2] from table cellIndex / rowIndex
function getPositionFromCell(cellIndex, rowIndex) {
    return [alpha[cellIndex - 1], (-1 * (rowIndex - 8))];
}

// Returns [cellIndex, rowIndex] in the table from a chess position e.g. ["f", 2]
function getCellFromPosition(position) {
    return [getIntOfAlpha(position[0]), (-1 * (position[1] - 8))];
}

function getIntOfAlpha(letter) {
    for (let x = 0; x < alpha.length; x++) {
        if (letter === alpha[x]) return x + 1;
    }
    return false;
}

// ─── Board state helpers ──────────────────────────────────────────────────────

// Returns the <td> cell for a chess position like ["e", 4], or null if out of bounds
function getCellElement(pos) {
    const col = pos[0];
    const row = pos[1];
    if (row < 1 || row > 8) return null;
    const colIdx = getIntOfAlpha(col);
    if (!colIdx) return null;
    const table = document.getElementById("ChessTable");
    const tableRow = 8 - row; // rank 8 → row index 0, rank 1 → row index 7
    return table.rows[tableRow].cells[colIdx];
}

// Returns piece info on a cell, or null if empty
function getPieceOnCell(pos) {
    const cell = getCellElement(pos);
    if (!cell) return null;
    const type = cell.getAttribute("piece-type");
    const color = cell.getAttribute("piece-color");
    if (!type) return null;
    return { type, color, cell };
}

// Checks whether a square is on the board
function inBounds(pos) {
    const colIdx = getIntOfAlpha(pos[0]);
    return colIdx !== false && pos[1] >= 1 && pos[1] <= 8;
}

// ─── Valid move generators ────────────────────────────────────────────────────

function getValidMoves(cell) {
    const pieceType  = cell.getAttribute("piece-type");
    const pieceColor = cell.getAttribute("piece-color");
    const cellPos    = getPositionFromCell(cell.cellIndex, cell.parentNode.rowIndex);
    const col        = cellPos[0];
    const row        = cellPos[1];
    const hasMoved   = cell.getAttribute("moved") === "true";

    let moves = [];

    switch (pieceType) {
        case "Pawn":   moves = getPawnMoves(col, row, pieceColor, hasMoved);   break;
        case "Rook":   moves = getRookMoves(col, row, pieceColor);              break;
        case "Horse":  moves = getHorseMoves(col, row, pieceColor);             break;
        case "Bishop": moves = getBishopMoves(col, row, pieceColor);            break;
        case "Queen":  moves = getQueenMoves(col, row, pieceColor);             break;
        case "King":   moves = getKingMoves(col, row, pieceColor);              break;
    }

    return moves;
}

// Pawns move forward (white goes up / +row, black goes down / -row).
// They can capture diagonally, but only move straight if the square is empty.
function getPawnMoves(col, row, color, hasMoved) {
    const moves = [];
    const dir = color === "white" ? 1 : -1;
    const colIdx = getIntOfAlpha(col);

    const startingRow = color === "white" ? 2 : 7;

    const oneStep = [col, row + dir];
    if (inBounds(oneStep) && !getPieceOnCell(oneStep)) {
        moves.push(oneStep);

        const twoStep = [col, row + 2 * dir];
        if (
            row === startingRow &&
            !hasMoved &&
            inBounds(twoStep) &&
            !getPieceOnCell(twoStep)
        ) {
            moves.push(twoStep);
        }
    }

    for (const dx of [-1, 1]) {
        const newColIdx = colIdx + dx;
        if (newColIdx < 1 || newColIdx > 8) continue;

        const diagPos = [alpha[newColIdx - 1], row + dir];
        const target = getPieceOnCell(diagPos);

        if (target && target.color !== color) {
            moves.push(diagPos);
        }
    }

    return moves;
}

// Rooks slide along ranks and files, blocked by any piece, can capture enemy pieces
function getRookMoves(col, row, color) {
    return slidingMoves(col, row, color, [
        [0, 1], [0, -1], [1, 0], [-1, 0]
    ]);
}

// Bishops slide diagonally
function getBishopMoves(col, row, color) {
    return slidingMoves(col, row, color, [
        [1, 1], [1, -1], [-1, 1], [-1, -1]
    ]);
}

// Queens combine rook + bishop
function getQueenMoves(col, row, color) {
    return slidingMoves(col, row, color, [
        [0, 1], [0, -1], [1, 0], [-1, 0],
        [1, 1], [1, -1], [-1, 1], [-1, -1]
    ]);
}

// Knights jump in an L-shape
function getHorseMoves(col, row, color) {
    const moves = [];
    const colIdx = getIntOfAlpha(col);
    const offsets = [
        [2, 1], [2, -1], [-2, 1], [-2, -1],
        [1, 2], [1, -2], [-1, 2], [-1, -2]
    ];
    for (const [dc, dr] of offsets) {
        const newColIdx = colIdx + dc;
        const newRow    = row + dr;
        if (newColIdx < 1 || newColIdx > 8 || newRow < 1 || newRow > 8) continue;
        const pos = [alpha[newColIdx - 1], newRow];
        const target = getPieceOnCell(pos);
        if (!target || target.color !== color) moves.push(pos);
    }
    return moves;
}

// Kings move one square in any direction
function getKingMoves(col, row, color) {
    const moves = [];
    const colIdx = getIntOfAlpha(col);
    const offsets = [
        [0, 1], [0, -1], [1, 0], [-1, 0],
        [1, 1], [1, -1], [-1, 1], [-1, -1]
    ];
    for (const [dc, dr] of offsets) {
        const newColIdx = colIdx + dc;
        const newRow    = row + dr;
        if (newColIdx < 1 || newColIdx > 8 || newRow < 1 || newRow > 8) continue;
        const pos = [alpha[newColIdx - 1], newRow];
        const target = getPieceOnCell(pos);
        if (!target || target.color !== color) moves.push(pos);
    }
    return moves;
}

// Shared sliding logic for Rooks, Bishops, Queens
function slidingMoves(col, row, color, directions) {
    const moves  = [];
    const colIdx = getIntOfAlpha(col);
    for (const [dc, dr] of directions) {
        let c = colIdx + dc;
        let r = row + dr;
        while (c >= 1 && c <= 8 && r >= 1 && r <= 8) {
            const pos    = [alpha[c - 1], r];
            const target = getPieceOnCell(pos);
            if (target) {
                if (target.color !== color) moves.push(pos); // can capture
                break;                                        // blocked either way
            }
            moves.push(pos);
            c += dc;
            r += dr;
        }
    }
    return moves;
}

// ─── Highlighting ─────────────────────────────────────────────────────────────

function showValidMoves(validMoves) {
    for (const move of validMoves) {
        const cell = getCellElement(move);
        if (!cell) continue;

        if (getPieceOnCell(move)) {
            // Enemy piece on this square — highlight as capturable
            cell.classList.add("capture-highlight");
        } else {
            cell.classList.add("move-highlight");
        }
    }
}

function clearHighlights() {
    document.querySelectorAll(".move-highlight, .capture-highlight").forEach(cell => {
        cell.classList.remove("move-highlight", "capture-highlight");
    });
}

// ─── Mouse hover (preview moves) ─────────────────────────────────────────────

function mouseEnter(event) {
    // event.target may be the <img> inside the cell
    const cell = event.currentTarget;
    const validMoves = getValidMoves(cell);
    showValidMoves(validMoves);
}

function mouseLeave(event) {
    clearHighlights();
}

// ─── Drag & Drop (dragging the <img>) ────────────────────────────────────────

function dragstartHandler(event) {
    // event.target is the <img>
    dragged = event.target;
    const cell = dragged.parentElement;
    if (cell.getAttribute("piece-color") !== currentTurn) {
    console.log("Not this player's turn");
    event.preventDefault();
    dragged = null;
    return;
}
    console.log(
        "Picked up:", cell.getAttribute("piece-type"),
        "at", getPositionFromCell(cell.cellIndex, cell.parentNode.rowIndex)
    );
    event.dataTransfer.effectAllowed = "move";
}

function dragoverHandler(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
}

function dropHandler(event) {
     console.log('playerColour:', playerColour, 'gameId:', gameId);
    // Check if it's this player's turn
    if (playerColour && gameId) {
        if (window._currentTurn !== playerColour) {
            console.log("Not your turn!");
            dragged = null;
            return;
        }
    }    
    event.preventDefault();
    if (!dragged) return;

    const fromCell = dragged.parentElement;
    if (!fromCell) {
        dragged = null;
        return;
    }
    // The drop target might be a <td> or another <img> sitting in a <td>
    const toCell   = event.target.tagName === "IMG"
        ? event.target.parentElement
        : event.target;

    if (!toCell || toCell.tagName !== "TD") return;
    if (toCell === fromCell) return;

    // Prevent moving opponent's pieces
    const pieceColor = fromCell.getAttribute('piece-color');
    if (gameId && pieceColor !== playerColour) {
        console.log("That's not your piece!");
        dragged = null;
        return;
    }

    const fromPos = getPositionFromCell(fromCell.cellIndex, fromCell.parentNode.rowIndex);
    const toPos   = getPositionFromCell(toCell.cellIndex,   toCell.parentNode.rowIndex);

    // Check destination is a valid move for this piece
    const validMoves = getValidMoves(fromCell);
    const isValid = validMoves.some(m => m[0] === toPos[0] && m[1] === toPos[1]);
    if (!isValid) {
        console.log("Invalid move to", toPos);
        dragged = null;
        return;
    }

    console.log("Moving", fromCell.getAttribute("piece-type"), "from", fromPos, "to", toPos);
    // Save what was on the destination cell BEFORE moving
    const capturedType = toCell.getAttribute('piece-type');

    // Move piece to destination cell
    toCell.innerHTML = fromCell.innerHTML;
    toCell.setAttribute("piece-type",  fromCell.getAttribute("piece-type"));
    toCell.setAttribute("piece-color", fromCell.getAttribute("piece-color"));
    toCell.setAttribute("draggable",   "true");
    toCell.setAttribute("moved", "true");

    // Re-attach events on destination cell
    toCell.addEventListener('mouseenter', (e) => { mouseEnter(e); });
    toCell.addEventListener('mouseleave', (e) => { mouseLeave(e); });

    // Re-attach dragstart to the new img
    const newImg = toCell.querySelector("img");
    if (newImg) {
        newImg.setAttribute("draggable", "true");
        newImg.addEventListener("dragstart", dragstartHandler);
    }

    // Clear origin cell
    fromCell.innerHTML = "";
    fromCell.removeAttribute("piece-type");
    fromCell.removeAttribute("piece-color");
    fromCell.removeAttribute("draggable");
    fromCell.removeAttribute("moved");
    fromCell.replaceWith(fromCell.cloneNode(false)); // removes old event listeners
    currentTurn = currentTurn === "white" ? "black" : "white";
    console.log("Current turn:", currentTurn);

    clearHighlights();

    // If king was captured end the game
    if (capturedType === 'King') {
        if (gameId) {
            const boardState = captureBoardState();
            fetch(`/api/game/${gameId}/move`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ board_state: boardState })
            })
            .then(() => fetch(`/api/game/${gameId}/end`, { method: 'POST' }))
            .then(() => {
                showGameOver(`Game over! ${playerColour} wins!`);
            });
        }
        dragged = null;
        return;
    }

    // Send board state to server after a valid move
    if (gameId) {
        const boardState = captureBoardState();
        fetch(`/api/game/${gameId}/move`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ board_state: boardState })
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                window._currentTurn = data.current_turn;
                justMoved = true;
            }
        });
    }

    dragged = null;
}

// ─── Board setup ─────────────────────────────────────────────────────────────

function addDragFunctionality(table) {
    Array.from(table.rows).forEach(row => {
        Array.from(row.cells).forEach(cell => {
            cell.addEventListener("dragover",  (e) => { e.preventDefault(); dragoverHandler(e); });
            cell.addEventListener("drop",      (e) => { e.preventDefault(); dropHandler(e); });
        });
    });
}

function loadChessboard(colour) {
    const table = document.getElementById("ChessTable");

    for (const [key] of Object.entries(chesspieces)) {
        const locations = chesspieces[key][`spawn_location_${colour}`];
        for (let x = 0; x < locations.length; x++) {
            const colLetter  = locations[x][0];
            const rank       = locations[x][1];          // chess rank 1–8
            const svgUrl     = chesspieces[key][colour];

            const colIdx     = getIntOfAlpha(colLetter); // 1-based column index
            const tableRowIdx = 8 - rank;                // rank 8 → row 0, rank 1 → row 7

            const cell = table.rows[tableRowIdx].cells[colIdx];

            // Build the img — draggable=true on the img itself, pointer-events:none removed
            cell.innerHTML = `<img src="${svgUrl}" draggable="true" style="width:100%;height:100%;display:block;">`;
            cell.setAttribute("piece-type",  key);
            cell.setAttribute("piece-color", colour);
            cell.setAttribute("draggable",   "true"); // kept for attribute reads
            cell.setAttribute("moved",       "false");

            cell.addEventListener('mouseenter', mouseEnter);
            cell.addEventListener('mouseleave', mouseLeave);

            // Attach dragstart directly to the img
            const img = cell.querySelector("img");
            img.addEventListener("dragstart", dragstartHandler);
        }
    }

    addDragFunctionality(table);
}

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded!");
    // Board is loaded by game.js when game starts
});

// Captures the current board state as a JSON object for server sync
function captureBoardState() {
    const table = document.getElementById("ChessTable");
    const state = {};
    Array.from(table.rows).forEach(row => {
        Array.from(row.cells).forEach(cell => {
            const type = cell.getAttribute("piece-type");
            const color = cell.getAttribute("piece-color");
            if (type && color) {
                const pos = getPositionFromCell(cell.cellIndex, cell.parentNode.rowIndex);
                state[`${pos[0]}${pos[1]}`] = { type, color };
            }
        });
    });
    return state;
}