<template>
    <div class="content">
        <list-bids-data>
        </list-bids-data>
    </div>
</template>

<script>
import ListBidsData from "../DataList/ListBidsData.vue";

export default {
    components: {
        'list-bids-data': ListBidsData
    }
};
</script>