eel.expose(PythonPrint);
function PythonPrint(message) {
    console.log("Python: "+message);
}

Vue.use(VueMaterial.default);

const STARTING_BOT_POOL = [
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
            skip_replays: false,
            instant_start: false,
            enable_lockstep: false,
            match_behavior: null,
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
        showFolderSettingsDialog: false,
        showExtraOptions: false,
        showDownloadProgressDialog: false,
        downloadProgressPercent: 0,
        downloadStatus: '',
        showBotpackUpdateSnackbar: false,
        botNameFilter: '',
        appearanceEditor: {
            show: false,
            path: '',
            config: {
                blue: {},
                orange: {},
            },
            itemsLoaded: false,
            items: [],
            itemTypes: [
                {name: 'Body', itemKey: 'car_id', paintKey: 'car_paint_id'},
                {name: 'Decal', itemKey: 'decal_id', paintKey: 'decal_paint_id'},
                {name: 'Wheels', itemKey: 'wheels_id', paintKey: 'wheels_paint_id'},
                {name: 'Rocket Boost', itemKey: 'boost_id', paintKey: 'boost_paint_id'},
                {name: 'Antenna', itemKey: 'antenna_id', paintKey: 'antenna_paint_id'},
                {name: 'Topper', itemKey: 'hat_id', paintKey: 'hat_paint_id'},
                {name: 'Paint Finish', itemKey: 'paint_finish_id', paintKey: null},
                {name: 'Accent Paint Finish', itemKey: 'custom_finish_id', paintKey: null},
                {name: 'Engine Audio', itemKey: 'engine_audio_id', paintKey: null},
                {name: 'Trail', itemKey: 'trails_id', paintKey: 'trails_paint_id'},
                {name: 'Goal Explosion', itemKey: 'goal_explosion_id', paintKey: 'goal_explosion_paint_id'},
            ],
            teams: ['blue', 'orange'],
            colorTypes: [
                {primary: true, name: 'Primary Color', key: 'team_color_id', rows: 7, columns: 10},
                {primary: false, name: 'Accent Color', key: 'custom_color_id', rows: 7, columns: 15}
            ]
        }
    },
    methods: {
        startMatch: function (event) {
            eel.save_match_settings(this.matchSettings);
            eel.save_team_settings(this.blueTeam, this.orangeTeam);

            const blueBots = this.blueTeam.map((bot) => { return  {'name': bot.name, 'team': 0, 'type': bot.type, 'skill': bot.skill, 'path': bot.path} });
            const orangeBots = this.orangeTeam.map((bot) => { return  {'name': bot.name, 'team': 1, 'type': bot.type, 'skill': bot.skill, 'path': bot.path} });
            eel.start_match(blueBots.concat(orangeBots), this.matchSettings);
        },
        killBots: function(event) {
            eel.kill_bots();
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
        resetMatchSettingsToDefault: function() {
            this.matchSettings.map = this.matchOptions.map_types[0];
            this.matchSettings.game_mode = this.matchOptions.game_modes[0];
            this.matchSettings.match_behavior = this.matchOptions.match_behaviours[0];
            this.matchSettings.skip_replays = false;
            this.matchSettings.instant_start = false;
            this.matchSettings.enable_lockstep = false;
            this.resetMutatorsToDefault();

            this.updateBGImage(this.matchSettings.map);
        },
        updateBGImage: function(mapName) {
            this.bodyStyle = { backgroundImage: "url(../imgs/arenas/" + mapName + ".jpg)" };
        },
        installPackage: function () {
            this.showProgressSpinner = true;
            eel.install_package(this.packageString)(onInstallationComplete);
        },
        downloadBotPack: function() {
            this.showBotpackUpdateSnackbar = false;
            this.showDownloadProgressDialog = true;
            this.downloadStatus = "Starting"
            this.downloadProgressPercent = 0;
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

            if (language === 'scratch') {
                app.showProgressSpinner = true;
                eel.begin_scratch_bot(bot_name)(botLoadHandler);
            }
        },
        applyFolderSettings: function() {
            eel.save_folder_settings(app.folderSettings);
            app.botPool = STARTING_BOT_POOL;
            eel.scan_for_bots()(botsReceived);
        },
        passesFilter: function(botName) {
            return botName.toLowerCase().includes(this.botNameFilter.toLowerCase());
        },
        getAndParseItems: async function(url) {
            let response = await fetch(url);
            let data = await response.json();

            // rename duplicate item names
            for (let category of data.Slots) {
                let nameCounts = {};
                for (let item of category.Items) {
                    if (nameCounts[item.Name]) {
                        nameCounts[item.Name]++;
                        item.Name = `${item.Name} (${nameCounts[item.Name]})`;
                    } else {
                        nameCounts[item.Name] = 1;
                    }
                }
            }
            this.appearanceEditor.items = data.Slots;
        },
        showAppearanceEditor: async function(lookPath) {
            this.showBotInfo = false;
            this.showProgressSpinner = true;

            if (!this.appearanceEditor.itemsLoaded) {
                try {
                    // try to fetch latest items from alphaconsole github
                    await this.getAndParseItems('https://raw.githubusercontent.com/AlphaConsole/AlphaConsoleElectron/public/items.json');
                } catch (error) {
                    // otherwise use local version
                    await this.getAndParseItems('json/items.json');
                }
                this.appearanceEditor.itemsLoaded = true;
            }

            this.appearanceEditor.path = lookPath;
            this.appearanceEditor.config = await eel.get_looks(lookPath)();
            this.showProgressSpinner = false;
            this.appearanceEditor.show = true;
        },
        saveAppearance: function() {
            this.appearanceEditor.show = false;
            this.showBotInfo = true;
            eel.save_looks(this.appearanceEditor.config, this.appearanceEditor.path)();
        },
        spawnCarForViewing: function(team) {
            eel.spawn_car_for_viewing(this.appearanceEditor.config, team);
        },
        blueColors: i => { return {
            h: (i % 10) / 20.5 + .33,
            s: .8,
            v: .75 - (Math.floor(i / 10) / 10)
        }},
        orangeColors: i => { return {
            h: 0.2 - ((i % 10) / 35),
            s: 1,
            v: .79 - (Math.floor(i / 10) / 10)
        }},
        accentColors: i => { return {
            h: ((i % 15) / 13) - .12,
            s: i % 15 === 0 ? 0 : 0.9,
            v: i % 15 === 0 ? .75 - (Math.floor(i / 15) / 8) : .85 - (Math.floor(i / 15) / 8)
        }},
        colorStyleFromID: function(id, swatchFunction) {
            let hsl = swatchFunction(parseInt(id));
            let rgb = hslToRgb(hsl.h, hsl.s, hsl.v);
            return 'rgb(' + rgb.toString() + ')';
        },
        getSwatchFunction: function(colorType, team) {
            return colorType.primary ? (team == 'blue' ? this.blueColors : this.orangeColors) : this.accentColors;
        },
        getColorIDFromRowAndColumn(row, column, colorType) {
            return (row - 1) * colorType.columns + (column - 1);
        },
        colorStyle: function(colorType, team) {
            let id = this.appearanceEditor.config[team][colorType.key];
            return this.colorStyleFromID(id, this.getSwatchFunction(colorType, team));
        },
        colorStyleFromRowAndColumn: function (colorType, team, row, column) {
            let id = this.getColorIDFromRowAndColumn(row, column, colorType);
            return this.colorStyleFromID(id, this.getSwatchFunction(colorType, team));
        }
    }
});

eel.get_folder_settings()(folderSettingsReceived);
eel.scan_for_bots()(botsReceived);
eel.get_match_options()(matchOptionsReceived);
eel.get_match_settings()(matchSettingsReceived);
eel.get_team_settings()(teamSettingsReceived);

eel.get_language_support()((support) => {
    app.languageSupport = support;
    applyLanguageWarnings();
});

eel.is_botpack_up_to_date()(botpackUpdateChecked);

function botpackUpdateChecked(isBotpackUpToDate) {
    app.showBotpackUpdateSnackbar = !isBotpackUpToDate;
}

function botPackDownloaded(response) {
    app.snackbarContent = 'Downloaded Bot Pack!';
    app.showSnackbar = true;
    app.showDownloadProgressDialog = false;
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
}

function matchSettingsReceived(matchSettings) {
    if (matchSettings) {
        app.matchSettings = matchSettings;
        app.updateBGImage(app.matchSettings.map);
    } else {
        app.resetMatchSettingsToDefault();
    }
}

function teamSettingsReceived(teamSettings) {
    if (teamSettings) {
        app.blueTeam = teamSettings.blue_team;
        app.orangeTeam = teamSettings.orange_team;
    }
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

eel.expose(updateDownloadProgress);
function updateDownloadProgress(progress, status) {
    app.downloadStatus = status;
    app.downloadProgressPercent = progress;
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
