<template>

	<div>

	<md-toolbar class="md-primary">
		<div class="md-toolbar-row">
			<img class="logo" src="imgs/rlbot_logo.png">
			<h3 class="md-title" style="flex: 1">RLBot</h3>

			<div class="md-toolbar-section-end">
				<md-progress-spinner v-if="showProgressSpinner" class="md-accent" :md-diameter="30" md-mode="indeterminate"></md-progress-spinner>
				<md-menu md-direction="bottom-start">
					<md-button md-menu-trigger class="md-icon-button">
						<md-icon>more_vert</md-icon>
					</md-button>

					<md-menu-content>
						<md-menu-item @click="showPackageInstaller = true;">
							Install missing python package
						</md-menu-item>
						<md-menu-item @click="resetMatchSettingsToDefault()">
							Reset match settings
						</md-menu-item>
						<md-menu-item @click="pickAndEditAppearanceFile()">
							Edit appearance config file
						</md-menu-item>
						<md-menu-item @click="$router.replace('/sandbox')">
							Sandbox (experimental)
						</md-menu-item>
					</md-menu-content>
				</md-menu>
			</div>
		</div>
	</md-toolbar>

	<md-dialog :md-active.sync="showPackageInstaller">
		<md-dialog-title>Install Package</md-dialog-title>

		<md-dialog-content>

			<md-field>
				<label>Package Name</label>
				<md-input v-model="packageString"></md-input>
			</md-field>
		</md-dialog-content>

		<md-dialog-actions>
			<md-button @click="installPackage()" class="md-raised md-primary">Install Package</md-button>
			<md-button @click="showPackageInstaller = false">Close</md-button>
		</md-dialog-actions>
	</md-dialog>

	<div>

		<md-card class="bot-pool">
			<md-card-header class="center-flex">
				<div class="md-title" style="display:inline-block">Player Types</div>
				<md-menu md-direction="bottom-start" class="bot-pool-adder">
					<md-button class="md-fab md-mini" md-menu-trigger>
						<md-icon>add</md-icon>
						<md-tooltip md-direction="top">Load more player types</md-tooltip>
					</md-button>

					<md-menu-content>
						<md-menu-item  @click="downloadBotPack()">
							<span>Download Bot Pack</span>
							<md-icon>cloud_download</md-icon>
						</md-menu-item>
						<md-menu-item  @click="showNewBotDialog = true">
							<span>Start Your Own Bot!</span>
							<md-icon>create</md-icon>
						</md-menu-item>
						<md-menu-item  @click="pickBotFolder()">
							<span>Load Folder</span>
							<md-icon>folder_open</md-icon>
						</md-menu-item>
						<md-menu-item @click="pickBotConfig()">
							<span>Load Cfg File</span>
							<md-icon>file_copy</md-icon>
						</md-menu-item>
					</md-menu-content>
				</md-menu>
				<md-button class="md-fab md-mini bot-pool-adder" @click="openFolderSettingsDialog">
					<md-icon>settings</md-icon>
					<md-tooltip md-direction="top">Manage bot folders</md-tooltip>
				</md-button>

				<div class="bot-filter">
					<md-field md-inline md-clearable>
						<label><md-icon>search</md-icon>Filter</label>
						<md-input v-model="botNameFilter"></md-input>
					</md-field>
				</div>

			</md-card-header>

			<draggable v-model="botPool" :options="{group: {name:'bots', pull:'clone', put:false}, sort: false}">
				<md-card class="bot-card md-elevation-3" v-for="bot in botPool" :class="{'filtered': !passesFilter(bot.name)}">
					<button class="center-flex secret-button" @click="addToTeam(bot, teamSelection)">
						<img v-if="!bot.logo" class="darkened" v-bind:src="bot.image">
						<img v-if="bot.logo" v-bind:src="bot.logo">
						<span class="bot-name">{{ bot.name }}</span>
						<md-button class="md-icon-button md-dense warning-icon" v-if="bot.warn"
								   @click.stop="activeBot = bot; showLanguageWarning = true;">
							<md-icon>warning</md-icon>
						</md-button>
						<md-button class="md-icon-button md-dense bot-hover-reveal" v-if="bot.info"
								   @click.stop="activeBot = bot; showBotInfo = true;">
							<md-icon>blur_on</md-icon>
						</md-button>
					</button>
				</md-card>
			</draggable>
		</md-card>

		<div id="teamSwitcher" style="text-align: center;">
			<div style="display: inline-block">
				<md-switch v-model="teamSelection" v-bind:class="[teamSelection]" value="orange" style="margin:1px 0"></md-switch>
				<md-tooltip md-direction="top">Toggle which team gets bots when you click them</md-tooltip>
			</div>
		</div>

		<div class="md-layout">
			<div class="md-layout-item">
				<md-card class="blu team-card md-elevation-8">
					<md-card-header class="team-label">
						<div class="md-title">Blue Team</div>
					</md-card-header>
					<draggable v-model="blueTeam" class="team-entries" :options="{group:'bots'}">
						<md-card class="bot-card center-flex md-elevation-3" v-for="(bot, index) in blueTeam">
							<img v-if="!bot.logo" class="darkened" v-bind:src="bot.image">
							<img v-if="bot.logo" v-bind:src="bot.logo">
							<span class="bot-name">{{ bot.name }}</span>
							<md-button class="md-icon-button" @click="blueTeam.splice(index, 1)">
								<md-icon>close</md-icon>
							</md-button>
						</md-card>
					</draggable>
				</md-card>
			</div>

			<div class="md-layout-item">
				<md-card class="org team-card md-elevation-8">
					<md-card-header class="team-label">
						<div class="md-title">Orange Team</div>
					</md-card-header>
					<draggable v-model="orangeTeam" class="team-entries" :options="{group:'bots'}">
						<md-card class="bot-card center-flex md-elevation-3" v-for="(bot, index) in orangeTeam">
							<img v-if="!bot.logo" class="darkened" v-bind:src="bot.image">
							<img v-if="bot.logo" v-bind:src="bot.logo">
							<span class="bot-name">{{ bot.name }}</span>
							<md-button class="md-icon-button" @click="orangeTeam.splice(index, 1)">
								<md-icon>close</md-icon>
							</md-button>
						</md-card>
					</draggable>
				</md-card>
			</div>
		</div>

		<md-card v-if="matchOptions" class="settings-card">
			<md-card-header>
				<div class="md-title">Match Settings</div>
			</md-card-header>

			<md-card-content>

				<div class="center-flex">

					<div class="md-layout md-gutter" style="max-width: 400px;">
						<div class="md-layout-item">
							<md-field>
								<label for="map_selection">Map</label>
								<md-select v-model="matchSettings.map" id="map_selection" @md-closed="updateBGImage(matchSettings.map)">
									<md-option v-for="map in matchOptions.map_types" :key="map" v-bind:value="map">{{map}}</md-option>
								</md-select>
							</md-field>
						</div>
						<div class="md-layout-item">
							<md-field>
								<label for="mode_selection">Mode</label>
								<md-select v-model="matchSettings.game_mode" id="mode_selection">
									<md-option v-for="mode in matchOptions.game_modes" :key="mode" v-bind:value="mode">{{mode}}</md-option>
								</md-select>
							</md-field>
						</div>
					</div>

					<md-button class="md-raised" style="margin-left: 20px" @click="showMutatorDialog = true">Mutators</md-button>

					<md-button class="md-raised" @click="showExtraOptions = true">Extra</md-button>

					<span style="flex-grow: 1"></span>

					<md-button @click="hotReload()" class="md-icon-button">
						<md-icon>loop</md-icon>
						<md-tooltip md-direction="top">Hot-reload python bots</md-tooltip>
					</md-button>
					<md-button @click="startMatch({'blue': blueTeam, 'orange': orangeTeam})" class="md-primary md-raised">Start Match</md-button>
					<md-button @click="killBots()" class="md-raised">Stop</md-button>
				</div>

				<md-dialog :md-active.sync="showExtraOptions">
					<md-dialog-title>Extra Options</md-dialog-title>

					<md-dialog-content>
						<md-switch v-model="matchSettings.skip_replays">Skip Replays</md-switch>
						<md-switch v-model="matchSettings.instant_start">Instant Start</md-switch>
						<md-switch v-model="matchSettings.enable_lockstep">Enable lockstep</md-switch>
						<mutator-field label="Existing Match Behaviour" :options="matchOptions.match_behaviours" v-model="matchSettings.match_behavior"></mutator-field>
					</md-dialog-content>

					<md-dialog-actions>
						<md-button @click="showExtraOptions = false">Close</md-button>
					</md-dialog-actions>
				</md-dialog>

				<md-dialog :md-active.sync="showMutatorDialog">
					<md-dialog-title>Mutators</md-dialog-title>

					<md-dialog-content>

						<div class="md-layout md-gutter">
							<div class="md-layout-item">
								<mutator-field label="Match Length" :options="matchOptions.mutators.match_length_types" v-model="matchSettings.mutators.match_length"></mutator-field>
								<mutator-field label="Max Score" :options="matchOptions.mutators.max_score_types" v-model="matchSettings.mutators.max_score"></mutator-field>
								<mutator-field label="Overtime Type" :options="matchOptions.mutators.overtime_types" v-model="matchSettings.mutators.overtime"></mutator-field>
								<mutator-field label="Game Speed" :options="matchOptions.mutators.game_speed_types" v-model="matchSettings.mutators.game_speed"></mutator-field>
								<mutator-field label="Respawn Time" :options="matchOptions.mutators.respawn_time_types" v-model="matchSettings.mutators.respawn_time"></mutator-field>
							</div>
							<div class="md-layout-item">
								<mutator-field label="Max Ball Speed" :options="matchOptions.mutators.ball_max_speed_types" v-model="matchSettings.mutators.ball_max_speed"></mutator-field>
								<mutator-field label="Ball Type" :options="matchOptions.mutators.ball_type_types" v-model="matchSettings.mutators.ball_type"></mutator-field>
								<mutator-field label="Ball Weight" :options="matchOptions.mutators.ball_weight_types" v-model="matchSettings.mutators.ball_weight"></mutator-field>
								<mutator-field label="Ball Size" :options="matchOptions.mutators.ball_size_types" v-model="matchSettings.mutators.ball_size"></mutator-field>
								<mutator-field label="Ball Bounciness" :options="matchOptions.mutators.ball_bounciness_types" v-model="matchSettings.mutators.ball_bounciness"></mutator-field>
							</div>
							<div class="md-layout-item">
								<mutator-field label="Boost Amount" :options="matchOptions.mutators.boost_amount_types" v-model="matchSettings.mutators.boost_amount"></mutator-field>
								<mutator-field label="Rumble Type" :options="matchOptions.mutators.rumble_types" v-model="matchSettings.mutators.rumble"></mutator-field>
								<mutator-field label="Boost Strength" :options="matchOptions.mutators.boost_strength_types" v-model="matchSettings.mutators.boost_strength"></mutator-field>
								<mutator-field label="Gravity" :options="matchOptions.mutators.gravity_types" v-model="matchSettings.mutators.gravity"></mutator-field>
								<mutator-field label="Demolition" :options="matchOptions.mutators.demolish_types" v-model="matchSettings.mutators.demolish"></mutator-field>
							</div>
						</div>
					</md-dialog-content>

					<md-dialog-actions>
						<md-button @click="resetMutatorsToDefault()">Reset Defaults</md-button>
						<md-button @click="showMutatorDialog = false">Close</md-button>
					</md-dialog-actions>
				</md-dialog>

			</md-card-content>
		</md-card>

		<md-snackbar md-position="center" :md-active.sync="showSnackbar" md-persistent>
			<span>{{snackbarContent}}</span>
		</md-snackbar>

		<md-snackbar md-position="center" :md-active="showBotpackUpdateSnackbar" :md-duration="10000">
			<span>Bot Pack update available!</span>
			<md-button class="md-accent" @click="downloadBotPack()" style="margin-left: auto;">Download</md-button>
			<md-button class="md-icon-button" @click="showBotpackUpdateSnackbar = false;">
				<md-icon style="color: #ffffffb4;">close</md-icon>
			</md-button>
		</md-snackbar>

		<md-dialog v-if="activeBot && activeBot.info" :md-active.sync="showBotInfo">
			<md-dialog-title>
				{{activeBot.name}}
			</md-dialog-title>
			<md-dialog-content>
				<img v-if="activeBot.logo" class="bot-logo" v-bind:src="activeBot.logo">
				<p><span class="bot-info-key">Developers:</span> {{activeBot.info.developer}}</p>
				<p><span class="bot-info-key">Description:</span> {{activeBot.info.description}}</p>
				<p><span class="bot-info-key">Fun Fact:</span> {{activeBot.info.fun_fact}}</p>
				<p><span class="bot-info-key">GitHub:</span>
					<a :href="activeBot.info.github" target="_blank">{{activeBot.info.github}}</a></p>
				<p><span class="bot-info-key">Language:</span> {{activeBot.info.language}}</p>
				<p class="bot-file-path">{{activeBot.path}}</p>
			</md-dialog-content>

			<md-dialog-actions>
				<md-button @click="showAppearanceEditor(activeBot.looks_path)">
					<md-icon>palette</md-icon> Edit Appearance
				</md-button>
				<md-button v-if="activeBot.path" @click="showBotInExplorer(activeBot.path)">
					<md-icon>folder</md-icon> Show Files
				</md-button>
				<md-button @click="showBotInfo = false">Close</md-button>
			</md-dialog-actions>
		</md-dialog>

		<md-dialog v-if="activeBot && activeBot.warn" :md-active.sync="showLanguageWarning">
			<md-dialog-title>Compatibility Warning</md-dialog-title>

			<md-dialog-content>
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
			</md-dialog-content>

			<md-dialog-actions>
				<md-button @click="showLanguageWarning = false">Close</md-button>
			</md-dialog-actions>
		</md-dialog>

		<md-dialog :md-active.sync="showNewBotDialog">
			<md-dialog-title>Create New Bot</md-dialog-title>

			<md-dialog-content>
				<md-field>
					<label>Bot Name</label>
					<md-input v-model="newBotName"></md-input>
				</md-field>
				<div>
					<md-radio v-model="newBotLanguageChoice" value="python">Python</md-radio>
					<md-radio v-model="newBotLanguageChoice" value="scratch">Scratch</md-radio>
				</div>
			</md-dialog-content>

			<md-dialog-actions>
				<md-button class="md-raised md-primary" @click="beginNewBot(newBotLanguageChoice, newBotName)">Begin</md-button>
				<md-button @click="showNewBotDialog = false">Close</md-button>
			</md-dialog-actions>
		</md-dialog>

		<md-dialog :md-active.sync="showFolderSettingsDialog" style="overflow: scroll;">
			<md-dialog-title>Folder Settings</md-dialog-title>

			<md-dialog-content>

				<md-list>
					<md-list-item v-for="(settings, path) in folderSettings.folders">
						<md-switch v-model="settings.visible" style="overflow:hidden;">
							{{ path }}
						</md-switch>

						<md-button class="md-icon-button" @click="delete folderSettings.folders[path]">
							<md-icon>close</md-icon>
						</md-button>
					</md-list-item>

					<md-list-item v-for="(settings, path) in folderSettings.files">
						<md-switch v-model="settings.visible" style="overflow: hidden;">
							{{ path }}
						</md-switch>

						<md-button class="md-icon-button" @click="delete folderSettings.files[path]">
							<md-icon>close</md-icon>
						</md-button>
					</md-list-item>
				</md-list>
			</md-dialog-content>

			<md-dialog-actions>
				<md-button class="md-raised md-primary" @click="applyFolderSettings()">Apply</md-button>
				<md-button @click="showFolderSettingsDialog = false">Close</md-button>
			</md-dialog-actions>
		</md-dialog>

		<appearance-editor
				v-bind:active="appearanceEditorVisible"
				v-bind:active-bot="activeBot"
				v-bind:path="appearancePath"
				v-on:appearance-editor-closed="appearanceEditorVisible = false"
				id="appearance-editor-dialog" />

	</div>

	<div>

		<md-dialog :md-active.sync="showDownloadProgressDialog"
				   :md-close-on-esc="false"
				   :md-click-outside-to-close="false">
			<md-dialog-title>Downloading Bot Pack</md-dialog-title>

			<md-dialog-content>
				<div class="md-layout md-gutter" :class="`md-alignment-center-center`">
					<md-icon class="md-size-4x">cloud_download</md-icon>
				</div>
				<md-progress-bar class="md-accent" md-mode="determinate" :md-value="downloadProgressPercent">
				</md-progress-bar>
				<p>{{ downloadStatus }}</p>
			</md-dialog-content>
		</md-dialog>
	</div>

	</div>

</template>

<script>

	const AppearanceEditor = httpVueLoader('appearance-editor.vue');
	const MutatorField = httpVueLoader('mutator-field.vue');

	const STARTING_BOT_POOL = [
		{'name': 'Human', 'type': 'human', 'image': 'imgs/human.png'},
		{'name': 'Psyonix Allstar', 'type': 'psyonix', 'skill': 1, 'image': 'imgs/psyonix.png'},
		{'name': 'Psyonix Pro', 'type': 'psyonix', 'skill': 0.5, 'image': 'imgs/psyonix.png'},
		{'name': 'Psyonix Rookie', 'type': 'psyonix', 'skill': 0, 'image': 'imgs/psyonix.png'}
	];

	module.exports = {
		name: 'match-setup',
		components: {
			'appearance-editor': AppearanceEditor,
			'mutator-field': MutatorField
		},
		data () {
			return {
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
				appearanceEditorVisible: false,
				appearancePath: ''
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
				let bodyStyle = {backgroundImage: 'url(../imgs/arenas/' + mapName + '.jpg)'};
				this.$emit('background-change', bodyStyle);
			},
			downloadBotPack: function() {
				this.showBotpackUpdateSnackbar = false;
				this.showDownloadProgressDialog = true;
				this.downloadStatus = "Starting"
				this.downloadProgressPercent = 0;
				eel.download_bot_pack()(this.botPackDownloaded);
			},
			showAppearanceEditor: function(looksPath) {
				this.showBotInfo = false;
				this.appearancePath = looksPath;
				this.appearanceEditorVisible = true;
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
				}

				if (language === 'python') {
					this.showProgressSpinner = true;
					eel.begin_python_bot(bot_name)(this.botLoadHandler);
				}

				if (language === 'scratch') {
					this.showProgressSpinner = true;
					eel.begin_scratch_bot(bot_name)(this.botLoadHandler);
				}
			},
			openFolderSettingsDialog: function() {
				eel.get_folder_settings()(this.folderSettingsReceived);
				this.showFolderSettingsDialog = true;
			},
			applyFolderSettings: function() {
				eel.save_folder_settings(this.folderSettings);
				this.botPool = STARTING_BOT_POOL;
				eel.scan_for_bots()(this.botsReceived);
			},
			passesFilter: function(botName) {
				return botName.toLowerCase().includes(this.botNameFilter.toLowerCase());
			},
			botLoadHandler: function (response) {
				this.showNewBotDialog = false;
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

	 		applyLanguageWarnings: function () {
				if (this.languageSupport) {
					this.botPool.forEach((bot) => {
						if (bot.info && bot.info.language) {
							const language = bot.info.language.toLowerCase();
							if (!this.languageSupport.java && language.match(/java|kotlin|scala/)) {
								bot.warn = 'java';
							}
							if (!this.languageSupport.chrome && language.match(/scratch/)) {
								bot.warn = 'chrome';
							}
						}
					});
				}
			},
			matchOptionsReceived: function(matchOptions) {
				this.matchOptions = matchOptions;
			},

			matchSettingsReceived: function (matchSettings) {
				if (matchSettings) {
					this.matchSettings = matchSettings;
					this.updateBGImage(this.matchSettings.map);
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
			},
			botpackUpdateChecked: function (isBotpackUpToDate) {
				this.showBotpackUpdateSnackbar = !isBotpackUpToDate;
			},

			botPackDownloaded: function (response) {
				this.snackbarContent = 'Downloaded Bot Pack!';
				this.showSnackbar = true;
				this.showDownloadProgressDialog = false;
				eel.get_folder_settings()(this.folderSettingsReceived);
				eel.scan_for_bots()(this.botsReceived);
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
		},
		created: function () {
			eel.get_folder_settings()(this.folderSettingsReceived);
			eel.scan_for_bots()(this.botsReceived);
			eel.get_match_options()(this.matchOptionsReceived);
			eel.get_match_settings()(this.matchSettingsReceived);
			eel.get_team_settings()(this.teamSettingsReceived);

			eel.get_language_support()((support) => {
				this.languageSupport = support;
				this.applyLanguageWarnings();
			});

			eel.is_botpack_up_to_date()(this.botpackUpdateChecked);

			const self = this;
			eel.expose(updateDownloadProgress);
			function updateDownloadProgress(progress, status) {
				self.downloadStatus = status;
				self.downloadProgressPercent = progress;
			}
		}
	};

</script>
