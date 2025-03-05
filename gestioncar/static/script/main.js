const app = document.getElementById('typewriter');
const typewriter  = new Typewriter(app, {
    loop: true,
    delay:75
});

typewriter
    .typeString('The City of Parks')
    .pauseFor(200)
    .start();