import streamlit as st

# 1. Page Config
st.set_page_config(page_title="GLOBALINTERNET.PY - Cash Runner", layout="wide")

# 2. Header and Branding
st.title("🏃‍♂️ GLOBALINTERNET.PY: Cash Runner")
st.write("Use **Space** or **Up Arrow** to jump. Catch 5 bags to win!")

# 3. Game Logic (HTML/JS)
# Note: Keeping the HTML logic in a string for st.components.v1.html
game_code = """
<style>
    body { margin: 0; background-color: #0e1117; color: white; display: flex; justify-content: center; }
    canvas { border: 4px solid #4ade80; border-radius: 8px; background: #1e293b; outline: none; }
    #ui { text-align: center; font-family: sans-serif; margin-top: 10px; color: #4ade80; font-size: 1.2rem; }
</style>

<canvas id="g" width="800" height="400" tabindex="0"></canvas>
<div id="ui">💰 Bags: <span id="s">0</span>/5 | <span id="m">Ready? Press Space to Jump!</span></div>

<script>
const c = document.getElementById('g'), x = c.getContext('2d'), sEl = document.getElementById('s'), mEl = document.getElementById('m');
let p = {y:340, vy:0, j:false, f:0}, world = 0, score = 0, active = true;
let bags = [{x:600, y:200}, {x:1100, y:150}, {x:1600, y:250}, {x:2100, y:180}, {x:2600, y:220}];
let cars = [{x:900}, {x:1500}, {x:2200}];

function drawMan(y, f, j) {
    x.strokeStyle = "#fff"; x.lineWidth = 3;
    let swing = j ? 0 : Math.sin(f * 0.2) * 15;
    x.beginPath(); x.arc(50, y+10, 8, 0, 7); x.stroke(); // Head
    x.moveTo(50, y+18); x.lineTo(50, y+40); // Body
    x.moveTo(50, y+25); x.lineTo(50+swing, y+35); x.moveTo(50, y+25); x.lineTo(50-swing, y+35); // Arms
    x.moveTo(50, y+40); x.lineTo(50+swing, y+55); x.moveTo(50, y+40); x.lineTo(50-swing, y+55); // Legs
    x.stroke();
}

function loop() {
    if(!active) return;
    x.clearRect(0,0,800,400);
    x.fillStyle="#334155"; x.fillRect(0,390,800,10); // Ground
    
    p.vy += 0.8; p.y += p.vy;
    if(p.y > 340) { p.y = 340; p.vy = 0; p.j = false; }
    world += 4; p.f++;

    bags.forEach(b => {
        if(!b.c) {
            x.fillStyle="#fbbf24"; x.fillRect(b.x-world, b.y, 25, 30);
            if(Math.abs(50-(b.x-world)) < 30 && Math.abs(p.y-b.y) < 40) { b.c=true; score++; sEl.innerText=score; }
        }
    });

    x.fillStyle="#ef4444";
    cars.forEach(car => {
        x.fillRect(car.x-world, 365, 50, 25);
        if(Math.abs(50-(car.x-world)) < 30 && p.y > 320) { active=false; mEl.innerText="💥 CRASHED! Refresh to try again."; }
    });

    drawMan(p.y, p.f, p.j);
    if(score >= 5) mEl.innerText = "🏆 MISSION COMPLETE!";
    requestAnimationFrame(loop);
}

c.addEventListener('keydown', e => { 
    if((e.code=='Space' || e.code=='ArrowUp') && !p.j) { p.vy=-15; p.j=true; }
});
c.focus(); loop();
</script>
"""

# 4. Render the Component
st.components.v1.html(game_code, height=500)

st.divider()
st.info("Technical Note: This app uses a Zero-Subscription model with full source transparency.")
