<template>
  <div class="bar">
    <div
      class="barbar"
      :style="{ width: percentage, backgroundColor: color }"
      v-if="ratio > 0.5"
    >
      <span class="barnum">{{ formatted_number }}</span>
    </div>
    <div v-else>
      <span class="barnum">{{ formatted_number }}</span>
      <div
        class="barbar"
        :style="{ width: percentage, backgroundColor: color }"
      ></div>
    </div>
  </div>
</template>
<script>
export default {
  name: "SizeBar",
  props: {
    number: {
      required: true,
      type: Number,
    },
    decimals: {
      required: false,
      default: 1,
      type: Number,
    },
    max_value: {
      required: true,
      type: Number,
    },
    color: {
      default: "#375694",
    },
  },
  computed: {
    ratio() {
      return this.number / this.max_value;
    },
    percentage() {
      return (100 * this.ratio).toFixed(0) + "%";
    },
    formatted_number() {
      return this.number.toFixed(this.decimals);
    },
  },
};
</script>

<style lang="scss">
div.bar {
  div.barbar {
    float: right;
    background-color: #375694;
    height: 1.5rem;
    span.barnum {
      color: white;
    }
  }
  span.barnum {
    margin-right: 0.125rem;
    font-size: 0.875rem;
  }
}

.highlight {
  div.bar div.barbar {
    background-color: #993333;
  }
}
</style>
