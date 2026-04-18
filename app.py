import streamlit as st

st.set_page_config(page_title="Python Running After Cash", layout="wide")

st.markdown("""
<style>
    body { margin: 0; overflow: hidden; }
    canvas { display: block; margin: 0 auto; border: 2px solid #333; box-shadow: 0 0 10px rgba(0,0,0,0.2); cursor: pointer; }
    .info { text-align: center; font-family: monospace; font-size: 1.2rem; margin-top: 10px; }
    .focus-note { text-align: center; color: #666; font-size: 0.9rem; margin-top: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center;">
    <h1>🐍 Python Running After Cash 💰</h1>
    <p>Press <strong>SPACE</strong> or <strong>UP ARROW</strong> to jump. Collect all 5 money bags, avoid the red car, and reach the finish line!</p>
    <p class="focus-note">⚠️ Click on the game area first to activate keyboard controls ⚠️</p>
</div>
""", unsafe_allow_html=True)

game_html = """
<canvas id="gameCanvas" width="1000" height="500" tabindex="0" style="outline: none;"></canvas>
<div class="info">
    <span>💰 Cash: <span id="scoreDisplay">0</span> / 5</span>
    &nbsp;&nbsp;&nbsp;
    <span id="statusMessage">🐍 Click here then press SPACE/UP to jump!</span>
</div>

<script>
    (function() {
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');
        const scoreSpan = document.getElementById('scoreDisplay');
        const statusSpan = document.getElementById('statusMessage');

        const W = 1000, H = 500;
        const GROUND_Y = H - 50;
        const SNAKE_W = 45, SNAKE_H = 45;
        const MONEY_W = 30, MONEY_H = 30;
        const CAR_W = 70, CAR_H = 45;

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
        let allCollected = false;
        let autoMoveSpeed = 3.5;
        let finishLineX = 1450;
        let hitTimer = null;
        let audioCtx = null;

        function playBell() {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();
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

        function fullReset() {
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
            statusSpan.innerText = "🐍 Click then press SPACE/UP to jump!";
        }

        function drawSnake(x, y, w, h) {
            ctx.fillStyle = "#2E8B57";
            ctx.beginPath();
            ctx.ellipse(x + w/2, y + h/2, w/2, h/2, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = "#3CB371";
            ctx.beginPath();
            ctx.ellipse(x + w/2, y + h/1.8, w/2.5, h/3, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = "#2E8B57";
            ctx.beginPath();
            ctx.ellipse(x + w - 5, y + h/2, w/2.2, h/2.2, 0, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = "white";
            ctx.beginPath();
            ctx.arc(x + w - 12, y + h/2 - 8, 6, 0, Math.PI*2);
            ctx.arc(x + w - 28, y + h/2 - 8, 6, 0, Math.PI*2);
            ctx.fill();
            ctx.fillStyle = "black";
            ctx.beginPath();
            ctx.arc(x + w - 14, y + h/2 - 9, 3, 0, Math.PI*2);
            ctx.arc(x + w - 30, y + h/2 - 9, 3, 0, Math.PI*2);
            ctx.fill();
            ctx.beginPath();
            ctx.moveTo(x + w, y + h/2);
            ctx.lineTo(x + w + 12, y + h/2 - 6);
            ctx.lineTo(x + w + 12, y + h/2 + 6);
            ctx.fillStyle = "red";
            ctx.fill();
            ctx.fillStyle = "#1F6B3A";
            for (let i = 0; i < 8; i++) {
                ctx.beginPath();
                ctx.arc(x + 10 + i*5, y + h - 8, 2, 0, Math.PI*2);
                ctx.fill();
            }
        }

        function updateGame() {
            if (gameOver || win) return;

            snake.vy += 0.8;
            snake.y += snake.vy;
            if (snake.y >= GROUND_Y - SNAKE_H) {
                snake.y = GROUND_Y - SNAKE_H;
                snake.vy = 0;
                snake.onGround = true;
            } else {
                snake.onGround = false;
            }
            if (snake.y < 0) { snake.y = 0; snake.vy = 0; }

            if (!allCollected) {
                snake.x += autoMoveSpeed;
                if (snake.x < 0) snake.x = 0;
            }

            carSpawnCounter++;
            if (carSpawnCounter > 85 && !allCollected) {
                carSpawnCounter = 0;
                cars.push({ x: W, y: GROUND_Y - CAR_H });
            }
            for (let i = 0; i < cars.length; i++) {
                cars[i].x -= 7;
                if (cars[i].x + CAR_W < 0) { cars.splice(i,1); i--; }
            }

            for (let car of cars) {
                if (snake.x < car.x + CAR_W && snake.x + SNAKE_W > car.x &&
                    snake.y < car.y + CAR_H && snake.y + SNAKE_H > car.y) {
                    gameOver = true;
                    statusSpan.innerText = "💥 Hit by car! Restarting...";
                    hitTimer = setTimeout(() => { fullReset(); gameOver = false; win = false; statusSpan.innerText = "🐍 Click then press SPACE/UP to jump!"; }, 800);
                    return;
                }
            }

            for (let m of moneyBags) {
                if (!m.collected && snake.x < m.x + MONEY_W && snake.x + SNAKE_W > m.x &&
                    snake.y < m.y + MONEY_H && snake.y + SNAKE_H > m.y) {
                    m.collected = true;
                    snake.score++;
                    playBell();
                    updateScoreUI();
                }
            }

            allCollected = checkAllCollected();
            if (allCollected) {
                statusSpan.innerText = "🎉 All money collected! Run to the finish line! 🎉";
                if (snake.x + SNAKE_W >= finishLineX) { win = true; statusSpan.innerText = "🏆 Congratulations! Pythoneer! 🏆"; }
            } else { win = false; }
            if (allCollected && snake.x + SNAKE_W >= finishLineX) { win = true; statusSpan.innerText = "🏆 Congratulations! Pythoneer! 🏆"; }
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            ctx.fillStyle = "#87CEEB";
            ctx.fillRect(0, 0, W, H);
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

            for (let m of moneyBags) {
                if (!m.collected) {
                    ctx.fillStyle = "#FFD700";
                    ctx.fillRect(m.x, m.y, MONEY_W, MONEY_H);
                    ctx.fillStyle = "#000";
                    ctx.font = "bold 20px monospace";
                    ctx.fillText("$", m.x+8, m.y+22);
                }
            }

            for (let car of cars) {
                ctx.fillStyle = "#FF4500";
                ctx.fillRect(car.x, car.y, CAR_W, CAR_H);
                ctx.fillStyle = "#333";
                ctx.fillRect(car.x+15, car.y+30, 15, 15);
                ctx.fillRect(car.x+40, car.y+30, 15, 15);
                ctx.fillStyle = "#555";
                ctx.fillRect(car.x+20, car.y+8, 30, 25);
            }

            drawSnake(snake.x, snake.y, SNAKE_W, SNAKE_H);

            if (gameOver && !win) {
                ctx.font = "bold 28px monospace";
                ctx.fillStyle = "red";
                ctx.fillText("GAME OVER – RESTARTING...", W/2-180, H/2);
            }
            if (win) {
                ctx.font = "bold 28px monospace";
                ctx.fillStyle = "gold";
                ctx.fillText("Congratulations! Pythoneer!", W/2-210, H/2-40);
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

        function jump() {
            if (gameOver || win) return;
            if (snake.onGround) {
                snake.vy = -12;
                snake.onGround = false;
            }
        }

        function handleKey(e) {
            if (e.code === 'Space' || e.code === 'ArrowUp') {
                e.preventDefault();
                jump();
            }
        }

        canvas.addEventListener('click', () => {
            canvas.focus();
            statusSpan.innerText = "🎮 Controls active! Press SPACE/UP to jump.";
        });
        canvas.addEventListener('keydown', handleKey);
        window.addEventListener('keydown', handleKey);

        fullReset();
        gameLoop();
    })();
</script>
"""

st.components.v1.html(game_html, height=560, scrolling=False)
