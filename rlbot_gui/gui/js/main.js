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

const Main = httpVueLoader('main.vue');
const routes = [
    { path: '/', component: Main },
];

const router = new VueRouter({
    routes: routes
});

const app = new Vue({
    router: router,
    el: '#app',
    data: {
    }
});

router.replace('/');
