eel.expose(PythonPrint);
function PythonPrint(message) {
    console.log("Python: "+message);
}

Vue.use(VueMaterial.default);

const STARTING_BOT_POOL = [
    {'name': 'Human', 'type': 'human', 'image': 'imgs/human.png'},
    {'name': 'Psyonix Allstar', 'type': 'psyonix', 'skill': 1, 'image': 'imgs/psyonix.png'},
    {'name': 'Psyonix Pro', 'type': 'psyonix', 'skill': 0.5, 'image': 'imgs/psyonix.png'},
    {'name': 'Psyonix Rookie', 'type': 'psyonix', 'skill': 0, 'image': 'imgs/psyonix.png'}
];

const app = new Vue({
    el: '#app',
    data: {
        botPool: STARTING_BOT_POOL,
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
        showMutatorDialog: false,
        showPackageInstaller: false,
        packageString: null,
        showSnackbar: false,
        snackbarContent: null,
        bodyStyle: null,
        showProgressSpinner: false,
        languageSupport: null,
        activeBot: null,
        showBotInfo: false,
        showLanguageWarning: false,
        showNewBotDialog: false,
        newBotName: '',
        newBotLanguageChoice: 'python',
        folderSettings: {
            files: [],
            folders: []
        },
        showFolderSettingsDialog: false
    },
    methods: {
        startMatch: function (event) {
            const blueBots = this.blueTeam.map((bot) => { return  {'name': bot.name, 'team': 0, 'type': bot.type, 'skill': bot.skill, 'path': bot.path} });
            const orangeBots = this.orangeTeam.map((bot) => { return  {'name': bot.name, 'team': 1, 'type': bot.type, 'skill': bot.skill, 'path': bot.path} });
            eel.start_match(blueBots.concat(orangeBots), this.matchSettings)
        },
        killBots: function(event) {
            eel.kill_bots()
        },
        pickBotFolder: function (event) {
            eel.pick_bot_folder()(botsReceived);
            eel.get_folder_settings()(folderSettingsReceived);
        },
        pickBotConfig: function (event) {
            eel.pick_bot_config()(botsReceived);
            eel.get_folder_settings()(folderSettingsReceived);
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
        },
        updateBGImage: function(mapName) {
            this.bodyStyle = { backgroundImage: "url(../imgs/arenas/" + mapName + ".jpg)" };
        },
        installPackage: function () {
            this.showProgressSpinner = true;
            eel.install_package(this.packageString)(onInstallationComplete);
        },
        downloadBotPack: function() {
            this.showProgressSpinner = true;
            eel.download_bot_pack()(botPackDownloaded);
        },
        showBotInExplorer: function (botPath) {
            eel.show_bot_in_explorer(botPath);
        },
        hotReload: function() {
            eel.hot_reload_python_bots();
        },
        beginNewBot: function (language, bot_name) {
            if (!bot_name) {
                app.snackbarContent = "Please choose a proper name!";
                app.showSnackbar = true;
            }

            if (language === 'python') {
                app.showProgressSpinner = true;
                eel.begin_python_bot(bot_name)(botLoadHandler);
            }
        },
        applyFolderSettings: function() {
            eel.save_folder_settings(app.folderSettings);
            app.botPool = STARTING_BOT_POOL;
            eel.scan_for_bots()(botsReceived);
        }
    }
});

eel.get_folder_settings()(folderSettingsReceived);
eel.scan_for_bots()(botsReceived);
eel.get_match_options()(matchOptionsReceived);

eel.get_language_support()((support) => {
    app.languageSupport = support;
    applyLanguageWarnings();
});

function botPackDownloaded(response) {
    app.snackbarContent = 'Downloaded Bot Pack!';
    app.showSnackbar = true;
    eel.get_folder_settings()(folderSettingsReceived);
    eel.scan_for_bots()(botsReceived);
}

function botLoadHandler(response) {
    app.showNewBotDialog = false;
    app.showProgressSpinner = false;
    if (response.error) {
        app.snackbarContent = response.error;
        app.showSnackbar = true;
    } else {
        botsReceived(response.bots);
    }
}

function botsReceived(bots) {

    const freshBots = bots.filter( (bot) =>
        !app.botPool.find( (element) => element.path === bot.path ));

    freshBots.forEach((bot) => bot.warn = false);

    app.botPool = app.botPool.concat(freshBots).sort((a, b) => a.name.localeCompare(b.name));
    applyLanguageWarnings();
    app.showProgressSpinner = false;
}

function applyLanguageWarnings() {
    if (app.languageSupport) {
        app.botPool.forEach((bot) => {
            if (bot.info && bot.info.language) {
                const language = bot.info.language.toLowerCase();
                if (!app.languageSupport.java && language.match(/java|kotlin|scala/)) {
                    bot.warn = 'java';
                }
                if (!app.languageSupport.chrome && language.match(/scratch/)) {
                    bot.warn = 'chrome';
                }
            }
        });
    }
}

function matchOptionsReceived(matchOptions) {
    app.matchOptions = matchOptions;

    app.matchSettings.map = app.matchOptions.map_types[0];
    app.matchSettings.game_mode = app.matchOptions.game_modes[0];

    app.updateBGImage(app.matchSettings.map);

    app.resetMutatorsToDefault();
}

function folderSettingsReceived(folderSettings) {
    app.folderSettings = folderSettings;
}

function onInstallationComplete(result) {
    let message = result.exitCode === 0 ? 'Successfully installed ' : 'Failed to install ';
    message += result.package;
    app.snackbarContent = message;
    app.showSnackbar = true;
    app.showProgressSpinner = false;
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