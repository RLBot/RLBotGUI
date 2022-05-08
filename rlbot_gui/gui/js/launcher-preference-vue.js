export default {
	name: 'launcher-preference',
	props: ['modalId'],
	template: `
	<div>
		<div>
			<b-form-group>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="epic">Try All</b-form-radio>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="steam">Steam</b-form-radio>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="epic_only">Epic Games</b-form-radio>
			</b-form-group>
			<b-form-group 
				label="Optional: Path to RocketLeague.exe for Epic Launcher" 
				description="Only needed if it's not working automatically, only used by Epic launcher.">
				<b-form-input
					v-model="launcherSettings.rocket_league_exe_path"
					trim
					placeholder="C:\\Path\\To\\Your\\RocketLeague.exe"
					:disabled="launcherSettings.preferred_launcher == 'steam'">
				</b-form-input>
			</b-form-group>
		</div>
		<b-button variant="primary" class="mt-3" @click="saveLauncherSettings()">Save</b-button>
	</div>
	`,
	data () {
		return {
			launcherSettings: { preferred_launcher: 'epic', use_login_tricks: true },
		}
	},

	methods: {
		launcherSettingsReceived: function (launcherSettings) {
			if (launcherSettings) {
				Object.assign(this.launcherSettings, launcherSettings);
			}
		},
		saveLauncherSettings: function () {
			eel.save_launcher_settings(this.launcherSettings);
			this.$bvModal.hide(this.modalId);
		},
	},
	created: function () {
		eel.get_launcher_settings()(this.launcherSettingsReceived);
	},
}
