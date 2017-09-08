<template>
    <div>
        <h1>Upload pictures to PYBOSSA</h1>
        <dropzone id="myVueDropzone" url="/upload" acceptedFileTypes='image/*' maxFileSizeInMB=10 maxNumberOfFiles=1000>
            <input type="hidden" v-model="project">
        </dropzone>
    </div>
</template>
<script>
import Dropzone from 'vue2-dropzone'
import axios from 'axios'
export default {
    data(){
        return {projects: []}
    },
    components: {Dropzone},
    created(){
        var url = '/projects'
        var self = this
        axios.get(url)
            .then(response => {
                self.projects = response.data
            })
            .catch(error => {console.log(error)})
    }
}
</script>
