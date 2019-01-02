eel.expose(PythonPrint);
function PythonPrint(message) {
    console.log("Python: "+message);
}

Vue.use(VueMaterial.default);

var app = new Vue({
    el: '#app',
    data: {
        message: 'Hello Vue!',
        botPool: [
            {'name': 'Psyonix Bot', 'image': 'imgs/psyonix.png'},
            {'name': 'Human', 'image': 'imgs/human.png'}
        ],
        blueTeam: [],
        orangeTeam: [],
    },
    methods: {
        startMatch: function (event) {
            eel.startMatch({'blue': this.blueTeam, 'orange': this.orangeTeam})
        }
    }
});

eel.scanForBots('.')(botsReceived);

function botsReceived(bots) {
    app.botPool = app.botPool.concat(bots);
    console.log(app.botPool);
}
