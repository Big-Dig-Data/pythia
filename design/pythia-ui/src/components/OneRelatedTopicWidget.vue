<template>
  <div class="related-topics" :class="{ 'px-lg-4': !standalone }">
    <h3 class="font-weight-light" v-text="title"></h3>
    <ExplicitTopicRecommendationsWidget
      :topic-type="topicType"
      :extra-filter="extraFilter"
      :show-ordering-selection="false"
      :drill-down="false"
      :default-min-topic-size="1"
      :default-page-size="5"
      compact-table
      :ignore-global-filters="ignoreGlobalFilters"
    />
  </div>
</template>
<script>
export default {
  name: "OneRelatedTopicWidget",
  components: {
    ExplicitTopicRecommendationsWidget: () =>
      import("./ExplicitTopicRecommendationsWidget.vue"),
  },
  props: {
    extraFilter: {
      required: true,
      type: Object,
    },
    topicType: {
      required: true,
      type: String,
    },
    title: {
      required: true,
      type: String,
    },
    ignoreGlobalFilters: {
      default: false,
      type: Boolean,
    },
    standalone: {
      default: false,
      type: Boolean,
    },
  },
};
</script>

<style scoped lang="scss">
div.related-topics {
  margin-top: 1rem;
  height: 100%;
}
</style>
