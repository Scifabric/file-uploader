<template>
    <div>
        <h1>Upload pictures to PYBOSSA</h1>
        <dropzone id="myVueDropzone" url="/upload" acceptedFileTypes='image/*' maxFileSizeInMB=10 maxNumberOfFiles=1000></dropzone>
    </div>
</template>
<script>
import Dropzone from 'vue2-dropzone'
export default {
    data(){
        return {foo: 1}
    },
    components: {Dropzone},
}
</script>
