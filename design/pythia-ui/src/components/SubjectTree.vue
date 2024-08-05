<i18n src="../locales/common.yaml"></i18n>
<i18n>
en:
  cat_score: Category score / Category score including subcategories
  candidates_count_info: Number of candidates (including candidates from subcategories)
  growth_info: Category growth / Category growth including subcategories
cs:
  cat_score: Skóre kategorie / Skóre kategorie včetně podkategorií
  candidates_count_info: Počet kandidátů (včetně podkategorií)
  growth_info: Růst kategorie / Růst kategorie včetně podkategorií
</i18n>

<template>
  <div>
    <v-text-field
      v-model="search"
      clearable
      :placeholder="$t('search')"
    ></v-text-field>
    <v-card :loading="loading">
      <template slot="progress">
        <v-progress-linear
          color="deep-purple"
          height="10"
          indeterminate
        ></v-progress-linear>
      </template>
      <v-treeview
        v-model="selected"
        :selection-type="selectionType"
        :items="tree"
        :search="search"
        selectable
        dense
        class="overflow"
        :style="`max-height: ${height}`"
      >
        <template v-slot:label="{ item }">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <ExplicitTopicLink
                v-if="withLinks"
                topic-type="psh"
                :topic-id="item.id"
              >
                <span v-bind="attrs" v-on="on">{{ item.name }}</span>
              </ExplicitTopicLink>
              <span v-else v-bind="attrs" v-on="on">{{ item.name }}</span>
            </template>
            <span>{{ item.name }}</span>
          </v-tooltip>
        </template>
        <template v-slot:append="{ item }">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span v-if="score_type == 'score'">
                <span v-if="item.acc_score != 0" v-bind="attrs" v-on="on">
                  {{ formatInteger(item.score) }} /
                  {{ formatInteger(item.acc_score) }}
                </span>
              </span>
              <span v-else-if="score_type == 'candidates_count'">
                <span v-bind="attrs" v-on="on">
                  {{ formatInteger(item.acc_score) }}
                </span>
              </span>
              <span v-else>
                <span v-bind="attrs" v-on="on">
                  <span
                    :class="`${
                      item.absolute_growth > 0 ? 'green' : 'red'
                    }--text text-caption`"
                  >
                    {{ formatRelGrowth(item.relative_growth) }}
                  </span>
                  /
                  <span
                    :class="`${
                      item.acc_absolute_growth > 0 ? 'green' : 'red'
                    }--text text-caption`"
                  >
                    {{ formatRelGrowth(item.acc_relative_growth) }}
                  </span>
                </span>
              </span>
            </template>
            <span class="d-flex flex-column">
              <span v-if="score_type == 'growth'">
                {{ formatRelGrowth(item.relative_growth) }} ({{
                  item.score_yr_b4
                }}
                -> {{ item.score_past_yr }}) /
                {{ formatRelGrowth(item.acc_relative_growth) }} ({{
                  item.acc_score_yr_b4
                }}
                -> {{ item.acc_score_past_yr }})
              </span>
              {{ tooltipMap[score_type] }}
            </span>
          </v-tooltip>
        </template>
      </v-treeview>
    </v-card>
  </div>
</template>

<script>
import axios from "axios";
import cloneDeep from "lodash/cloneDeep";
import numeral from "numeral";
import { mapActions, mapGetters } from "vuex";
import { formatInteger } from "../libs/numbers";
import ExplicitTopicLink from "./ExplicitTopicLink";
import isEqual from "lodash/isEqual";

export default {
  name: "SubjectTree",
  components: { ExplicitTopicLink },
  props: {
    value: { required: true, type: Array },
    parent_uid: { default: "THEMA-ROOT", type: String },
    height: { default: "auto", type: String },
    withLinks: { default: false, type: Boolean },
    score_type: { default: "score", type: String },
    candidate_count_filters: { default: () => {}, type: Object },
  },
  data() {
    return {
      loading: false,
      tree: [],
      selected: cloneDeep(this.value),
      search: "",
      justFetchingUrl: null,
      justFetchingParams: null,
      tooltipMap: {
        score: this.$t("cat_score"),
        candidates_count: this.$t("candidates_count_info"),
        growth: this.$t("growth_info"),
      },
      selectionType: "mode that works best",
    };
  },
  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
    }),
    dataUrl() {
      if (!this.worksetUUID) return null;
      return `/api/bookrank/workset/${this.worksetUUID}/subjects/${this.parent_uid}/`;
    },
    urlParams() {
      return {
        score_type: this.score_type,
        candidate_count_filters: this.candidate_count_filters,
      };
    },
  },

  created() {
    this.fetchData();
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    formatInteger,
    async fetchData() {
      if (!this.dataUrl) return null;
      this.loading = true;
      this.justFetchingUrl = this.dataUrl;
      this.justFetchingParams = cloneDeep(this.urlParams);
      try {
        const response = await axios.get(this.dataUrl, {
          params: this.urlParams,
        });
        this.selectionType = "independent";
        this.tree = response.data.tree;
        this.$emit("ready", true);
        this.$nextTick(() => {
          this.selectionType = "whatever";
        });
      } catch (error) {
        this.showSnackbar({
          content: "Error fetching data: " + error,
          color: "error",
        });
      } finally {
        this.loading = false;
      }
    },

    formatRelGrowth(val) {
      if (!val) return "-";
      return numeral(val).format("+0,0%").replace(/,/g, "\xa0");
    },
  },

  watch: {
    dataUrl(newUrl) {
      if (newUrl !== this.justFetchingUrl) this.fetchData();
    },
    urlParams: {
      handler() {
        if (!isEqual(this.justFetchingParams, this.urlParams)) {
          this.fetchData();
        }
      },
      deep: true,
    },
    selected() {
      this.$emit("input", this.selected);
    },
    value() {
      if (!isEqual(this.selected, this.value))
        this.selected = cloneDeep(this.value);
    },
  },
};
</script>

<style scoped>
.overflow {
  overflow: auto;
}
</style>
