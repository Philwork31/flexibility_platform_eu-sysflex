<template>
    <div class="content">
        <list-activation-requests-data>
        </list-activation-requests-data>
    </div>
</template>

<script>
import ListActivationRequestsData from "../DataList/ListActivationRequestsData.vue";

export default {
    components: {
        'list-activation-requests-data': ListActivationRequestsData
    }
};
</script>
