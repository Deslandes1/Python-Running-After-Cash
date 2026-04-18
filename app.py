import streamlit as st

st.set_page_config(page_title="Python Running After Cash", layout="wide")

st.markdown("""
<style>
    body { margin: 0; overflow: hidden; background-color: #f0f0f0; }
    canvas { display: block; margin: 0 auto; border: 4px solid #2E8B57; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); cursor: pointer; background: #87CEEB; }
    .info { text-align: center; font-family: 'Courier New', Courier, monospace; font-size: 1.5rem; margin-top: 15px; font-weight: bold; color: #2E8B57; }
    .focus-note { text-align: center; color: #d63031; font-size: 1rem; margin-top: 5px; animation: blink 1.5s infinite; }
    @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.3; } 100% { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h1 style="color: #2E8B57;">🐍 Python Running After Cash 💰</h1>
    <p style="font-size: 1.2rem;">Press <strong>SPACE</strong> or <strong>UP ARROW</strong> to jump. Catch the bags in the air!</p>
    <p class="focus-note">⚠️ Click the game screen to enable controls ⚠️</p>
</div>
""", unsafe_allow_html=True)

game_html = """
<canvas id="gameCanvas" width="1000" height="500" tabindex="0" style="outline: none;"></canvas>
<div class="info">
    <span>💰 Collected: <span id="scoreDisplay">0</span> / 5</span>
    &nbsp;&nbsp;&nbsp;
    <span id="statusMessage">🐍 Ready to Run!</span>
</div>

<script>
    (function() {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreSpan = document.getElementById('scoreDisplay');
        const statusSpan = document.getElementById('statusMessage');

        const W = 1000, H = 500;
        const GROUND_Y = H - 50;
        const SNAKE_W = 60, SNAKE_H = 30;
        
        let snake = { x: 80, y: GROUND_Y - SNAKE_H, vy: 0, onGround: true, score: 0, wiggle: 0 };
        let moneyBags = [
            { x: 400, y: GROUND_Y - 180, collected: false },
            { x: 700, y: GROUND_Y - 220, collected: false },
            { x: 1000, y: GROUND_Y - 150, collected: false },
            { x: 1300, y: GROUND_Y - 250, collected: false },
            { x: 1600, y: GROUND_Y - 190, collected: false }
        ];
        let obstacles = [];
        let spawnTimer = 0;
        let gameOver = false;
        let win = false;
        let finishLineX = 1800;

        function drawSnake(x, y, wiggle) {
            ctx.save();
            ctx.translate(x, y);
            
            // Snake Body Segments
            ctx.fillStyle = "#2E8B57";
            for (let i = 0; i < 5; i++) {
                let segmentWiggle = Math.sin(wiggle + (i * 0.8)) * 8;
                ctx.beginPath();
                ctx.ellipse(0 - (i * 12), 15 + segmentWiggle, 12, 10, 0, 0, Math.PI * 2);
                ctx.fill();
                // Patterns
                ctx.fillStyle = "#1F6B3A";
                ctx.beginPath();
                ctx.arc(0 - (i * 12), 15 + segmentWiggle, 3, 0, Math.PI * 2);
                ctx.fill();
                ctx.fillStyle = "#2E8B57";
            }

            // Head
            ctx.fillStyle = "#3CB371";
            ctx.beginPath();
            ctx.ellipse(10, 12, 18, 14, 0, 0, Math.PI * 2);
            ctx.fill();

            // Eyes
            ctx.fillStyle = "white";
            ctx.beginPath(); ctx.arc(15, 8, 5, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = "black";
            ctx.beginPath(); ctx.arc(17, 8, 2.5, 0, Math.PI * 2); ctx.fill();

            // Tongue
            ctx.strokeStyle = "red";
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(25, 15);
            ctx.lineTo(35, 12 + Math.sin(wiggle * 2) * 5);
            ctx.stroke();

            ctx.restore();
        }

        function drawMoneyBag(x, y) {
            ctx.fillStyle = "#8B4513"; // Brown bag
            ctx.beginPath();
            ctx.moveTo(x, y);
            ctx.quadraticCurveTo(x + 15, y - 10, x + 30, y);
            ctx.lineTo(x + 35, y + 35);
            ctx.lineTo(x - 5, y + 35);
            ctx.fill();
            // Tie
            ctx.strokeStyle = "#FFD700";
            ctx.lineWidth = 3;
            ctx.strokeRect(x + 5, y + 5, 20, 2);
            // Dollar Sign
            ctx.fillStyle = "#FFD700";
            ctx.font = "bold 16px Arial";
            ctx.fillText("$", x + 10, y + 25);
        }

        function update() {
            if (gameOver || win) return;

            // Physics
            snake.vy += 0.7;
            snake.y += snake.vy;
            if (snake.y > GROUND_Y - SNAKE_H) {
                snake.y = GROUND_Y - SNAKE_H;
                snake.vy = 0;
                snake.onGround = true;
            }
            
            snake.x += 4; // Constant run speed
            snake.wiggle += 0.2;

            // Obstacles (Red Spheres/Spikes)
            spawnTimer++;
            if (spawnTimer > 100) {
                obstacles.push({ x: snake.x + 800, y: GROUND_Y - 40 });
                spawnTimer = 0;
            }

            obstacles.forEach((obs, index) => {
                if (Math.abs(snake.x - obs.x) < 40 && Math.abs(snake.y - obs.y) < 40) {
                    gameOver = true;
                    statusSpan.innerText = "💥 Ouch! Try Again!";
                    setTimeout(reset, 1500);
                }
            });

            // Money Collection
            moneyBags.forEach(bag => {
                if (!bag.collected && Math.abs(snake.x - bag.x) < 40 && Math.abs(snake.y - bag.y) < 50) {
                    bag.collected = true;
                    snake.score++;
                    scoreSpan.innerText = snake.score;
                }
            });

            if (snake.score >= 5 && snake.x > finishLineX) {
                win = true;
                statusSpan.innerText = "🏆 YOU GOT THE CASH! 🏆";
            }
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            
            // Sky & Clouds
            ctx.fillStyle = "#87CEEB";
            ctx.fillRect(0, 0, W, H);

            // Ground
            ctx.fillStyle = "#556B2F";
            ctx.fillRect(0, GROUND_Y, W, 50);

            // Scrolling view
            ctx.save();
            ctx.translate(-snake.x + 100, 0);

            // Finish Line
            ctx.fillStyle = "gold";
            ctx.fillRect(finishLineX, 0, 10, GROUND_Y);

            moneyBags.forEach(bag => { if (!bag.collected) drawMoneyBag(bag.x, bag.y); });
            obstacles.forEach(obs => {
                ctx.fillStyle = "red";
                ctx.beginPath();
                ctx.arc(obs.x, obs.y + 15, 20, 0, Math.PI * 2);
                ctx.fill();
            });

            drawSnake(snake.x, snake.y, snake.wiggle);
            ctx.restore();

            if (gameOver) {
                ctx.fillStyle = "rgba(0,0,0,0.5)";
                ctx.fillRect(0,0,W,H);
                ctx.fillStyle = "white";
                ctx.font = "40px Arial";
                ctx.fillText("CRASHED!", W/2 - 100, H/2);
            }
            
            requestAnimationFrame(() => { update(); draw(); });
        }

        function reset() {
            snake = { x: 80, y: GROUND_Y - SNAKE_H, vy: 0, onGround: true, score: 0, wiggle: 0 };
            moneyBags.forEach(b => b.collected = false);
            obstacles = [];
            gameOver = false;
            win = false;
            scoreSpan.innerText = "0";
            statusSpan.innerText = "🐍 Running...";
        }

        window.addEventListener('keydown', (e) => {
            if ((e.code === 'Space' || e.code === 'ArrowUp') && snake.onGround) {
                snake.vy = -16;
                snake.onGround = false;
                e.preventDefault();
            }
        });

        draw();
    })();
</script>
"""

st.components.v1.html(game_html, height=600)
