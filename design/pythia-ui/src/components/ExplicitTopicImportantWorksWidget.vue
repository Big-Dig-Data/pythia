<i18n src="../locales/common.yaml"></i18n>

<template>
  <v-lazy min-height="320" transition="fade-transition">
    <v-data-table
      :headers="headers"
      :items="rows"
      :loading="rowsLoading"
      sort-desc
      :items-per-page.sync="tablePageSize"
      :page.sync="tablePage"
      :footer-props="{
        'items-per-page-text': $t('table.rows_per_page'),
        'items-per-page-options': $numRowsOpts,
      }"
      :server-items-length="totalItems"
      dense
    >
      <template v-slot:item.name="{ item }">
        <router-link :to="{ name: 'work detail', params: { workId: item.pk } }">
          {{ item.name }}
        </router-link>
      </template>

      <template v-slot:item.score="{ item }">
        {{ formatInteger(item.score) }}
      </template>
      <template v-slot:pageText="props">
        {{ $t("table.row_counter", props) }}
      </template>
    </v-data-table>
  </v-lazy>
</template>

<script>
import axios from "axios";
import { mapActions, mapGetters } from "vuex";
import { stringify } from "query-string";
import { formatInteger } from "../libs/numbers";
import { topicTypeToQueryParam } from "../libs/api";

export default {
  name: "ExplicitTopicImportantWorksWidget",
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
    defaultPageSize: {
      required: false,
      type: Number,
      default: 10,
    },
  },

  data() {
    return {
      rows: [],
      orderBy: "score",
      tablePage: 1,
      tablePageSize: this.defaultPageSize,
      rowsLoading: false,
      totalItems: null,
      numberFormat: {
        notation: "fixed",
        precision: 1,
      },
    };
  },

  computed: {
    ...mapGetters({
      worksetUUID: "selectedWorksetUUID",
      queryParams: "workQueryParams",
    }),

    headers() {
      return [
        {
          text: this.$i18n.t("columns.title"),
          value: "name",
          sortable: false,
        },
        {
          text: this.$i18n.t("columns.score"),
          value: "score",
          align: "right",
          sortable: false,
        },
      ];
    },
    dataUrl() {
      if (this.worksetUUID) {
        let params = {
          ...this.queryParams,
          page_size: this.tablePageSize,
          page: this.tablePage,
          order_by: this.orderBy,
          filter_type: topicTypeToQueryParam[this.topicType],
          filter_value: this.topicId,
        };
        return `/api/hits/workhit/works/${this.worksetUUID}/${
          this.topicType
        }?${stringify(params)}`;
      } else return null;
    },
  },

  methods: {
    ...mapActions({
      showSnackbar: "showSnackbar",
    }),
    formatInteger,
    async fetchData() {
      if (this.dataUrl) {
        this.rowsLoading = true;
        try {
          const response = await axios.get(this.dataUrl);
          this.rows = response.data.results;
          this.totalItems = response.data.count;
        } catch (error) {
          this.showSnackbar({
            content: "Error fetching work data: " + error,
            color: "error",
          });
        } finally {
          this.rowsLoading = false;
        }
      }
    },
  },
  watch: {
    dataUrl() {
      this.fetchData();
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>
