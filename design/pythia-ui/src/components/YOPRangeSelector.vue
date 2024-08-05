<i18n>
en:
    start_yop: From
    end_yop: To
    unset: Unlimited
cs:
    start_yop: Od
    end_yop: Do
    unset: Neomezeno
</i18n>

<template>
  <v-container class="my-0 py-0">
    <v-row class="my-0 py-0">
      <v-col cols="auto" class="my-0 py-0 pl-0">
        <v-text-field
          v-model="startYOP"
          type="number"
          :label="$t('start_yop')"
          :placeholder="$t('unset')"
        ></v-text-field>
      </v-col>
      <v-col cols="auto" class="my-0 py-0">
        <v-text-field
          v-model="endYOP"
          type="number"
          :label="$t('end_yop')"
          :placeholder="$t('unset')"
        ></v-text-field>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapGetters, mapState } from "vuex";
import debounce from "lodash/debounce";

export default {
  name: "YOPRangeSelector",

  data() {
    return {};
  },

  computed: {
    ...mapState({
      startYOPStore: (state) => state.YOP.startYOP,
      endYOPStore: (state) => state.YOP.endYOP,
    }),
    startYOP: {
      get() {
        return this.startYOPStore;
      },
      set: debounce(function (value) {
        this.changeYOP({ start: value });
      }, 500),
    },
    endYOP: {
      get() {
        return this.endYOPStore;
      },
      set: debounce(function (value) {
        this.changeYOP({ end: value });
      }, 500),
    },
  },

  methods: {
    ...mapActions({
      changeYOP: "changeYOP",
    }),
  },
};
</script>

<style scoped></style>
