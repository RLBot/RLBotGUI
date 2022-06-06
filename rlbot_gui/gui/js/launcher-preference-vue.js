export default {
	name: 'launcher-preference',
	props: ['modalId'],
	template: `
	<div>
		<div>
			<b-form-group>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="epic">Try both</b-form-radio>
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
					:state="exePathState"
					:disabled="launcherSettings.preferred_launcher == 'steam'">
				</b-form-input>
				<b-form-invalid-feedback>
					This needs to be the full path, ending with <b>RocketLeague.exe</b>
					<div v-if="correctedExePath">
						Did you mean:<br>
						<div style="overflow-x: auto; white-space: nowrap;">
							<b>{{ correctedExePath }}</b>
						</div>
						<b-button @click="launcherSettings.rocket_league_exe_path = correctedExePath" size="sm" variant="danger">Yes, paste that in</b-button>
					</div>
				</b-form-invalid-feedback>
			</b-form-group>
		</div>
		<b-button variant="primary" class="mt-3" @click="saveLauncherSettings()" :disabled="exePathState === false">Save</b-button>
	</div>
	`,
	data () {
		return {
			launcherSettings: {
				preferred_launcher: 'epic',
				use_login_tricks: true,
				rocket_league_exe_path: '',
			},
		}
	},
	computed: {
		exePathState: function() {
			if (this.launcherSettings.preferred_launcher == 'steam' || this.launcherSettings.rocket_league_exe_path === '') return null;
			return this.launcherSettings.rocket_league_exe_path.endsWith("RocketLeague.exe");
		},
		correctedExePath: function() {
			let path = this.launcherSettings.rocket_league_exe_path;
			if (path.endsWith("rocketleague")) {
				path += "\\Binaries";
			}
			if (path.endsWith("Binaries")) {
				path += "\\Win64";
			}
			if (path.endsWith("Win64")) {
				path += "\\RocketLeague.exe";
				return path;
			}
			return null;
		},
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
