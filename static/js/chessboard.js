let dragInProgress = false;

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
let chessGameOver = false;
let gameMessageTimeout = null;

function showGameMessage(message) {
    let messageBox = document.getElementById("game-status-message");

    if (!messageBox) {
        messageBox = document.createElement("div");
        messageBox.id = "game-status-message";

        messageBox.style.position = "fixed";
        messageBox.style.top = "90px";
        messageBox.style.left = "50%";
        messageBox.style.transform = "translateX(-50%)";
        messageBox.style.zIndex = "9999";

        messageBox.style.padding = "12px 20px";
        messageBox.style.border = "1px solid #3b82f6";
        messageBox.style.borderRadius = "10px";
        messageBox.style.backgroundColor = "#1f2937";
        messageBox.style.color = "#ffffff";
        messageBox.style.fontWeight = "600";
        messageBox.style.textAlign = "center";
        messageBox.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.25)";
        messageBox.style.maxWidth = "600px";

        document.body.appendChild(messageBox);
    }

    messageBox.textContent = message;
    messageBox.style.display = "block";

    if (gameMessageTimeout) {
        clearTimeout(gameMessageTimeout);
    }

    gameMessageTimeout = setTimeout(() => {
        messageBox.style.display = "none";
        gameMessageTimeout = null;
    }, 3000);
}

// ─── Coordinate helpers ───────────────────────────────────────────────────────

// Returns chess position e.g. ["f", 2] from table cellIndex / rowIndex
function getPositionFromCell(cellIndex, rowIndex) {
    return [alpha[cellIndex], (-1 * (rowIndex - 8))];
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
    return table.rows[tableRow].cells[colIdx - 1];
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

function promotePawnIfNeeded(cell) {
    const pieceType = cell.getAttribute("piece-type");
    const pieceColor = cell.getAttribute("piece-color");

    if (pieceType !== "Pawn") return;

    const position = getPositionFromCell(cell.cellIndex, cell.parentNode.rowIndex);
    const row = position[1];

    const reachedPromotionRank =
        (pieceColor === "white" && row === 8) ||
        (pieceColor === "black" && row === 1);

    if (!reachedPromotionRank) return;

    let choice = prompt("Promote pawn to Queen, Rook, Bishop, or Horse?", "Queen");

    if (!choice) {
        choice = "Queen";
    }

    choice = choice.trim().toLowerCase();

    const promotionMap = {
        queen: "Queen",
        rook: "Rook",
        bishop: "Bishop",
        horse: "Horse",
        knight: "Horse"
    };

    const promotedPiece = promotionMap[choice] || "Queen";

    cell.setAttribute("piece-type", promotedPiece);

    const img = cell.querySelector("img");
    if (img) {
        img.src = chesspieces[promotedPiece][pieceColor];
    }

    showGameMessage(pieceColor + " pawn promoted to " + promotedPiece + "!");
}

// ─── King safety helpers ─────────────────────────────────────────────

function findKing(color) {
    for (let row = 1; row <= 8; row++) {
        for (let col of alpha) {
            const piece = getPieceOnCell([col, row]);
            if (piece && piece.type === "King" && piece.color === color) {
                return [col, row];
            }
        }
    }
    return null;
}

function isKingInCheck(color) {
    const kingPos = findKing(color);
    if (!kingPos) return false;

    for (let row = 1; row <= 8; row++) {
        for (let col of alpha) {
            const piece = getPieceOnCell([col, row]);

            if (piece && piece.color !== color) {
                const moves = getValidMoves(piece.cell);

                if (moves.some(m => m[0] === kingPos[0] && m[1] === kingPos[1])) {
                    return true;
                }
            }
        }
    }

    return false;
}

function hasAnyLegalMove(color) {
    for (let row = 1; row <= 8; row++) {
        for (let col of alpha) {
            const piece = getPieceOnCell([col, row]);

            if (piece && piece.color === color) {
                const fromCell = piece.cell;
                const moves = getValidMoves(fromCell);

                for (const move of moves) {
                    const toCell = getCellElement(move);

                    if (!toCell) continue;

                    const movingColor = fromCell.getAttribute("piece-color");

                    const fromState = {
                        html: fromCell.innerHTML,
                        type: fromCell.getAttribute("piece-type"),
                        color: fromCell.getAttribute("piece-color"),
                        draggable: fromCell.getAttribute("draggable"),
                        moved: fromCell.getAttribute("moved")
                    };

                    const toState = {
                        html: toCell.innerHTML,
                        type: toCell.getAttribute("piece-type"),
                        color: toCell.getAttribute("piece-color"),
                        draggable: toCell.getAttribute("draggable"),
                        moved: toCell.getAttribute("moved")
                    };

                    // simulate move
                    toCell.innerHTML = fromState.html;
                    toCell.setAttribute("piece-type", fromState.type);
                    toCell.setAttribute("piece-color", fromState.color);
                    toCell.setAttribute("draggable", fromState.draggable || "true");
                    toCell.setAttribute("moved", "true");

                    fromCell.innerHTML = "";
                    fromCell.removeAttribute("piece-type");
                    fromCell.removeAttribute("piece-color");
                    fromCell.removeAttribute("draggable");
                    fromCell.removeAttribute("moved");

                    const stillInCheck = isKingInCheck(movingColor);

                    // restore origin
                    fromCell.innerHTML = fromState.html;
                    fromCell.setAttribute("piece-type", fromState.type);
                    fromCell.setAttribute("piece-color", fromState.color);
                    fromCell.setAttribute("draggable", fromState.draggable || "true");
                    fromCell.setAttribute("moved", fromState.moved || "false");

                    // restore destination
                    toCell.innerHTML = toState.html;
                    if (toState.type) {
                        toCell.setAttribute("piece-type", toState.type);
                        toCell.setAttribute("piece-color", toState.color);
                        toCell.setAttribute("draggable", toState.draggable || "true");
                        toCell.setAttribute("moved", toState.moved || "false");
                    } else {
                        toCell.removeAttribute("piece-type");
                        toCell.removeAttribute("piece-color");
                        toCell.removeAttribute("draggable");
                        toCell.removeAttribute("moved");
                    }

                    if (!stillInCheck) {
                        return true;
                    }
                }
            }
        }
    }

    return false;
}

function isCheckmate(color) {
    return isKingInCheck(color) && !hasAnyLegalMove(color);
}

function isStalemate(color) {
    return !isKingInCheck(color) && !hasAnyLegalMove(color);
}

function isInsufficientMaterial() {
    const pieces = [];

    for (let row = 1; row <= 8; row++) {
        for (let col of alpha) {
            const piece = getPieceOnCell([col, row]);
            if (piece) {
                pieces.push(piece);
            }
        }
    }

    return pieces.length === 2 &&
        pieces.every(piece => piece.type === "King");
}

function checkGameEndState() {
    if (chessGameOver) return;

    const turnToCheck = window._currentTurn || currentTurn;

    if (isInsufficientMaterial()) {
        lockBoardAfterCheckmate();
        showGameMessage("Draw by insufficient material.");
        return;
    }


    if (turnToCheck && isCheckmate(turnToCheck)) {
        lockBoardAfterCheckmate();
        showGameMessage(turnToCheck + " is checkmated!");
    } else if (turnToCheck && isStalemate(turnToCheck)) {
        lockBoardAfterCheckmate();
        showGameMessage("Stalemate! The game is a draw.");
    }
    
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

function lockBoardAfterCheckmate() {
    chessGameOver = true;
    clearHighlights();

    document.querySelectorAll("#ChessTable img").forEach(img => {
        img.setAttribute("draggable", "false");
    });
}

// ─── Mouse hover (preview moves) ─────────────────────────────────────────────

function mouseEnter(event) {
    if (chessGameOver) return;

    const cell = event.currentTarget;

    if (playerColour && cell.getAttribute('piece-color') !== playerColour) return;

    const validMoves = getValidMoves(cell);
    showValidMoves(validMoves);
}

function mouseLeave(event) {
    clearHighlights();
}

// ─── Drag & Drop (dragging the <img>) ────────────────────────────────────────

function dragstartHandler(event) {
    if (chessGameOver) {
    event.preventDefault();
    return;
    } 

    dragInProgress = true;

    // event.target is the <img>
    dragged = event.target;

    // Handle case where drag fires on TD instead of IMG
    const fromCell = dragged.tagName === 'TD' ? dragged : dragged.parentElement;
    if (!fromCell || fromCell.tagName !== 'TD') {
        dragged = null;
        return;
    }  
        
    //in a multiplayer game, only allow moving your own colour
    if (playerColour && gameId) {
        if (fromCell.getAttribute("piece-color") !== playerColour) {
            event.preventDefault();
            dragged = null;
            return;
        }
        if (window._currentTurn !== playerColour) {
            event.preventDefault();
            dragged = null;
            return;
        }
    }

    console.log(
        "Picked up:", fromCell.getAttribute("piece-type"),
        "at", getPositionFromCell(fromCell.cellIndex, fromCell.parentNode.rowIndex)
    );
    event.dataTransfer.effectAllowed = "move";
}

function dragoverHandler(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
}

function dropHandler(event) {
    // sync local turn with server turn
    if (window._currentTurn) {
        currentTurn = window._currentTurn;
    }

    if (chessGameOver) {
    event.preventDefault();
    dragged = null;
    dragInProgress = false;
    return;
    }

    // Check if it's this player's turn
    if (playerColour && gameId) {
        if (window._currentTurn !== playerColour) {
            console.log("Not your turn!");
            dragged = null;
            dragInProgress = false;
            return;
        }
    }    
    event.preventDefault();
    if (!dragged) return;

    const fromCell = dragged.tagName === 'TD' ? dragged : dragged.parentElement;
    if (!fromCell || fromCell.tagName !== 'TD') {
        dragged = null;
        dragInProgress = false;
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
        dragInProgress = false;
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
        dragInProgress = false;
        return;
    }
    const movingColor = fromCell.getAttribute("piece-color");

const fromState = {
    html: fromCell.innerHTML,
    type: fromCell.getAttribute("piece-type"),
    color: fromCell.getAttribute("piece-color"),
    draggable: fromCell.getAttribute("draggable"),
    moved: fromCell.getAttribute("moved")
};

const toState = {
    html: toCell.innerHTML,
    type: toCell.getAttribute("piece-type"),
    color: toCell.getAttribute("piece-color"),
    draggable: toCell.getAttribute("draggable"),
    moved: toCell.getAttribute("moved")
};

// Simulate move, clear destination first
toCell.innerHTML = "";
toCell.removeAttribute("piece-type");
toCell.removeAttribute("piece-color");
toCell.removeAttribute("draggable");
toCell.removeAttribute("moved");

// Then place the moving piece
toCell.innerHTML = fromState.html;
toCell.setAttribute("piece-type", fromState.type);
toCell.setAttribute("piece-color", fromState.color);
toCell.setAttribute("draggable", fromState.draggable || "true");
toCell.setAttribute("moved", "true");

fromCell.innerHTML = "";
fromCell.removeAttribute("piece-type");
fromCell.removeAttribute("piece-color");
fromCell.removeAttribute("draggable");
fromCell.removeAttribute("moved");

const leavesKingInCheck = isKingInCheck(movingColor);

// Restore origin cell
fromCell.innerHTML = fromState.html;
fromCell.setAttribute("piece-type", fromState.type);
fromCell.setAttribute("piece-color", fromState.color);
fromCell.setAttribute("draggable", fromState.draggable || "true");
fromCell.setAttribute("moved", fromState.moved || "false");

// Restore destination cell
toCell.innerHTML = toState.html;
if (toState.type) {
    toCell.setAttribute("piece-type", toState.type);
    toCell.setAttribute("piece-color", toState.color);
    toCell.setAttribute("draggable", toState.draggable || "true");
    toCell.setAttribute("moved", toState.moved || "false");
} else {
    toCell.removeAttribute("piece-type");
    toCell.removeAttribute("piece-color");
    toCell.removeAttribute("draggable");
    toCell.removeAttribute("moved");
}

if (leavesKingInCheck) {
    showGameMessage("You cannot make a move that leaves your king in check.");
    dragged = null;
    dragInProgress = false;
    return;
}

    // Save what was on the destination cell BEFORE moving
    const capturedType = toCell.getAttribute('piece-type');

    // Move piece to destination cell
    toCell.innerHTML = fromCell.innerHTML;
    toCell.setAttribute("piece-type",  fromCell.getAttribute("piece-type"));
    toCell.setAttribute("piece-color", fromCell.getAttribute("piece-color"));
    toCell.setAttribute("draggable",   "true");
    toCell.setAttribute("moved", "true");

    promotePawnIfNeeded(toCell);

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
    currentTurn = currentTurn === "white" ? "black" : "white";
    console.log("Current turn:", currentTurn);

    // Check if opponent is now in check

    if (isInsufficientMaterial()) {
        lockBoardAfterCheckmate();
        showGameMessage("Draw by insufficient material.");
        clearHighlights();
        dragged = null;
        dragInProgress = false;
        return;
    }

    if (isCheckmate(currentTurn)) {
        lockBoardAfterCheckmate();
        showGameMessage(currentTurn + " is checkmated!");
    } else if (isKingInCheck(currentTurn)) {
        showGameMessage(currentTurn + " king is in check!");
    }

    clearHighlights();

    // Re-attach mouse events to all cells with pieces
    Array.from(document.getElementById('ChessTable').rows).forEach(row => {
        Array.from(row.cells).forEach(cell => {
            if (cell.getAttribute('piece-type')) {
                cell.addEventListener('mouseenter', mouseEnter);
                cell.addEventListener('mouseleave', mouseLeave);
                const img = cell.querySelector('img');
                if (img) img.addEventListener('dragstart', dragstartHandler);
            }
        });
    });

    // If king was captured end the game
    if (capturedType === 'King') {
        if (gameId) {
            const boardState = captureBoardState();
            socket.emit('make_move', { game_id: gameId, board_state: boardState });
            socket.emit('end_game', { game_id: gameId, winner: playerColour });
            showGameOver(`Game over! ${playerColour} wins!`);
        }
        dragged = null;
        dragInProgress = false;
        return;
    }

    // Send board state to server after a valid move
    if (gameId) {
        const boardState = captureBoardState();
        socket.emit('make_move', { game_id: gameId, board_state: boardState });
        justMoved = true;
    }

    dragged = null;
    dragInProgress = false;
}

// ─── Board setup ─────────────────────────────────────────────────────────────

function addDragFunctionality(table) {
    if (table._dragListenersAdded) return;
    table._dragListenersAdded = true;
    table.addEventListener("dragstart", (e) => {
        dragstartHandler(e);
    });
    table.addEventListener("dragover", (e) => { 
        e.preventDefault(); 
        dragoverHandler(e); 
    });
    table.addEventListener("drop", (e) => { 
        e.preventDefault(); 
        dropHandler(e); 
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

            const cell = table.rows[tableRowIdx].cells[colIdx - 1];

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

setInterval(() => {
    if (dragInProgress) return;
    const table = document.getElementById("ChessTable");

    if (!table || chessGameOver) return;

    const hasPieces = document.querySelector("#ChessTable img");
    if (!hasPieces) return;

    checkGameEndState();
}, 1000);
