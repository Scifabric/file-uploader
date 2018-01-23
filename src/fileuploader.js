import Vue from 'vue'
import VueFormGenerator from 'vue-form-generator'
import FileUploader from './components/fileuploader.vue'
import Buefy from 'buefy'
import 'buefy/lib/buefy.css'
import VueSocketio from 'vue-socket.io'

Vue.use(VueFormGenerator)
Vue.use(Buefy)
Vue.use(VueSocketio, `http://${document.domain}:${location.port}`)

new Vue({
    el: '#fileuploader',
    components: {FileUploader}
});

