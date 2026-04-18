import streamlit as st

st.set_page_config(page_title="Cash Runner Pro", layout="wide")

st.markdown("""
<style>
    body { margin: 0; background-color: #1a1a1a; color: white; }
    canvas { display: block; margin: 20px auto; border: 5px solid #4ade80; border-radius: 12px; background: #0f172a; cursor: crosshair; }
    .status-bar { text-align: center; font-family: 'Courier New', monospace; font-size: 1.4rem; color: #4ade80; margin-top: 10px; }
</style>
""", unsafe_allow_html=True)

game_html = """
<canvas id="gameCanvas" width="1000" height="500" tabindex="0"></canvas>
<div class="status-bar">
    💰 Score: <span id="score">0</span>/5 | <span id="msg">Click to Start!</span>
</div>

<script>
(function() {
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    const scoreEl = document.getElementById('score');
    const msgEl = document.getElementById('msg');

    // --- Game Settings ---
    const W = 1000, H = 500, GROUND_Y = 450;
    let player = { x: 100, y: GROUND_Y - 60, vy: 0, w: 30, h: 60, jumping: false, frame: 0 };
    let bags = [
        { x: 500, y: 250, collected: false },
        { x: 850, y: 200, collected: false },
        { x: 1200, y: 280, collected: false },
        { x: 1550, y: 180, collected: false },
        { x: 1900, y: 230, collected: false }
    ];
    let cars = [];
    let worldX = 0;
    let score = 0;
    let active = true;

    // --- Draw Man Figure ---
    function drawMan(p) {
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 4;
        const headR = 8;
        const centerX = p.x;
        const baseY = p.y;

        // Head
        ctx.beginPath();
        ctx.arc(centerX, baseY + headR, headR, 0, Math.PI*2);
        ctx.stroke();

        // Torso
        ctx.beginPath();
        ctx.moveTo(centerX, baseY + headR*2);
        ctx.lineTo(centerX, baseY + headR*2 + 25);
        ctx.stroke();

        // Animation logic
        let limbSwing = p.jumping ? 0.5 : Math.sin(p.frame * 0.2);

        // Arms
        ctx.beginPath();
        ctx.moveTo(centerX, baseY + headR*2 + 5);
        ctx.lineTo(centerX + (15 * limbSwing), baseY + headR*2 + 20); // Right
        ctx.moveTo(centerX, baseY + headR*2 + 5);
        ctx.lineTo(centerX - (15 * limbSwing), baseY + headR*2 + 20); // Left
        ctx.stroke();

        // Legs
        ctx.beginPath();
        ctx.moveTo(centerX, baseY + headR*2 + 25);
        ctx.lineTo(centerX + (15 * limbSwing), baseY + headR*2 + 45); // Right
        ctx.moveTo(centerX, baseY + headR*2 + 25);
        ctx.lineTo(centerX - (15 * limbSwing), baseY + headR*2 + 45); // Left
        ctx.stroke();
    }

    function drawBag(b) {
        ctx.fillStyle = "#fbbf24";
        ctx.beginPath();
        ctx.roundRect(b.x - worldX, b.y, 30, 35, 5);
        ctx.fill();
        ctx.fillStyle = "#000";
        ctx.font = "bold 18px Arial";
        ctx.fillText("$", b.x - worldX + 10, b.y + 25);
    }

    function update() {
        if (!active) return;

        // Gravity & Jump
        player.vy += 0.8;
        player.y += player.vy;
        if (player.y > GROUND_Y - 60) {
            player.y = GROUND_Y - 60;
            player.vy = 0;
            player.jumping = false;
        }

        // Camera move
        worldX += 5;
        player.frame++;

        // Obstacle Spawn
        if (player.frame % 120 === 0) {
            cars.push({ x: worldX + 1100, y: GROUND_Y - 30 });
        }

        // Collisions
        bags.forEach(b => {
            if (!b.collected && Math.abs(player.x - (b.x - worldX)) < 30 && Math.abs(player.y - b.y) < 60) {
                b.collected = true;
                score++;
                scoreEl.innerText = score;
                if (score === 5) msgEl.innerText = "FINISH LINE OPEN!";
            }
        });

        cars.forEach(c => {
            if (Math.abs(player.x - (c.x - worldX)) < 40 && player.y > GROUND_Y - 80) {
                active = false;
                msgEl.innerText = "💥 CRASHED! Refresh to restart.";
            }
        });

        if (score >= 5 && worldX > 2200) {
            active = false;
            msgEl.innerText = "🏆 WINNER! CASH SECURED! 🏆";
        }
    }

    function render() {
        ctx.clearRect(0, 0, W, H);
        
        // Ground
        ctx.fillStyle = "#334155";
        ctx.fillRect(0, GROUND_Y, W, 50);

        // Entities
        bags.forEach(b => { if(!b.collected) drawBag(b); });
        
        ctx.fillStyle = "#ef4444";
        cars.forEach(c => {
            ctx.fillRect(c.x - worldX, c.y, 60, 30);
            ctx.fillStyle = "#fff";
            ctx.fillRect(c.x - worldX + 10, c.y + 5, 15, 10);
            ctx.fillStyle = "#ef4444";
        });

        drawMan(player);
        update();
        requestAnimationFrame(render);
    }

    canvas.addEventListener('keydown', (e) => {
        if ((e.code === 'Space' || e.code === 'ArrowUp') && !player.jumping) {
            player.vy = -18;
            player.jumping = true;
            msgEl.innerText = "JUMPING!";
        }
    });

    canvas.focus();
    render();
})();
</script>
"""

st.components.v1.html(game_html, height=600)
