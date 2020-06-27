import AppearanceEditor from './appearance-editor-vue.js'
import MutatorField from './mutator-field-vue.js'
import BotCard from './bot-card-vue.js'

const STARTING_BOT_POOL = [
	{'name': 'Human', 'type': 'human', 'image': 'imgs/human.png'},
	{'name': 'Psyonix Allstar', 'type': 'psyonix', 'skill': 1, 'image': 'imgs/psyonix.png'},
	{'name': 'Psyonix Pro', 'type': 'psyonix', 'skill': 0.5, 'image': 'imgs/psyonix.png'},
	{'name': 'Psyonix Rookie', 'type': 'psyonix', 'skill': 0, 'image': 'imgs/psyonix.png'}
];

export default {
	name: 'match-setup',
	template: `
	<div>
	<b-navbar class="navbar">
		<b-navbar-brand>
			<img class="logo" src="imgs/rlbot_logo.png">
			<span class="rlbot-brand" style="flex: 1">RLBot</span>
		</b-navbar-brand>


		<b-navbar-nav class="ml-auto">
			<b-spinner v-if="showProgressSpinner" variant="success" label="Spinning" class="mr-2"></b-spinner>
			<span id="sandbox-button-wrapper">
				<b-button
					@click="$router.replace('/sandbox')" variant="dark"
					:disabled="!matchSettings.enable_state_setting">
					State Setting Sandbox
				</b-button>
			</span>
			<b-tooltip target="sandbox-button-wrapper" v-if="!matchSettings.enable_state_setting">
				<b-icon class="warning-icon" icon="exclamation-triangle-fill"></b-icon>
				State setting is turned off, sandbox won't work!
			</b-tooltip>

			<span id="story-button-wrapper">
				<b-button 
					@click="$router.replace('/story')" variant="dark" class="ml-2"
					:disabled="!botpackPreExisting">
					Story Mode
				</b-button>
			</span>
			<b-tooltip target="story-button-wrapper" v-if="!botpackPreExisting">
				<b-icon class="warning-icon" icon="exclamation-triangle-fill"></b-icon>
				Download the BotPack first!
			</b-tooltip>

			<b-dropdown right class="ml-4" variant="dark">
				<template v-slot:button-content>
					Menu
				</template>

				<b-dropdown-item v-b-modal.package-installer>
					Install missing python package
				</b-dropdown-item>
				<b-dropdown-item @click="resetMatchSettingsToDefault()">
					Reset match settings
				</b-dropdown-item>
				<b-dropdown-item @click="pickAndEditAppearanceFile()">
					Edit appearance config file
				</b-dropdown-item>
			</b-dropdown>
		</b-navbar-nav>
	</b-navbar>
	<b-container fluid class="rlbot-main-config">

	

	<b-modal title="Install Package" id="package-installer" centered>

		<b-form-group label="Package Name" label-for="package-name">
			<b-form-input id="package-name" v-model="packageString"></b-form-input>
		</b-form-group>

		<template v-slot:modal-footer>
			<b-button @click="installPackage()" class="md-raised md-primary">Install Package</b-button>
		</template>
	</b-modal>


		<b-card class="bot-pool">
			<div class="center-flex mb-3">
				<span class="rlbot-card-header">Player Types</span>
				<b-dropdown text="Add" class="ml-2 mr-2">
					<b-dropdown-item  @click="downloadBotPack()">
						<b-icon icon="cloud-download"></b-icon>
						<span>Download Bot Pack</span>
					</b-dropdown-item>
					<b-dropdown-item v-b-modal.new-bot-modal>
						<b-icon icon="pencil-square"></b-icon>
						<span>Start Your Own Bot!</span>
					</b-dropdown-item>
					<b-dropdown-item  @click="pickBotFolder()">
						<b-icon icon="folder-plus"></b-icon>
						<span>Load Folder</span>
					</b-dropdown-item>
					<b-dropdown-item @click="pickBotConfig()">
						<b-icon icon="file-earmark-plus"></b-icon>
						<span>Load Cfg File</span>
					</b-dropdown-item>
				</b-dropdown>
				<b-button @click="prepareFolderSettingsDialog" v-b-modal.folder-settings-modal>
					Manage bot folders
				</b-button>
				<div class="ml-4">
					<b-form inline>
						<label for="filter-text-input" class="mr-2"><b-icon icon="search"></b-icon></label>
						<b-form-input id="filter-text-input" v-model="botNameFilter" placeholder="Filter..."></b-form-input>
					</b-form>
				</div>
			</div>

			<draggable v-model="botPool" :options="{group: {name:'bots', pull:'clone', put:false}, sort: false}">
				<bot-card v-for="bot in botPool" :bot="bot" @active-bot="activeBot = bot;"
						  :class="{'filtered': !passesFilter(bot.name)}" class="draggable"
						  @click="addToTeam(bot, teamSelection)"/>
			</draggable>

			<div class="mt-2 d-flex flex-wrap">
				<bot-card v-for="script in scriptPool" :bot="script"
						  class="script-card" :class="{'filtered': !passesFilter(script.name)}"
						  @active-bot="activeBot = script;">
					<b-form inline>
						<b-form-checkbox v-model="script.enabled">
							<img v-if="script.logo" v-bind:src="script.logo">
							{{script.name}}
						</b-form-checkbox>
					</b-form>
				</bot-card>
			</div>

		</b-card>

		<b-row>
			<b-col>
				<b-card class="blu team-card md-elevation-8">
					<div class="team-label">
						<b-form-radio v-model="teamSelection" name="team-radios" value="blue">Add to Blue Team</b-form-radio>
					</div>
					<draggable v-model="blueTeam" class="team-entries" :options="{group:'bots'}">
						<b-card class="bot-card draggable center-flex md-elevation-3" v-for="(bot, index) in blueTeam">
							<img v-if="!bot.logo" class="darkened" v-bind:src="bot.image">
							<img v-if="bot.logo" v-bind:src="bot.logo">
							<span class="bot-name">{{ bot.name }}</span>
							<b-button size="sm" variant="outline-danger" class="icon-button" @click="blueTeam.splice(index, 1)">
								<b-icon icon="x"></b-icon>
							</b-button>
						</b-card>
					</draggable>
				</b-card>
			</b-col>

			<b-col>
				<b-card class="org team-card md-elevation-8">
					<div class="team-label">
						<b-form-radio v-model="teamSelection" name="team-radios" value="orange">Add to Orange Team</b-form-radio>
					</div>
					<draggable v-model="orangeTeam" class="team-entries" :options="{group:'bots'}">
						<b-card class="bot-card draggable center-flex md-elevation-3" v-for="(bot, index) in orangeTeam">
							<img v-if="!bot.logo" class="darkened" v-bind:src="bot.image">
							<img v-if="bot.logo" v-bind:src="bot.logo">
							<span class="bot-name">{{ bot.name }}</span>
							<b-button size="sm" variant="outline-danger" class="icon-button" @click="orangeTeam.splice(index, 1)">
								<b-icon icon="x"></b-icon>
							</b-button>
						</b-card>
					</draggable>
				</b-card>
			</b-col>
		</b-row>

		<b-card v-if="matchOptions" class="settings-card">
			<span class="rlbot-card-header">Match Settings</span>
			<div style="display:flex; align-items: flex-end">

				<div>
					<label for="map_selection">Map</label>
					<b-form-select v-model="matchSettings.map" id="map_selection" @change="updateBGImage(matchSettings.map)">
						<b-form-select-option v-for="map in matchOptions.map_types" :key="map" v-bind:value="map">{{map}}</b-form-select-option>
					</b-form-select>
				</div>
				<div class="ml-2">
					<label for="mode_selection">Mode</label>
					<b-form-select v-model="matchSettings.game_mode" id="mode_selection">
						<b-form-select-option v-for="mode in matchOptions.game_modes" :key="mode" v-bind:value="mode">{{mode}}</b-form-select-option>
					</b-form-select>
				</div>

				<b-button class="ml-4" v-b-modal.mutators-modal>Mutators</b-button>
				<b-button class="ml-2" v-b-modal.extra-modal>Extra</b-button>

				<span style="flex-grow: 1"></span>

				<b-button @click="startMatch({'blue': blueTeam, 'orange': orangeTeam})" variant="success" size="lg">Start Match</b-button>
				<b-button @click="killBots()" variant="secondary" size="lg" class="ml-2">Stop</b-button>
			</div>

			<div>
				<b-form-checkbox v-model="matchSettings.randomizeMap" class="mt-1 mb-1">
					Randomize Map
				</b-form-checkbox>
			</div>

			<b-modal title="Extra Options" id="extra-modal" size="md" hide-footer centered>
			<div><b-form-checkbox v-model="matchSettings.enable_rendering">Enable Rendering (bots can draw on screen)</b-form-checkbox></div>
			<div><b-form-checkbox v-model="matchSettings.enable_state_setting">Enable State Setting (bots can teleport)</b-form-checkbox></div>
			<div><b-form-checkbox v-model="matchSettings.auto_save_replay">Auto Save Replay</b-form-checkbox></div>
			<div><b-form-checkbox v-model="matchSettings.skip_replays">Skip Replays</b-form-checkbox></div>
			<div><b-form-checkbox v-model="matchSettings.instant_start">Instant Start</b-form-checkbox></div>
			<div><b-form-checkbox v-model="matchSettings.enable_lockstep">Enable Lockstep</b-form-checkbox></div>
			<mutator-field label="Existing Match Behaviour" :options="matchOptions.match_behaviours" v-model="matchSettings.match_behavior" class="mt-3"></mutator-field>
			</b-modal>

			<b-modal id="mutators-modal" title="Mutators" size="lg" hide-footer centered>

				<b-row>
					<b-col>
						<mutator-field label="Match Length" :options="matchOptions.mutators.match_length_types" v-model="matchSettings.mutators.match_length"></mutator-field>
						<mutator-field label="Max Score" :options="matchOptions.mutators.max_score_types" v-model="matchSettings.mutators.max_score"></mutator-field>
						<mutator-field label="Overtime Type" :options="matchOptions.mutators.overtime_types" v-model="matchSettings.mutators.overtime"></mutator-field>
						<mutator-field label="Game Speed" :options="matchOptions.mutators.game_speed_types" v-model="matchSettings.mutators.game_speed"></mutator-field>
						<mutator-field label="Respawn Time" :options="matchOptions.mutators.respawn_time_types" v-model="matchSettings.mutators.respawn_time"></mutator-field>
					</b-col>
					<b-col>
						<mutator-field label="Max Ball Speed" :options="matchOptions.mutators.ball_max_speed_types" v-model="matchSettings.mutators.ball_max_speed"></mutator-field>
						<mutator-field label="Ball Type" :options="matchOptions.mutators.ball_type_types" v-model="matchSettings.mutators.ball_type"></mutator-field>
						<mutator-field label="Ball Weight" :options="matchOptions.mutators.ball_weight_types" v-model="matchSettings.mutators.ball_weight"></mutator-field>
						<mutator-field label="Ball Size" :options="matchOptions.mutators.ball_size_types" v-model="matchSettings.mutators.ball_size"></mutator-field>
						<mutator-field label="Ball Bounciness" :options="matchOptions.mutators.ball_bounciness_types" v-model="matchSettings.mutators.ball_bounciness"></mutator-field>
					</b-col>
					<b-col>
						<mutator-field label="Boost Amount" :options="matchOptions.mutators.boost_amount_types" v-model="matchSettings.mutators.boost_amount"></mutator-field>
						<mutator-field label="Rumble Type" :options="matchOptions.mutators.rumble_types" v-model="matchSettings.mutators.rumble"></mutator-field>
						<mutator-field label="Boost Strength" :options="matchOptions.mutators.boost_strength_types" v-model="matchSettings.mutators.boost_strength"></mutator-field>
						<mutator-field label="Gravity" :options="matchOptions.mutators.gravity_types" v-model="matchSettings.mutators.gravity"></mutator-field>
						<mutator-field label="Demolition" :options="matchOptions.mutators.demolish_types" v-model="matchSettings.mutators.demolish"></mutator-field>
					</b-col>
				</b-row>


				<b-button @click="resetMutatorsToDefault()">Reset Defaults</b-button>

			</b-modal>
		</b-card>

		<b-toast id="snackbar-toast" v-model="showSnackbar" toaster="b-toaster-bottom-center" body-class="d-none">
			<template v-slot:toast-title>
				{{snackbarContent}}
		    </template>
		</b-toast>

		<b-toast id="bot-pack-available-toast" v-model="showBotpackUpdateSnackbar" title="Bot Pack Update Available!" toaster="b-toaster-bottom-center">
			<b-button class="md-accent" @click="downloadBotPack()" style="margin-left: auto;">Download</b-button>
		</b-toast>

		<b-modal id="bot-info-modal" size="xl" :title="activeBot.name" v-if="activeBot && activeBot.info" hide-footer centered>

			<img v-if="activeBot.logo" class="bot-logo" v-bind:src="activeBot.logo">
			<p><span class="bot-info-key">Developers:</span> {{activeBot.info.developer}}</p>
			<p><span class="bot-info-key">Description:</span> {{activeBot.info.description}}</p>
			<p><span class="bot-info-key">Fun Fact:</span> {{activeBot.info.fun_fact}}</p>
			<p><span class="bot-info-key">GitHub:</span>
				<a :href="activeBot.info.github" target="_blank">{{activeBot.info.github}}</a></p>
			<p><span class="bot-info-key">Language:</span> {{activeBot.info.language}}</p>
			<p class="bot-file-path">{{activeBot.path}}</p>

			<md-dialog-actions>
				<b-button v-if="activeBot.type !== 'script'" @click="showAppearanceEditor(activeBot.looks_path)" v-b-modal.appearance-editor-dialog>
					<b-icon icon="card-image"></b-icon> Edit Appearance
				</b-button>
				<b-button v-if="activeBot.path" @click="showBotInExplorer(activeBot.path)">
					<b-icon icon="folder"></b-icon> Show Files
				</b-button>
			</md-dialog-actions>
		</b-modal>

		<b-modal id="language-warning-modal" v-if="activeBot && activeBot.warn" title="Compatibility Warning" hide-footer centered>
			<div v-if="activeBot.warn === 'java'">
				<p><b>{{activeBot.name}}</b> requires Java and it looks like you don't have it installed!</p>
				To play with it, you'll need to:
				<ol>
					<li>Download Java from <a href="https://java.com" target="_blank">java.com</a></li>
					<li>Install it</li>
					<li>Reboot your computer</li>
				</ol>
			</div>
			<div v-if="activeBot.warn === 'chrome'">
				<p>
					This bot requires Google Chrome for its auto-run feature, and it looks like
					you don't have it installed! You can
					<a href="https://www.google.com/chrome/" target="_blank">download it here</a>.
				</p>
			</div>
			<div v-if="activeBot.warn === 'pythonpkg'">
				<p>
					This bot needs some python package versions you haven't installed yet:
					<code><span v-for="missing in activeBot.missing_python_packages">{{missing}} </span></code>
				</p>
				<b-button @click="installRequirements(activeBot.path)"
						   class="md-primary md-raised">Install Now</b-button>
				<p v-if="!languageSupport.fullpython">
					If the installation fails, try downloading our <a href="https://github.com/RLBot/RLBotGUI/releases/download/v1.0/RLBotGUI.exe">new launcher script</a>
					which makes RLBotGUI better with package management.
				</p>
			</div>
		</b-modal>

		<b-modal id="new-bot-modal" title="Create New Bot" hide-footer centered>
			<b-form inline>
				<label class="mr-3">Bot Name</label>
				<b-form-input v-model="newBotName"></b-form-input>
			</b-form>
			<div>
				<b-form-group>
					<b-form-radio v-model="newBotLanguageChoice" name="lang-radios" value="python">Python</b-form-radio>
					<b-form-radio v-model="newBotLanguageChoice" name="lang-radios" value="python_hive">Python Hivemind</b-form-radio>
					<b-form-radio v-model="newBotLanguageChoice" name="lang-radios" value="scratch">Scratch</b-form-radio>
				</b-form-group>
			</div>

			<b-button variant="primary" @click="beginNewBot(newBotLanguageChoice, newBotName)">Begin</b-button>
		</b-modal>

		<b-modal id="folder-settings-modal" title="Folder Settings" size="xl" hide-footer centered>
			<b-form inline v-for="(settings, path) in folderSettings.folders">
				<b-form-checkbox v-model="settings.visible" style="overflow:hidden;">
					{{ path }}
				</b-form-checkbox>

				<b-button size="sm" variant="outline-danger" class="icon-button" @click="Vue.delete(folderSettings.folders, path)">
					<b-icon icon="x"></b-icon>
				</b-button>
			</b-form>

			<b-form inline v-for="(settings, path) in folderSettings.files">
				<b-form-checkbox v-model="settings.visible" style="overflow: hidden;">
					{{ path }}
				</b-form-checkbox>

				<b-button size="sm" variant="outline-danger" class="icon-button" @click="Vue.delete(folderSettings.files, path)">
					<b-icon icon="x"></b-icon>
				</b-button>
			</b-form>

			<b-button variant="primary" class="mt-3" @click="applyFolderSettings()">Apply</b-button>

		</b-modal>

		<b-modal id="bot-pack-download-modal" title="Downloading Bot Pack" hide-footer centered no-close-on-backdrop no-close-on-esc hide-header-close>
			<div class="text-center">
				<b-icon icon="cloud-download" font-scale="3"></b-icon>
			</div>
			<b-progress variant="success" :value="downloadProgressPercent" animated class="mt-2 mb-2"></b-progress>
			<p>{{ downloadStatus }}</p>
		</b-modal>

		<appearance-editor
				v-bind:active-bot="activeBot"
				v-bind:path="appearancePath"
				v-bind:map="matchSettings.map"
				id="appearance-editor-dialog" />

	</div>

	</b-container>
	</div>
	`,
	components: {
		'appearance-editor': AppearanceEditor,
		'mutator-field': MutatorField,
		'bot-card': BotCard,
	},
	data () {
		return {
			botPool: STARTING_BOT_POOL,
			scriptPool: [],
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
				},
				randomizeMap: false,
				enable_rendering: false,
				enable_state_setting: false,
				auto_save_replay: false,
				scripts: [],
			},
			randomMapPool: [],
			packageString: null,
			showSnackbar: false,
			snackbarContent: null,
			showProgressSpinner: false,
			languageSupport: null,
			activeBot: null,
			newBotName: '',
			newBotLanguageChoice: 'python',
			folderSettings: {
				files: {},
				folders: {}
			},
			botpackPreExisting: false,
			downloadProgressPercent: 0,
			downloadStatus: '',
			showBotpackUpdateSnackbar: false,
			botNameFilter: '',
			appearancePath: ''
		}
	},

	methods: {
		startMatch: async function (event) {
			if (this.matchSettings.randomizeMap) await this.setRandomMap();

			this.matchSettings.scripts = this.scriptPool.filter((val) => { return val.enabled });
			eel.save_match_settings(this.matchSettings);
			eel.save_team_settings(this.blueTeam, this.orangeTeam);

			const blueBots = this.blueTeam.map((bot) => { return  {'name': bot.name, 'team': 0, 'type': bot.type, 'skill': bot.skill, 'path': bot.path} });
			const orangeBots = this.orangeTeam.map((bot) => { return  {'name': bot.name, 'team': 1, 'type': bot.type, 'skill': bot.skill, 'path': bot.path} });

			const renderingMsg = this.matchSettings.enable_rendering ? "🎨 Rendering is ON." : "🚫 Rendering is OFF.";
			const stateSettingMsg = this.matchSettings.enable_state_setting ? "✨ State Setting is ON." : "🚫 State Setting is OFF.";
			this.snackbarContent = renderingMsg + " " + stateSettingMsg + " See EXTRA to change.";
			this.showSnackbar = true;

			// start match asynchronously, so it doesn't block things like updating the background image
			setTimeout(() => {
				eel.start_match(blueBots.concat(orangeBots), this.matchSettings);
			}, 0);
		},
		killBots: function(event) {
			eel.kill_bots();
		},
		pickBotFolder: function (event) {
			eel.pick_bot_folder()(this.botsReceived);
			eel.get_folder_settings()(this.folderSettingsReceived);
		},
		pickBotConfig: function (event) {
			eel.pick_bot_config()(this.botsReceived);
			eel.get_folder_settings()(this.folderSettingsReceived);
		},
		addToTeam: function(bot, team) {
			if (team === 'orange') {
				this.orangeTeam.push(bot);
			} else {
				this.blueTeam.push(bot);
			}
		},
		setRandomMap: async function() {
			if (this.randomMapPool.length == 0) {
				let response = await fetch("json/standard-maps.json");
				this.randomMapPool = await response.json();
			}

			let randomMapIndex = Math.floor(Math.random() * this.randomMapPool.length);
			this.matchSettings.map = this.randomMapPool.splice(randomMapIndex, 1)[0];
			this.updateBGImage(this.matchSettings.map);
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
			this.matchSettings.randomizeMap = false;
			this.matchSettings.enable_rendering = false;
			this.matchSettings.enable_state_setting = true;
			this.matchSettings.auto_save_replay = false;
			this.matchSettings.scripts = [];
			this.resetMutatorsToDefault();

			this.updateBGImage(this.matchSettings.map);
		},
		updateBGImage: function(mapName) {
			let bodyStyle = {backgroundImage: 'url(../imgs/arenas/' + mapName + '.jpg)'};
			this.$emit('background-change', bodyStyle);
		},
		downloadBotPack: function() {
			this.showBotpackUpdateSnackbar = false;
			this.$bvModal.show('bot-pack-download-modal');
			this.downloadStatus = "Starting";
			this.downloadProgressPercent = 0;
			eel.download_bot_pack()(this.botPackDownloaded);
		},
		showAppearanceEditor: function(looksPath) {
			this.appearancePath = looksPath;
			this.appearancePath = looksPath;
			this.$bvModal.show('appearance-editor-dialog');
		},
		pickAndEditAppearanceFile: async function() {
			let path = await eel.pick_location(false)();
			this.activeBot = null;
			if (path) this.showAppearanceEditor(path);
		},
		showBotInExplorer: function (botPath) {
			eel.show_bot_in_explorer(botPath);
		},
		hotReload: function() {
			eel.hot_reload_python_bots();
		},
		beginNewBot: function (language, bot_name) {
			if (!bot_name) {
				this.snackbarContent = "Please choose a proper name!";
				this.showSnackbar = true;
			} else if (language === 'python') {
				this.showProgressSpinner = true;
				eel.begin_python_bot(bot_name)(this.botLoadHandler);
			} else if (language === 'scratch') {
				this.showProgressSpinner = true;
				eel.begin_scratch_bot(bot_name)(this.botLoadHandler);
			} else if (language === 'python_hive') {
				this.showProgressSpinner = true;
				eel.begin_python_hivemind(bot_name)(this.botLoadHandler);
			}
		},
		prepareFolderSettingsDialog: function() {
			eel.get_folder_settings()(this.folderSettingsReceived);
		},
		applyFolderSettings: async function() {
			await eel.save_folder_settings(this.folderSettings)();
			this.botPool = STARTING_BOT_POOL;
			this.scriptPool = [];
			eel.scan_for_bots()(this.botsReceived);
			eel.scan_for_scripts()(this.scriptsReceived);
		},
		passesFilter: function(botName) {
			return botName.toLowerCase().includes(this.botNameFilter.toLowerCase());
		},
		botLoadHandler: function (response) {
			this.$bvModal.hide('new-bot-modal');
			this.showProgressSpinner = false;
			if (response.error) {
				this.snackbarContent = response.error;
				this.showSnackbar = true;
			} else {
				this.botsReceived(response.bots);
			}
		},
		botsReceived: function (bots) {

			const freshBots = bots.filter( (bot) =>
					!this.botPool.find( (element) => element.path === bot.path ));

			freshBots.forEach((bot) => bot.warn = false);

			this.botPool = this.botPool.concat(freshBots).sort((a, b) => a.name.localeCompare(b.name));
			this.applyLanguageWarnings();
			this.showProgressSpinner = false;
		},

		scriptsReceived: function (scripts) {
			const freshScripts = scripts.filter( (script) =>
					!this.scriptPool.find( (element) => element.path === script.path ));
			freshScripts.forEach((script) => {script.enabled = !!this.matchSettings.scripts.find( (element) => element.path === script.path )});

			this.scriptPool = this.scriptPool.concat(freshScripts).sort((a, b) => a.name.localeCompare(b.name));
			this.applyLanguageWarnings();
			this.showProgressSpinner = false;
		},

		applyLanguageWarnings: function () {
			if (this.languageSupport) {
				this.botPool.concat(this.scriptPool).forEach((bot) => {
					if (bot.info && bot.info.language) {
						const language = bot.info.language.toLowerCase();
						if (!this.languageSupport.java && language.match(/java|kotlin|scala/)) {
							bot.warn = 'java';
						}
						if (!this.languageSupport.chrome && language.match(/scratch/)) {
							bot.warn = 'chrome';
						}
					}
					if (bot.missing_python_packages && bot.missing_python_packages.length > 0) {
						bot.warn = 'pythonpkg';
					}
				});
			}
		},
		matchOptionsReceived: function(matchOptions) {
			this.matchOptions = matchOptions;
		},

		matchSettingsReceived: function (matchSettings) {
			if (matchSettings) {
				Object.assign(this.matchSettings, matchSettings);
				this.updateBGImage(this.matchSettings.map);
				this.scriptPool.forEach((script) => {script.enabled = !!this.matchSettings.scripts.find( (element) => element.path === script.path )});
			} else {
				this.resetMatchSettingsToDefault();
			}
		},
		teamSettingsReceived: function (teamSettings) {
			if (teamSettings) {
				this.blueTeam = teamSettings.blue_team;
				this.orangeTeam = teamSettings.orange_team;
			}
		},

		folderSettingsReceived: function (folderSettings) {
			this.folderSettings = folderSettings;
			eel.scan_for_bots()(this.botsReceived);
			eel.scan_for_scripts()(this.scriptsReceived);
		},

		botpackPreExistingReceived: function(commit_id) {
			this.botpackPreExisting = Boolean(commit_id)
		},

		botpackUpdateChecked: function (isBotpackUpToDate) {
			this.showBotpackUpdateSnackbar = !isBotpackUpToDate;
		},

		botPackDownloaded: function (response) {
			this.snackbarContent = 'Downloaded Bot Pack!';
			this.showSnackbar = true;
			this.$bvModal.hide('bot-pack-download-modal');
			eel.get_folder_settings()(this.folderSettingsReceived);
			eel.get_downloaded_botpack_commit_id()(this.botpackPreExistingReceived);
		},

		onInstallationComplete: function (result) {
			let message = result.exitCode === 0 ? 'Successfully installed ' : 'Failed to install ';
			message += result.package;
			this.snackbarContent = message;
			this.showSnackbar = true;
			this.showProgressSpinner = false;
		},
		installPackage: function () {
			this.showProgressSpinner = true;
			eel.install_package(this.packageString)(this.onInstallationComplete);
		},
		installRequirements: function (configPath) {
			this.showProgressSpinner = true;
			eel.install_requirements(configPath)(this.onInstallationComplete);
		}
	},
	created: function () {
		eel.get_folder_settings()(this.folderSettingsReceived);
		eel.get_match_options()(this.matchOptionsReceived);
		eel.get_match_settings()(this.matchSettingsReceived);
		eel.get_team_settings()(this.teamSettingsReceived);

		eel.get_language_support()((support) => {
			this.languageSupport = support;
			this.applyLanguageWarnings();
		});

		eel.get_downloaded_botpack_commit_id()(this.botpackPreExistingReceived)
		eel.is_botpack_up_to_date()(this.botpackUpdateChecked);

		const self = this;
		eel.expose(updateDownloadProgress);
		function updateDownloadProgress(progress, status) {
			self.downloadStatus = status;
			self.downloadProgressPercent = progress;
		}
	},
};
