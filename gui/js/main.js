eel.expose(PythonPrint);
function PythonPrint(message) {
    console.log("Python: "+message);
}

Vue.use(VueMaterial.default);

const app = new Vue({
    el: '#app',
    data: {
        botPool: [
            {'name': 'Human', 'type': 'human', 'image': 'imgs/human.png'},
            {'name': 'Psyonix Bot', 'type': 'psyonix', 'image': 'imgs/psyonix.png'}
        ],
        blueTeam: [],
        orangeTeam: [],
        teamSelection: "blue",
        matchOptions: null,
        matchSettings: {
            map: null,
            game_mode: null,
            mutators: {
                match_length: null,
                max_score: null,
                overtime: null,
                series_length: null,
                game_speed: null,
                ball_max_speed: null,
                ball_type: null,
                ball_weight: null,
                ball_size: null,
                ball_bounciness: null,
                boost_amount: null,
                rumble: null,
                boost_strength: null,
                gravity: null,
                demolish: null,
                respawn_time: null
            }
        },
        showMutatorDialog: false
    },
    methods: {
        startMatch: function (event) {
            const blueBots = this.blueTeam.map((bot) => { return  {'name': bot.name, 'team': 0, 'type': bot.type, 'path': bot.path} });
            const orangeBots = this.orangeTeam.map((bot) => { return  {'name': bot.name, 'team': 1, 'type': bot.type, 'path': bot.path} });
            eel.start_match(blueBots.concat(orangeBots), this.matchSettings)
        },
        killBots: function(event) {
            eel.kill_bots()
        },
        pickBotFolder: function (event) {
            eel.pick_bot_folder()(botsReceived);
        },
        pickBotConfig: function (event) {
            eel.pick_bot_config()(botsReceived);
        },
        addToTeam: function(bot, team) {
            if (team === 'orange') {
                this.orangeTeam.push(bot);
            } else {
                this.blueTeam.push(bot);
            }
        },
        resetMutatorsToDefault: function() {
            const self = this;
            Object.keys(this.matchOptions.mutators).forEach(function (mutator) {
                const mutatorName = mutator.replace('_types', '');
                self.matchSettings.mutators[mutatorName] = self.matchOptions.mutators[mutator][0];
            });
        }
    }
});

eel.scan_for_bots('.')(botsReceived);
eel.get_match_options()(matchOptionsReceived);

function botsReceived(bots) {

    const freshBots = bots.filter( (bot) =>
        !app.botPool.find( (element) => element.path === bot.path ));

    app.botPool = app.botPool.concat(freshBots).sort((a, b) => a.name.localeCompare(b.name));

    console.log(app.botPool);
}

function matchOptionsReceived(matchOptions) {
    app.matchOptions = matchOptions;

    app.matchSettings.map = app.matchOptions.map_types[0];
    app.matchSettings.game_mode = app.matchOptions.game_modes[0];

    app.resetMutatorsToDefault();
}

Vue.component('mutator-field', {
        props: ['label', 'options', 'value'],
        data: function() {
            return {
                id: Math.floor(Math.random() * 1000000000).toString(),
                model: this.value
            }
        },
        watch: {
            value: function(newVal, oldVal) {
                this.model = newVal;
            }
        },
        template: `
            <md-field>
                <label :for="id">{{label}}</label>
                <md-select v-model="model" :id="id" v-on:md-selected="$emit('input', $event)">
                    <md-option v-for="opt in options" :key="opt" :value="opt">{{opt}}</md-option>
                </md-select>
            </md-field>
        `
    }
);