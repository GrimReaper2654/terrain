// Connect to Flask WebSocket server
const socket = io("http://localhost:6969");

// Player object
let player = {
    x: 100,
    y: 100,
    speed: 100, // Base speed in pixels per second
    stats: {
        speed: 100  // Placeholder for player's speed stat
    }
};
wd
// Track pressed keys
let keys = {};

// Track last frame time for smooth movement
let lastUpdate = performance.now();

// Terrain-based movement penalties (future feature)
const terrainSpeeds = {
    "normal": 1.0,   // Normal terrain (no penalty)
    "sand": 0.75,     // Slower movement
    "water": 0.33,    // Much slower
    "path": 1.2       // Faster movement
};

const slopeSpeeds = {
    "upHalf": 0.8,
    "downHalf": 1.1,
    "upFull": 0.5,
    "downFull": 1.25,
};

// Handle reset position event from the server
socket.on("resetPosition", (data) => {
    if (data.playerID === "Player1") {
        player.x = data.position.x;
        player.y = data.position.y;
        console.log("Position reset by server due to invalid movement.");
    }
});

// Game loop (60 FPS)
function gameLoop(timestamp) {
    let deltaTime = (timestamp - lastUpdate) / 1000; // Convert ms to seconds
    lastUpdate = timestamp;

    updatePlayer(deltaTime);
    renderGame();

    requestAnimationFrame(gameLoop);
}

// Function to send player actions to the server
function sendPacket(type, payload) {
    const packet = {
        playerID: "player1",
        payload: payload,
        timestamp: Date.now()  // Current time in milliseconds since the Epoch
    };
    socket.emit(type, packet);
}

// Update player movement
function updatePlayer(deltaTime) {
    let terrainType = "normal"; // Placeholder until terrain is implemented
    let speedModifier = terrainSpeeds[terrainType]; // Adjust movement speed

    if (keys["arrowup"] || keys["w"]) player.y -= player.stats.speed * speedModifier * deltaTime;
    if (keys["arrowdown"] || keys["s"]) player.y += player.stats.speed * speedModifier * deltaTime;
    if (keys["arrowleft"] || keys["a"]) player.x -= player.stats.speed * speedModifier * deltaTime;
    if (keys["arrowright"] || keys["d"]) player.x += player.stats.speed * speedModifier * deltaTime;

    sendPacket("playerMove", {x: player.x, y: player.y});
}

// Render player on canvas
function renderGame() {
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    // Clear screen
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw player
    ctx.fillStyle = "blue";
    ctx.fillRect(player.x, player.y, 20, 20);
}

// Handle key events
document.addEventListener("keydown", (event) => keys[event.key.toLowerCase()] = true);
document.addEventListener("keyup", (event) => keys[event.key.toLowerCase()] = false);

// Start the game loop
requestAnimationFrame(gameLoop);
