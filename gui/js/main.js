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
        },
        pickBotFolder: function (event) {
            eel.pick_bot_folder()(botsReceived)
        },
        pickBotConfig: function (event) {
            eel.pick_bot_config()(botsReceived)
        }
    }
});

eel.scanForBots('.')(botsReceived);

function botsReceived(bots) {

    const freshBots = bots.filter( (bot) =>
        !app.botPool.find( (element) => element.path === bot.path ));

    app.botPool = app.botPool.concat(freshBots);

    console.log(app.botPool);
}
