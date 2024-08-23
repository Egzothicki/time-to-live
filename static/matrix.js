// matrix.js content
const canvas = document.getElementById('matrix');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const letters = 'アカサタナハマヤラワガザダバパイキシチニヒミリヰグズヅブプウクスツヌフムユルヱゲゼデベペエケセテネヘメレヲゴゾドボポオコソトノホモヨロン1234567890';
const fontSize = 16;
const columns = Math.floor(canvas.width / 11);

const drops = Array(Math.floor(columns)).fill(0);

function draw() {
    ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    for (let i = 0; i < drops.length; i++) {
        const text = letters[Math.floor(Math.random() * letters.length)];
        const x = i * 11;
        const y = drops[i] * fontSize;

        if (drops[i] === 0) {
            ctx.fillStyle = '#FFFFFF';
            ctx.shadowColor = '#00FF00';
            ctx.shadowBlur = 20;
        } else {
            const brightness = 255 - (drops[i] * 4);
            ctx.fillStyle = `rgb(0, ${brightness}, 0)`;
            ctx.shadowBlur = 0;
        }

        ctx.font = fontSize + 'px monospace';
        ctx.fillText(text, x, y);

        if (y > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }

        drops[i]++;
    }
}

setInterval(draw, 33);