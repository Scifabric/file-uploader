import Vue from 'vue'
import VueFormGenerator from 'vue-form-generator'
import FileUploader from './components/fileuploader.vue'
import Buefy from 'buefy'
import 'buefy/lib/buefy.css'

Vue.use(VueFormGenerator)
Vue.use(Buefy)

new Vue({
    el: '#fileuploader',
    components: {FileUploader}
});

