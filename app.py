import streamlit as st

st.set_page_config(page_title="Python Running After Cash", layout="centered")

st.markdown("""
<style>
    body { margin: 0; overflow: hidden; }
    canvas { display: block; margin: 0 auto; border: 2px solid #333; box-shadow: 0 0 10px rgba(0,0,0,0.2); }
    .info { text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; }
    button { background: #4CAF50; border: none; color: white; padding: 10px 20px; text-align: center; font-size: 16px; margin: 10px; cursor: pointer; border-radius: 8px; }
    button:hover { background: #45a049; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h1>🐍 Python Running After Cash 💰</h1>
    <p>Press <strong>SPACE</strong> or <strong>UP ARROW</strong> to jump. Collect all 5 money bags, avoid the red car, and reach the finish line!</p>
</div>
""", unsafe_allow_html=True)

game_html = """
<canvas id="gameCanvas" width="800" height="400"></canvas>
<div class="info">
    <span>💰 Cash: <span id="scoreDisplay">0</span> / 5</span>
    &nbsp;&nbsp;&nbsp;
    <span id="statusMessage">🐍 Jump to catch money!</span>
</div>
<div style="text-align: center;">
    <button id="restartButton">🔄 Restart Game</button>
</div>

<script>
    (function() {
        // ---------- DOM elements ----------
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreSpan = document.getElementById('scoreDisplay');
        const statusSpan = document.getElementById('statusMessage');

        // ---------- Game constants ----------
        const W = 800, H = 400;
        const GROUND_Y = H - 40;
        const SNAKE_W = 40, SNAKE_H = 40;
        const MONEY_W = 25, MONEY_H = 25;
        const CAR_W = 60, CAR_H = 40;

        // ---------- Game state ----------
        let snake = { x: 50, y: GROUND_Y - SNAKE_H, vy: 0, onGround: true, score: 0 };
        let moneyBags = [
            { x: 250, y: GROUND_Y - 70, collected: false },
            { x: 450, y: GROUND_Y - 100, collected: false },
            { x: 650, y: GROUND_Y - 60, collected: false },
            { x: 850, y: GROUND_Y - 90, collected: false },
            { x: 1050, y: GROUND_Y - 80, collected: false }
        ];
        let cars = [];
        let carSpawnCounter = 0;
        let gameOver = false;
        let win = false;
        let animationId = null;
        let lastTimestamp = 0;
        let finishLineX = 1200;
        let allCollected = false;
        
        // For automatic walking (snake moves right automatically)
        let autoMoveSpeed = 3;

        // ---------- Sound (simple beep using Web Audio) ----------
        let audioCtx = null;
        function playBell() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            // resume if suspended (browser policy)
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.frequency.value = 880; // A5
            gain.gain.value = 0.2;
            osc.type = 'sine';
            osc.start();
            gain.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + 0.3);
            osc.stop(audioCtx.currentTime + 0.3);
        }

        // ---------- Helper functions ----------
        function updateScoreUI() {
            scoreSpan.textContent = `${snake.score} / ${moneyBags.length}`;
        }

        function checkAllCollected() {
            return moneyBags.every(b => b.collected);
        }

        // ---------- Game logic update ----------
        function updateGame() {
            if (gameOver || win) return;

            // 1. Snake physics (jump)
            snake.vy += 0.8;
            snake.y += snake.vy;
            if (snake.y >= GROUND_Y - SNAKE_H) {
                snake.y = GROUND_Y - SNAKE_H;
                snake.vy = 0;
                snake.onGround = true;
            } else {
                snake.onGround = false;
            }
            if (snake.y < 0) {
                snake.y = 0;
                snake.vy = 0;
            }

            // 2. Auto move right (only if not all collected yet)
            if (!allCollected) {
                snake.x += autoMoveSpeed;
                if (snake.x < 0) snake.x = 0;
            }

            // 3. Car spawning and movement
            carSpawnCounter++;
            if (carSpawnCounter > 90 && !allCollected) { // every ~1.5 sec
                carSpawnCounter = 0;
                cars.push({ x: W, y: GROUND_Y - CAR_H, w: CAR_W, h: CAR_H });
            }
            for (let i = 0; i < cars.length; i++) {
                cars[i].x -= 6;
                if (cars[i].x + CAR_W < 0) {
                    cars.splice(i,1);
                    i--;
                }
            }

            // 4. Collision with car
            for (let car of cars) {
                if (snake.x < car.x + CAR_W &&
                    snake.x + SNAKE_W > car.x &&
                    snake.y < car.y + CAR_H &&
                    snake.y + SNAKE_H > car.y) {
                    gameOver = true;
                    statusSpan.innerText = "💀 Game Over! Press Restart.";
                    return;
                }
            }

            // 5. Money collection
            for (let i=0; i<moneyBags.length; i++) {
                let m = moneyBags[i];
                if (!m.collected &&
                    snake.x < m.x + MONEY_W &&
                    snake.x + SNAKE_W > m.x &&
                    snake.y < m.y + MONEY_H &&
                    snake.y + SNAKE_H > m.y) {
                    m.collected = true;
                    snake.score++;
                    playBell();
                    updateScoreUI();
                }
            }

            // 6. Check if all collected
            allCollected = checkAllCollected();
            if (allCollected) {
                statusSpan.innerText = "🎉 All money collected! Run to the finish line! 🎉";
                // If snake passes finish line, win
                if (snake.x + SNAKE_W >= finishLineX) {
                    win = true;
                    statusSpan.innerText = "🏆 Congratulations! Pythoneer! 🏆";
                }
            } else {
                // if not all collected, ensure win is false
                win = false;
            }

            // 7. Win condition (already checked above)
            if (allCollected && snake.x + SNAKE_W >= finishLineX) {
                win = true;
                statusSpan.innerText = "🏆 Congratulations! Pythoneer! 🏆";
            }
        }

        // ---------- Drawing functions ----------
        function draw() {
            ctx.clearRect(0, 0, W, H);
            // Sky
            ctx.fillStyle = "#87CEEB";
            ctx.fillRect(0, 0, W, H);
            // Ground
            ctx.fillStyle = "#8B5A2B";
            ctx.fillRect(0, GROUND_Y, W, H - GROUND_Y);
            ctx.fillStyle = "#654321";
            ctx.fillRect(0, GROUND_Y+5, W, 5);
            
            // Finish line (if all collected)
            if (allCollected) {
                ctx.beginPath();
                ctx.moveTo(finishLineX, 0);
                ctx.lineTo(finishLineX, H);
                ctx.lineWidth = 5;
                ctx.strokeStyle = "blue";
                ctx.stroke();
                ctx.fillStyle = "blue";
                ctx.font = "bold 16px monospace";
                ctx.fillText("FINISH", finishLineX-40, H/2);
            }
            
            // Draw money bags
            for (let m of moneyBags) {
                if (!m.collected) {
                    ctx.fillStyle = "#FFD700";
                    ctx.fillRect(m.x, m.y, MONEY_W, MONEY_H);
                    ctx.fillStyle = "#000";
                    ctx.font = "bold 16px monospace";
                    ctx.fillText("$", m.x+6, m.y+18);
                }
            }
            
            // Draw cars
            for (let car of cars) {
                ctx.fillStyle = "#FF4500";
                ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
                ctx.fillStyle = "#333";
                ctx.fillRect(car.x+10, car.y+25, 15, 15);
                ctx.fillRect(car.x+35, car.y+25, 15, 15);
                ctx.fillStyle = "#555";
                ctx.fillRect(car.x+15, car.y+5, 30, 20);
            }
            
            // Draw snake (green rectangle with eyes)
            ctx.fillStyle = "#2E8B57";
            ctx.fillRect(snake.x, snake.y, SNAKE_W, SNAKE_H);
            ctx.fillStyle = "white";
            ctx.fillRect(snake.x+8, snake.y+8, 8, 8);
            ctx.fillRect(snake.x+24, snake.y+8, 8, 8);
            ctx.fillStyle = "black";
            ctx.fillRect(snake.x+10, snake.y+10, 4, 4);
            ctx.fillRect(snake.x+26, snake.y+10, 4, 4);
            // Tongue
            ctx.beginPath();
            ctx.moveTo(snake.x+SNAKE_W, snake.y+SNAKE_H/2);
            ctx.lineTo(snake.x+SNAKE_W+10, snake.y+SNAKE_H/2-5);
            ctx.lineTo(snake.x+SNAKE_W+10, snake.y+SNAKE_H/2+5);
            ctx.fillStyle = "red";
            ctx.fill();
            
            // Game over text
            if (gameOver) {
                ctx.font = "bold 30px monospace";
                ctx.fillStyle = "red";
                ctx.fillText("GAME OVER", W/2-100, H/2);
            }
            if (win) {
                ctx.font = "bold 24px monospace";
                ctx.fillStyle = "gold";
                ctx.fillText("Congratulations! Pythoneer!", W/2-180, H/2-30);
                // Draw some balloons
                for (let i=0; i<10; i++) {
                    ctx.fillStyle = `hsl(${Date.now()/20 + i*36}, 70%, 60%)`;
                    ctx.beginPath();
                    ctx.ellipse(100 + i*70, H-80 - Math.sin(Date.now()/300 + i)*20, 15, 20, 0, 0, Math.PI*2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.moveTo(100 + i*70, H-80);
                    ctx.lineTo(100 + i*70 - 3, H-60);
                    ctx.lineTo(100 + i*70 + 3, H-60);
                    ctx.fill();
                }
            }
        }

        // ---------- Game loop ----------
        function gameLoop() {
            updateGame();
            draw();
            if (!gameOver && !win) {
                requestAnimationFrame(gameLoop);
            } else {
                // if game over or win, keep drawing but stop updates? We still loop but no movement.
                // Actually we still call loop to allow restart button to reset.
                requestAnimationFrame(gameLoop);
            }
        }

        // ---------- Jump control ----------
        function jump() {
            if (gameOver || win) return;
            if (snake.onGround) {
                snake.vy = -11;
                snake.onGround = false;
            }
        }

        // ---------- Restart function ----------
        function restartGame() {
            // Reset state
            snake = { x: 50, y: GROUND_Y - SNAKE_H, vy: 0, onGround: true, score: 0 };
            moneyBags = [
                { x: 250, y: GROUND_Y - 70, collected: false },
                { x: 450, y: GROUND_Y - 100, collected: false },
                { x: 650, y: GROUND_Y - 60, collected: false },
                { x: 850, y: GROUND_Y - 90, collected: false },
                { x: 1050, y: GROUND_Y - 80, collected: false }
            ];
            cars = [];
            carSpawnCounter = 0;
            gameOver = false;
            win = false;
            allCollected = false;
            snake.score = 0;
            updateScoreUI();
            statusSpan.innerText = "🐍 Jump to catch money!";
            // Restart audio context if needed
            if (audioCtx && audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        // ---------- Event listeners ----------
        window.addEventListener('keydown', function(e) {
            if (e.code === 'Space' || e.code === 'ArrowUp') {
                e.preventDefault();
                jump();
            }
        });
        document.getElementById('restartButton').addEventListener('click', function() {
            restartGame();
        });
        
        // Start the game
        restartGame();  // initial reset to correct values
        gameLoop();
    })();
</script>
"""

st.components.v1.html(game_html, height=480, scrolling=False)
