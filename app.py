import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="NEON ARCADE", page_icon="🟣", layout="wide")

# ---------- NEON CSS ----------
st.markdown(
    """
    <style>
    :root{
      --bg1:#070014;
      --bg2:#0b0022;
      --neon1:#00f5ff;
      --neon2:#ff2bd6;
      --neon3:#b4ff00;
      --card: rgba(255,255,255,0.06);
      --stroke: rgba(255,255,255,0.12);
      --text: rgba(255,255,255,0.92);
      --muted: rgba(255,255,255,0.68);
    }

    .stApp{
      background:
        radial-gradient(1200px 700px at 15% 15%, rgba(255,43,214,0.20), transparent 60%),
        radial-gradient(900px 600px at 80% 30%, rgba(0,245,255,0.18), transparent 55%),
        radial-gradient(900px 600px at 50% 90%, rgba(180,255,0,0.12), transparent 60%),
        linear-gradient(180deg, var(--bg1), var(--bg2));
      color: var(--text);
    }

    h1, h2, h3, h4 { color: var(--text) !important; }
    p, li { color: var(--muted) !important; }

    .neon-title{
      font-weight: 900;
      letter-spacing: 1.5px;
      font-size: 3.0rem;
      margin: 0.3rem 0 0.1rem 0;
      text-shadow:
        0 0 10px rgba(0,245,255,0.6),
        0 0 25px rgba(255,43,214,0.45),
        0 0 45px rgba(0,245,255,0.35);
    }
    .neon-sub{
      margin-top: 0.2rem;
      font-size: 1.05rem;
      color: var(--muted);
    }

    .neon-card{
      background: var(--card);
      border: 1px solid var(--stroke);
      border-radius: 18px;
      padding: 18px 18px;
      box-shadow:
        0 0 0 1px rgba(0,245,255,0.12) inset,
        0 0 30px rgba(255,43,214,0.12),
        0 0 50px rgba(0,245,255,0.10);
      backdrop-filter: blur(10px);
    }

    .pill{
      display: inline-block;
      padding: 6px 12px;
      border-radius: 999px;
      font-weight: 700;
      font-size: 0.85rem;
      border: 1px solid rgba(255,255,255,0.14);
      background: rgba(255,255,255,0.06);
      box-shadow: 0 0 18px rgba(0,245,255,0.18);
      margin-right: 8px;
    }

    /* Streamlit widget tweaks */
    div[data-baseweb="slider"] > div { color: var(--text) !important; }
    button[kind="primary"]{
      border-radius: 14px !important;
      border: 1px solid rgba(255,255,255,0.18) !important;
      background: linear-gradient(90deg, rgba(0,245,255,0.25), rgba(255,43,214,0.25)) !important;
      box-shadow: 0 0 18px rgba(0,245,255,0.25), 0 0 22px rgba(255,43,214,0.18) !important;
    }
    button[kind="secondary"]{
      border-radius: 14px !important;
      border: 1px solid rgba(255,255,255,0.18) !important;
      background: rgba(255,255,255,0.06) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- HEADER ----------
st.markdown(
    """
    <div style="padding: 8px 4px 2px 4px;">
      <div class="pill">⚡ NEON</div>
      <div class="pill">🎮 ARCADE</div>
      <div class="pill">🧪 STREAMLIT</div>
      <div class="neon-title">NEON ARCADE LAB</div>
      <div class="neon-sub">Een flashy mini-website + een bouncing ball game (paddle). Gebruik <b>←</b> en <b>→</b>.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

# ---------- LAYOUT ----------
left, right = st.columns([0.42, 0.58], gap="large")

with left:
    st.markdown('<div class="neon-card">', unsafe_allow_html=True)
    st.subheader("🧮 Kwadraat-calculator (jouw idee, neon versie)")
    x = st.slider("Kies een getal", 0, 100, 12)
    st.markdown(
        f"""
        <div style="font-size:1.2rem; margin-top: 8px;">
          Het kwadraat van <b>{x}</b> is
          <span style="
            font-weight:900;
            color: #ffffff;
            text-shadow: 0 0 10px rgba(0,245,255,0.65), 0 0 20px rgba(255,43,214,0.45);
          ">{x**2}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    st.subheader("🎛️ Game instellingen")
    c1, c2 = st.columns(2)
    with c1:
        ball_speed = st.slider("Bal-snelheid", 2, 10, 5)
        ball_size = st.slider("Bal-grootte", 6, 20, 10)
    with c2:
        paddle_w = st.slider("Paddle breedte", 60, 200, 120)
        difficulty = st.selectbox("Moeilijkheid", ["Chill", "Normal", "Spicy"], index=1)

    st.caption("Tip: als de game niet reageert: klik één keer in het speelveld (focus) en gebruik dan ← →.")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="neon-card">', unsafe_allow_html=True)
    st.subheader("🟣 Bouncing Ball Game (Neon Paddle)")

    # Difficulty mapping
    diff_map = {"Chill": 0.85, "Normal": 1.0, "Spicy": 1.25}
    diff = diff_map[difficulty]

    # ---------- GAME (HTML/JS canvas) ----------
    # Streamlit component: runs fully in browser, smooth animation
    game_html = f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        html, body {{
          margin: 0; padding: 0;
          background: transparent;
          font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial;
          color: white;
        }}
        .wrap {{
          width: 100%;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }}
        .hud {{
          display:flex;
          justify-content: space-between;
          align-items:center;
          padding: 8px 10px;
          border-radius: 14px;
          border: 1px solid rgba(255,255,255,0.12);
          background: rgba(255,255,255,0.05);
          box-shadow: 0 0 18px rgba(0,245,255,0.15);
          user-select: none;
        }}
        .hud b {{
          text-shadow: 0 0 10px rgba(0,245,255,0.55), 0 0 16px rgba(255,43,214,0.35);
        }}
        canvas {{
          width: 100%;
          height: 460px;
          border-radius: 18px;
          border: 1px solid rgba(255,255,255,0.12);
          background:
            radial-gradient(900px 500px at 20% 15%, rgba(255,43,214,0.18), transparent 60%),
            radial-gradient(900px 500px at 80% 25%, rgba(0,245,255,0.14), transparent 55%),
            linear-gradient(180deg, rgba(10,0,30,0.65), rgba(5,0,15,0.65));
          box-shadow:
            0 0 0 1px rgba(0,245,255,0.10) inset,
            0 0 35px rgba(255,43,214,0.14),
            0 0 55px rgba(0,245,255,0.10);
          outline: none;
        }}
        .hint {{
          font-size: 0.92rem;
          opacity: 0.85;
        }}
        .hint code {{
          background: rgba(255,255,255,0.08);
          padding: 2px 6px;
          border-radius: 10px;
          border: 1px solid rgba(255,255,255,0.10);
        }}
      </style>
    </head>
    <body>
      <div class="wrap">
        <div class="hud">
          <div>Score: <b id="score">0</b> · Lives: <b id="lives">3</b></div>
          <div class="hint">Besturing: <code>←</code> <code>→</code> · <code>Space</code> pauze · <code>R</code> reset</div>
        </div>
        <canvas id="c" tabindex="0"></canvas>
      </div>

      <script>
        const canvas = document.getElementById('c');
        const scoreEl = document.getElementById('score');
        const livesEl = document.getElementById('lives');
        const ctx = canvas.getContext('2d');

        // Handle sizing for crisp drawing
        function resize() {{
          const rect = canvas.getBoundingClientRect();
          const dpr = Math.max(1, window.devicePixelRatio || 1);
          canvas.width = Math.floor(rect.width * dpr);
          canvas.height = Math.floor(rect.height * dpr);
          ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        }}
        window.addEventListener('resize', resize);

        // Game params from Streamlit
        const BASE_SPEED = {ball_speed} * {diff};
        const BALL_R = {ball_size};
        const PADDLE_W = {paddle_w};
        const PADDLE_H = 14;

        let paused = false;

        // State
        let score = 0;
        let lives = 3;

        const keys = {{
          left: false,
          right: false
        }};

        function randSign() {{ return Math.random() < 0.5 ? -1 : 1; }}

        const ball = {{
          x: 120,
          y: 120,
          vx: BASE_SPEED * randSign(),
          vy: BASE_SPEED,
          r: BALL_R
        }};

        const paddle = {{
          x: 120,
          y: 0,
          w: PADDLE_W,
          h: PADDLE_H,
          vx: 0
        }};

        function resetBall() {{
          ball.x = canvas.getBoundingClientRect().width * 0.5;
          ball.y = 120;
          ball.vx = BASE_SPEED * randSign();
          ball.vy = BASE_SPEED;
        }}

        function resetAll() {{
          score = 0;
          lives = 3;
          scoreEl.textContent = score;
          livesEl.textContent = lives;
          resetBall();
        }}

        // Input
        window.addEventListener('keydown', (e) => {{
          if (e.key === 'ArrowLeft') keys.left = true;
          if (e.key === 'ArrowRight') keys.right = true;
          if (e.key === ' ') paused = !paused;
          if (e.key.toLowerCase() === 'r') resetAll();
        }});
        window.addEventListener('keyup', (e) => {{
          if (e.key === 'ArrowLeft') keys.left = false;
          if (e.key === 'ArrowRight') keys.right = false;
        }});

        // Glow helpers
        function glowRect(x,y,w,h, glow1, glow2) {{
          ctx.save();
          ctx.shadowBlur = 24;
          ctx.shadowColor = glow1;
          ctx.fillStyle = glow2;
          ctx.fillRect(x,y,w,h);
          ctx.restore();
        }}

        function glowCircle(x,y,r, glow) {{
          ctx.save();
          ctx.shadowBlur = 28;
          ctx.shadowColor = glow;
          ctx.beginPath();
          ctx.arc(x,y,r,0,Math.PI*2);
          ctx.fillStyle = 'rgba(255,255,255,0.92)';
          ctx.fill();
          ctx.restore();
        }}

        function grid() {{
          const w = canvas.getBoundingClientRect().width;
          const h = canvas.getBoundingClientRect().height;
          ctx.save();
          ctx.globalAlpha = 0.12;
          ctx.lineWidth = 1;
          for (let x=0; x<w; x+=28) {{
            ctx.beginPath();
            ctx.moveTo(x,0);
            ctx.lineTo(x,h);
            ctx.strokeStyle = 'rgba(0,245,255,0.35)';
            ctx.stroke();
          }}
          for (let y=0; y<h; y+=28) {{
            ctx.beginPath();
            ctx.moveTo(0,y);
            ctx.lineTo(w,y);
            ctx.strokeStyle = 'rgba(255,43,214,0.25)';
            ctx.stroke();
          }}
          ctx.restore();
        }}

        function draw() {{
          const w = canvas.getBoundingClientRect().width;
          const h = canvas.getBoundingClientRect().height;

          // Clear
          ctx.clearRect(0,0,w,h);

          // Subtle grid
          grid();

          // Paddle
          glowRect(paddle.x, paddle.y, paddle.w, paddle.h, 'rgba(0,245,255,0.65)', 'rgba(0,245,255,0.22)');
          ctx.save();
          ctx.strokeStyle = 'rgba(255,255,255,0.25)';
          ctx.strokeRect(paddle.x, paddle.y, paddle.w, paddle.h);
          ctx.restore();

          // Ball
          glowCircle(ball.x, ball.y, ball.r, 'rgba(255,43,214,0.65)');

          // Pause overlay
          if (paused) {{
            ctx.save();
            ctx.fillStyle = 'rgba(0,0,0,0.35)';
            ctx.fillRect(0,0,w,h);
            ctx.fillStyle = 'rgba(255,255,255,0.92)';
            ctx.font = '700 28px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial';
            ctx.textAlign = 'center';
            ctx.fillText('PAUSED', w/2, h/2);
            ctx.font = '500 14px ui-sans-serif, system-ui';
            ctx.fillStyle = 'rgba(255,255,255,0.75)';
            ctx.fillText('Press Space to resume', w/2, h/2 + 26);
            ctx.restore();
          }}
        }}

        function update() {{
          const w = canvas.getBoundingClientRect().width;
          const h = canvas.getBoundingClientRect().height;

          // Paddle movement
          const paddleSpeed = 9 * {diff};
          if (keys.left) paddle.x -= paddleSpeed;
          if (keys.right) paddle.x += paddleSpeed;

          // Clamp paddle
          paddle.x = Math.max(0, Math.min(w - paddle.w, paddle.x));
          paddle.y = h - paddle.h - 16;

          if (!paused) {{
            // Move ball
            ball.x += ball.vx;
            ball.y += ball.vy;

            // Wall collisions
            if (ball.x - ball.r <= 0) {{ ball.x = ball.r; ball.vx *= -1; }}
            if (ball.x + ball.r >= w) {{ ball.x = w - ball.r; ball.vx *= -1; }}
            if (ball.y - ball.r <= 0) {{ ball.y = ball.r; ball.vy *= -1; }}

            // Paddle collision
            const withinX = ball.x >= paddle.x && ball.x <= paddle.x + paddle.w;
            const hitY = ball.y + ball.r >= paddle.y && ball.y + ball.r <= paddle.y + paddle.h + 6;
            if (withinX && hitY && ball.vy > 0) {{
              // Bounce up
              ball.y = paddle.y - ball.r - 0.5;
              ball.vy *= -1;

              // Angle based on hit position
              const hitPos = (ball.x - (paddle.x + paddle.w/2)) / (paddle.w/2); // -1..1
              ball.vx = BASE_SPEED * 1.35 * hitPos;
              // Speed up a bit over time
              ball.vy = -Math.max(BASE_SPEED, Math.abs(ball.vy) * 1.03);

              score += 1;
              scoreEl.textContent = score;
            }}

            // Missed (bottom)
            if (ball.y - ball.r > h) {{
              lives -= 1;
              livesEl.textContent = lives;
              if (lives <= 0) {{
                paused = true;
                // Show game over overlay via draw()
                setTimeout(() => {{
                  alert('Game Over! Score: ' + score + '\\nPress R to reset.');
                }}, 10);
              }}
              resetBall();
            }}
          }}

          draw();
          requestAnimationFrame(update);
        }}

        // Start
        setTimeout(() => {{
          resize();
          // Initial paddle placement
          paddle.x = (canvas.getBoundingClientRect().width - paddle.w) / 2;
          resetBall();
          canvas.focus();
          update();
        }}, 60);

        // Click to focus for keys
        canvas.addEventListener('click', () => canvas.focus());
      </script>
    </body>
    </html>
    """

    components.html(game_html, height=560, scrolling=False)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.markdown(
    """
    <div style="opacity:0.75; font-size:0.95rem; padding: 4px 2px;">
      ✨ Volgende level ideeën: <b>levels</b>, <b>power-ups</b>, <b>sound effects</b>, of een <b>highscore</b> die opslaat.
    </div>
    """,
    unsafe_allow_html=True,
)
