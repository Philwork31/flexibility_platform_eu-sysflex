<template>
    <div class="content">
        <list-products-to-validate-data>
        </list-products-to-validate-data>
    </div>
</template>

<script>
import ListProductsToValidateData from "../DataList/ListProductsToValidateData.vue";

export default {
    components: {
        'list-products-to-validate-data': ListProductsToValidateData
    }
};
</script>
