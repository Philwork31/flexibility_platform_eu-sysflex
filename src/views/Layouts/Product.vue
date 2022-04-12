<template>
    <div class="content">
        <list-product-data>
        </list-product-data>
    </div>
</template>

<script>
import ListProductData from "../DataList/ListProductData.vue";

export default {
    components: {
        'list-product-data': ListProductData
    }
};
</script>
