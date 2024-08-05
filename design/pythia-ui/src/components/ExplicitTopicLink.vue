<template>
  <router-link :to="to">
    <slot></slot>
  </router-link>
</template>

<script>
import { topicTypeToQueryParam } from "../libs/api";

export default {
  name: "ExplicitTopicLink",

  props: {
    topicType: {
      required: true,
      type: String,
      validator: (value) => value in topicTypeToQueryParam,
    },
    topicId: {
      required: true,
      type: Number,
    },
  },

  computed: {
    to() {
      return {
        name: `${this.topicType} detail`,
        params: { topicId: this.topicId },
      };
    },
  },
};
</script>

<style scoped></style>
