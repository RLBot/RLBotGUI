eel.expose(PythonPrint);
function PythonPrint(message) {
    console.log("Python: "+message);
}

// looks like if you want to expose a function inside a vue component,
// you first have to expose it's signature like this
eel.expose(updateDownloadProgress);
function updateDownloadProgress(progress, status) {}
// otherwise python will think it doesn't exist
// you can then expose the actual function later

Vue.use(VueMaterial.default);

const STARTING_BOT_POOL = [
    {'name': 'Psyonix Allstar', 'type': 'psyonix', 'skill': 1, 'image': 'imgs/psyonix.png'},
    {'name': 'Psyonix Pro', 'type': 'psyonix', 'skill': 0.5, 'image': 'imgs/psyonix.png'},
    {'name': 'Psyonix Rookie', 'type': 'psyonix', 'skill': 0, 'image': 'imgs/psyonix.png'}
];

const Main = httpVueLoader('main.vue');
const Sandbox = httpVueLoader('sandbox.vue');
const routes = [
    { path: '/', component: Main },
    { path: '/sandbox', component: Sandbox },
];

const router = new VueRouter({
    routes: routes
});

const app = new Vue({
    router: router,
    el: '#app',
    data: {
        bodyStyle: null
    },
    methods: {
        changeBackgroundImage: function(bodyStyle) {
            this.bodyStyle = bodyStyle;
        }
    }
});

router.replace('/');
