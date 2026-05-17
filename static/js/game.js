let gameOver = false;
let gameId = null;
let playerColour = null;
let justMoved = false;

const socket = io();

//creates a new game and waits for an opponent to join
function createGame() {
    document.getElementById('lobbyStatus').textContent = 'Creating game...';
    fetch('/api/game/create', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            gameId = data.game_id;
            playerColour = 'white';
            document.getElementById('lobbyStatus').textContent = 'Waiting for opponent to join...';
            // Join socket room while waiting so we receive opponent_joined event
            socket.emit('join_game', { game_id: gameId });
        });
}

//joins an existing waiting game
function joinGame() {
    document.getElementById('lobbyStatus').textContent = 'Looking for a game...';
    fetch('/api/game/join', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                gameId = data.game_id;
                playerColour = 'black';
                startGame();
            } else {
                document.getElementById('lobbyStatus').textContent = 'No games available. Try creating one!';
            }
        });
}

//starts the game, shows the board and chat
function startGame() {
    document.getElementById('gameLobby').style.display = 'none';
    document.getElementById('gameArea').style.display = 'block';
    document.getElementById('chatToggleBtn').style.display = 'block';

    loadChessboard('black');
    loadChessboard('white');

    window._currentTurn = 'white';

    if (playerColour === 'black') {
        flipBoardForBlack();
    }

    socket.emit('join_game', { game_id: gameId });
    
    //get initial state
    fetch(`/api/game/${gameId}/state`)
        .then(r => r.json())
        .then(data => {
            window._currentTurn = data.current_turn;
            updateGameStatus(data);
        });
}

// Listen for board updates from server via websocket
socket.on('board_update', (data) => {
    window._currentTurn = data.current_turn;
    updateGameStatus(data);
    if (!justMoved) {
        applyBoardState(data.board_state);
        if (playerColour === 'black') {
            flipBoardForBlack();
        }
    }
    justMoved = false;
});

// Listen for game over
socket.on('game_over', (data) => {
    if (!gameOver) {
        gameOver = true;
        showGameOver(data.message);
    }
});

// Listen for new messages
socket.on('new_message', (data) => {
    if (data.sender !== currentUsername) {
        addMessage(data.content, data.sender, false);
    }
});

// Listen for opponent joining the game
socket.on('opponent_joined', (data) => {
    if (data.game_id === gameId) {
        startGame();
    }
});

function flipBoardForBlack() {
    const table = document.getElementById('ChessTable');
    table.style.transform = 'rotate(180deg)';
    
    //counter-rotate all images so pieces appear right-side up
    document.querySelectorAll('#ChessTable img').forEach(img => {
        img.style.transform = 'rotate(180deg)';
    });
    
    // Reverse rank labels
    const rankLabels = document.getElementById('rankLabels');
    rankLabels.innerHTML = '<span>1</span><span>2</span><span>3</span><span>4</span><span>5</span><span>6</span><span>7</span><span>8</span>';
    // Reverse file labels
    const fileLabels = document.getElementById('fileLabels');
    fileLabels.innerHTML = '<span>h</span><span>g</span><span>f</span><span>e</span><span>d</span><span>c</span><span>b</span><span>a</span>';

}

//updates the turn indicator and opponent status in the UI
function updateGameStatus(data) {
    if (!data) return;
    const statusEl = document.getElementById('gameStatus');
    const opponentEl = document.getElementById('opponentStatus');

    //show whose turn it is
    if (data.current_turn === playerColour) {
        statusEl.textContent = `Your turn (${playerColour})`;
    } else {
        statusEl.textContent = `Opponent's turn (${data.current_turn})`;
    }

    //show opponent name in chat header
    const opponent = playerColour === 'white' ? data.player2 : data.player1;
    if (opponent) {
        opponentEl.textContent = opponent + ' connected';
    }
}

//applies board state received from server to the local board
function applyBoardState(state) {
    const table = document.getElementById("ChessTable");

    //clear all pieces first
    Array.from(table.rows).forEach(row => {
        Array.from(row.cells).forEach(cell => {
            if (!cell.classList.contains('axis')) {
                cell.innerHTML = '';
                cell.removeAttribute('piece-type');
                cell.removeAttribute('piece-color');
                cell.removeAttribute('draggable');
                cell.removeAttribute('moved');
            }
        });
    });

    //place pieces from server state
    for (const [pos, piece] of Object.entries(state)) {
        const col = pos[0];
        const row = parseInt(pos[1]);
        const colIdx = getIntOfAlpha(col);
        const tableRowIdx = 8 - row;
        const cell = table.rows[tableRowIdx].cells[colIdx - 1];

        const svgUrl = chesspieces[piece.type][piece.color];
        cell.innerHTML = `<img src="${svgUrl}" draggable="true" style="width:100%;height:100%;display:block;">`;
        cell.setAttribute('piece-type', piece.type);
        cell.setAttribute('piece-color', piece.color);
        cell.setAttribute('draggable', 'true');
        const startingRank = piece.color === 'white' ? 2 : 7;
        cell.setAttribute('moved', row !== startingRank ? 'true' : 'false');

        // Counter-rotate image if playing as black
        if (playerColour === 'black') {
            const pieceImg = cell.querySelector('img');
            if (pieceImg) pieceImg.style.transform = 'rotate(180deg)';
        }

        cell.addEventListener('mouseenter', mouseEnter);
        cell.addEventListener('mouseleave', mouseLeave);
        const img = cell.querySelector('img');
        if (img) img.addEventListener('dragstart', dragstartHandler);
    }

    addDragFunctionality(table);
}

//shows a game over overlay with a message
function showGameOver(message) {
    const overlay = document.getElementById('gameOverOverlay');
    document.getElementById('gameOverTitle').textContent = message;
    overlay.style.display = 'flex';
    setTimeout(() => { location.href = '/'; }, 3000);
}