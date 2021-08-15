export default {
	name: 'launcher-preference',
	props: ['modalId'],
	template: `
	<div>
		<div>
			<b-form-group>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="steam">Steam</b-form-radio>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="epic">Epic Games</b-form-radio>
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
