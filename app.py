import streamlit as st

st.set_page_config(page_title="Python Running After Cash", layout="wide")

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
<canvas id="gameCanvas" width="1000" height="500"></canvas>
<div class="info">
    <span>💰 Cash: <span id="scoreDisplay">0</span> / 5</span>
    &nbsp;&nbsp;&nbsp;
    <span id="statusMessage">🐍 Jump to catch money!</span>
</div>

<script>
    (function() {
        // ---------- DOM elements ----------
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreSpan = document.getElementById('scoreDisplay');
        const statusSpan = document.getElementById('statusMessage');

        // ---------- Game constants ----------
        const W = 1000, H = 500;
        const GROUND_Y = H - 50;
        const SNAKE_W = 45, SNAKE_H = 45;
        const MONEY_W = 30, MONEY_H = 30;
        const CAR_W = 70, CAR_H = 45;

        // ---------- Game state ----------
        let snake = { x: 60, y: GROUND_Y - SNAKE_H, vy: 0, onGround: true, score: 0 };
        let moneyBags = [
            { x: 300, y: GROUND_Y - 80, collected: false },
            { x: 550, y: GROUND_Y - 110, collected: false },
            { x: 800, y: GROUND_Y - 70, collected: false },
            { x: 1050, y: GROUND_Y - 100, collected: false },
            { x: 1300, y: GROUND_Y - 90, collected: false }
        ];
        let cars = [];
        let carSpawnCounter = 0;
        let gameOver = false;
        let win = false;
        let animationId = null;
        let allCollected = false;
        let autoMoveSpeed = 3.5;
        let finishLineX = 1450;
        
        // For automatic restart after hit
        let hitTimer = null;

        // ---------- Sound (simple beep using Web Audio) ----------
        let audioCtx = null;
        function playBell() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.frequency.value = 880;
            gain.gain.value = 0.2;
            osc.type = 'sine';
            osc.start();
            gain.gain.exponentialRampToValueAtTime(0.00001, audioCtx.currentTime + 0.3);
            osc.stop(audioCtx.currentTime + 0.3);
        }

        function updateScoreUI() {
            scoreSpan.textContent = `${snake.score} / ${moneyBags.length}`;
        }

        function checkAllCollected() {
            return moneyBags.every(b => b.collected);
        }

        // ---------- Reset game fully ----------
        function fullReset() {
            // cancel any pending restart
            if (hitTimer) clearTimeout(hitTimer);
            snake = { x: 60, y: GROUND_Y - SNAKE_H, vy: 0, onGround: true, score: 0 };
            moneyBags = [
                { x: 300, y: GROUND_Y - 80, collected: false },
                { x: 550, y: GROUND_Y - 110, collected: false },
                { x: 800, y: GROUND_Y - 70, collected: false },
                { x: 1050, y: GROUND_Y - 100, collected: false },
                { x: 1300, y: GROUND_Y - 90, collected: false }
            ];
            cars = [];
            carSpawnCounter = 0;
            gameOver = false;
            win = false;
            allCollected = false;
            snake.score = 0;
            updateScoreUI();
            statusSpan.innerText = "🐍 Jump to catch money!";
            if (audioCtx && audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
        }

        // ---------- Game logic update ----------
        function updateGame() {
            if (gameOver || win) return;

            // Snake physics
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

            // Auto move right
            if (!allCollected) {
                snake.x += autoMoveSpeed;
                if (snake.x < 0) snake.x = 0;
            }

            // Car spawning
            carSpawnCounter++;
            if (carSpawnCounter > 85 && !allCollected) {
                carSpawnCounter = 0;
                cars.push({ x: W, y: GROUND_Y - CAR_H, w: CAR_W, h: CAR_H });
            }
            for (let i = 0; i < cars.length; i++) {
                cars[i].x -= 7;
                if (cars[i].x + CAR_W < 0) {
                    cars.splice(i,1);
                    i--;
                }
            }

            // Collision with car -> trigger restart
            for (let car of cars) {
                if (snake.x < car.x + CAR_W &&
                    snake.x + SNAKE_W > car.x &&
                    snake.y < car.y + CAR_H &&
                    snake.y + SNAKE_H > car.y) {
                    gameOver = true;
                    statusSpan.innerText = "💥 Hit by car! Restarting...";
                    // Automatic restart after 0.8 seconds
                    hitTimer = setTimeout(() => {
                        fullReset();
                        gameOver = false;
                        win = false;
                        statusSpan.innerText = "🐍 Jump to catch money!";
                    }, 800);
                    return;
                }
            }

            // Money collection
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

            // Check all collected
            allCollected = checkAllCollected();
            if (allCollected) {
                statusSpan.innerText = "🎉 All money collected! Run to the finish line! 🎉";
                if (snake.x + SNAKE_W >= finishLineX) {
                    win = true;
                    statusSpan.innerText = "🏆 Congratulations! Pythoneer! 🏆";
                }
            } else {
                win = false;
            }

            if (allCollected && snake.x + SNAKE_W >= finishLineX) {
                win = true;
                statusSpan.innerText = "🏆 Congratulations! Pythoneer! 🏆";
            }
        }

        // ---------- Drawing ----------
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
            
            if (allCollected) {
                ctx.beginPath();
                ctx.moveTo(finishLineX, 0);
                ctx.lineTo(finishLineX, H);
                ctx.lineWidth = 5;
                ctx.strokeStyle = "blue";
                ctx.stroke();
                ctx.fillStyle = "blue";
                ctx.font = "bold 18px monospace";
                ctx.fillText("FINISH", finishLineX-45, H/2);
            }
            
            // Money bags
            for (let m of moneyBags) {
                if (!m.collected) {
                    ctx.fillStyle = "#FFD700";
                    ctx.fillRect(m.x, m.y, MONEY_W, MONEY_H);
                    ctx.fillStyle = "#000";
                    ctx.font = "bold 20px monospace";
                    ctx.fillText("$", m.x+8, m.y+22);
                }
            }
            
            // Cars
            for (let car of cars) {
                ctx.fillStyle = "#FF4500";
                ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
                ctx.fillStyle = "#333";
                ctx.fillRect(car.x+15, car.y+30, 15, 15);
                ctx.fillRect(car.x+40, car.y+30, 15, 15);
                ctx.fillStyle = "#555";
                ctx.fillRect(car.x+20, car.y+8, 30, 25);
            }
            
            // Snake
            ctx.fillStyle = "#2E8B57";
            ctx.fillRect(snake.x, snake.y, SNAKE_W, SNAKE_H);
            ctx.fillStyle = "white";
            ctx.fillRect(snake.x+10, snake.y+10, 10, 10);
            ctx.fillRect(snake.x+25, snake.y+10, 10, 10);
            ctx.fillStyle = "black";
            ctx.fillRect(snake.x+12, snake.y+12, 5, 5);
            ctx.fillRect(snake.x+27, snake.y+12, 5, 5);
            ctx.beginPath();
            ctx.moveTo(snake.x+SNAKE_W, snake.y+SNAKE_H/2);
            ctx.lineTo(snake.x+SNAKE_W+12, snake.y+SNAKE_H/2-6);
            ctx.lineTo(snake.x+SNAKE_W+12, snake.y+SNAKE_H/2+6);
            ctx.fillStyle = "red";
            ctx.fill();
            
            if (gameOver && !win) {
                ctx.font = "bold 28px monospace";
                ctx.fillStyle = "red";
                ctx.fillText("GAME OVER – RESTARTING...", W/2-180, H/2);
            }
            if (win) {
                ctx.font = "bold 28px monospace";
                ctx.fillStyle = "gold";
                ctx.fillText("Congratulations! Pythoneer!", W/2-210, H/2-40);
                // Balloons
                for (let i=0; i<12; i++) {
                    ctx.fillStyle = `hsl(${Date.now()/20 + i*30}, 70%, 60%)`;
                    ctx.beginPath();
                    ctx.ellipse(120 + i*70, H-100 - Math.sin(Date.now()/300 + i)*25, 18, 24, 0, 0, Math.PI*2);
                    ctx.fill();
                    ctx.beginPath();
                    ctx.moveTo(120 + i*70, H-100);
                    ctx.lineTo(120 + i*70 - 4, H-75);
                    ctx.lineTo(120 + i*70 + 4, H-75);
                    ctx.fill();
                }
            }
        }

        function gameLoop() {
            updateGame();
            draw();
            requestAnimationFrame(gameLoop);
        }

        // ---------- Jump ----------
        function jump() {
            if (gameOver || win) return;
            if (snake.onGround) {
                snake.vy = -12;
                snake.onGround = false;
            }
        }

        // ---------- Event listeners ----------
        window.addEventListener('keydown', function(e) {
            if (e.code === 'Space' || e.code === 'ArrowUp') {
                e.preventDefault();
                jump();
            }
        });
        
        // Start
        fullReset();
        gameLoop();
    })();
</script>
"""

st.components.v1.html(game_html, height=560, scrolling=False)
