export default {
	name: 'launcher-preference',
	props: ['modalId'],
	template: `
	<div>
		<div>
			<b-form-group>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="steam">Steam</b-form-radio>
				<b-form-radio v-model="launcherSettings.preferred_launcher" name="launcher-radios" value="epic">Epic Games</b-form-radio>
				<b-form-checkbox
					class="ml-4"
					v-model="launcherSettings.use_login_tricks" 
					:disabled="launcherSettings.preferred_launcher !== 'epic'">
				
					Get My Items/Settings <b-icon class="warning-icon" icon="exclamation-triangle-fill" v-b-tooltip.hover 
					title="If you choose this, we'll do some fancy things to make sure your Epic account logs in successfully and loads your car + camera settings. 
					It might look slightly weird on the Epic login server but they probably won't care."></b-icon>
				</b-form-checkbox>
			</b-form-group>
		</div>
		<b-button variant="primary" class="mt-3" @click="saveLauncherSettings()">Save</b-button>
	</div>
	`,
	data () {
		return {
			launcherSettings: { preferred_launcher: 'epic', use_login_tricks: false },
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
	watch: {
		'launcherSettings.preferred_launcher': function(newVal) {
			if (newVal === 'steam') {
				this.launcherSettings.use_login_tricks = false;
			}
		}
	},
}
