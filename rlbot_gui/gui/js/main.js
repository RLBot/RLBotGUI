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

// Vue.use(VueMaterial.default);

import Main from './main-vue.js'
import Sandbox from './sandbox-vue.js'
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
